"""The circuit remapper logic."""
from typing import (
    Optional,
    List,
    Iterable,
)
import time
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.quantumcircuitdata import CircuitInstruction
from qiskit.circuit.quantumregister import Qubit
from qiskit.circuit.classicalregister import ClassicalRegister, Clbit
from qiskit.circuit.exceptions import CircuitError
from qiskit import transpile
from .components import Layer, Topology


class CircuitRemapper:
    """
    The circuit remapper class for remapping a ciruit to a topology.
    """

    def __init__(self, topology: Topology):
        self.topology = topology

    @staticmethod
    def _circuit_to_layers(
            circuit: QuantumCircuit,
            filter_function: Optional[callable] = lambda x: not getattr(
                x.operation, "_directive", False
            ),
    ) -> "list[list]":
        """Given a Qiskit circuit, return an array of the layers of that circuit"""
        # Assign each bit in the circuit a unique integer
        # to index into op_stack.
        circ = circuit
        bit_indices = {bit: idx for idx,
        bit in enumerate(circ.qubits + circ.clbits)}

        # If no bits, return 0
        if not bit_indices:
            return 0

        # A list that holds the height of each qubit
        # and classical bit.
        op_stack = [0] * len(bit_indices)
        layers = []
        for instruction in circ.data:
            levels = []
            reg_ints = []
            max_pos = 0

            for ind, reg in enumerate(instruction.qubits + instruction.clbits):
                # Add to the stacks of the qubits and
                # cbits used in the gate.
                reg_ints.append(bit_indices[reg])
                if filter_function(instruction):
                    levels.append(op_stack[reg_ints[ind]] + 1)
                    if len(layers) < (op_stack[reg_ints[ind]] + 1):
                        layers.append([])
                    max_pos = max(max_pos, (op_stack[reg_ints[ind]]))
                else:
                    levels.append(op_stack[reg_ints[ind]])

            layers[max_pos].append(instruction)
            # Assuming here that there is no conditional
            # snapshots or barriers ever.
            if getattr(instruction.operation, "condition", None):
                # Controls operate over all bits of a classical register
                # or over a single bit
                if isinstance(instruction.operation.condition[0], Clbit):
                    condition_bits = [instruction.operation.condition[0]]
                else:
                    condition_bits = instruction.operation.condition[0]
                for cbit in condition_bits:
                    idx = bit_indices[cbit]
                    if idx not in reg_ints:
                        reg_ints.append(idx)
                        levels.append(op_stack[idx] + 1)
            max_level = max(levels)
            for ind in reg_ints:
                op_stack[ind] = max_level

        assert max(op_stack) == len(layers)
        return layers

    @staticmethod
    def _layer_to_circuit(layers: Iterable[List], qubits: Iterable[Qubit] = (),
                          clbits: Iterable[Clbit] = (),
                          name: Optional[str] = None,
                          global_phase=0,
                          metadata: Optional[dict] = None, ) -> "QuantumCircuit":
        """Return a circuit from a list of layers.

        Args:
            layers: A list of layers, where each layer is a list of
                :class:`~qiskit.circuit.Instruction`
        return: A circuit from the layers.
        """
        circuit = QuantumCircuit(
            name=name, global_phase=global_phase, metadata=metadata)
        added_qubits = set()
        added_clbits = set()
        added_qregs = set()
        added_cregs = set()

        if qubits:
            qubits = list(qubits)
            circuit.add_bits(qubits)
            added_qubits.update(qubits)
            added_qregs.update(qubit.register for qubit in qubits)
            circuit.add_register(*added_qregs)

        if clbits:
            clbits = list(clbits)
            circuit.add_bits(clbits)
            added_clbits.update(clbits)
            added_cregs.update(clbit.register for clbit in clbits)
            circuit.add_register(*added_cregs)

        for layer in layers:
            for instruction in layer:
                if not isinstance(instruction, CircuitInstruction):
                    instruction = CircuitInstruction(*instruction)
                qubits = [qubit for qubit in instruction.qubits if
                          qubit not in added_qubits and qubit.register not in added_qregs]
                clbits = [clbit for clbit in instruction.clbits if
                          clbit not in added_clbits and clbit.register not in added_cregs]
                qregs = [qubit.register for qubit in qubits]
                cregs = [clbit.register for clbit in clbits]
                circuit.add_bits(qubits)
                circuit.add_bits(clbits)
                circuit.add_register(*qregs)
                circuit.add_register(*cregs)
                added_qubits.update(qubits)
                added_clbits.update(clbits)
                added_qregs.update(qregs)
                added_cregs.update(cregs)
                circuit.append(instruction)
        return circuit

    @staticmethod
    def _replace_nonlocal_control(operation: CircuitInstruction,
                                  topology: Topology,
                                  deeper_ops: List[CircuitInstruction] = None):
        """
        Replace the non-local control gates with Cat entanglement gates for a given layer.
        Args:
            operation: a non-local control gate
            topology: The network topology.
            deeper_ops: The list of operations.
        Returns:
            (list): List of new operations to be added in the layer
        """

        control_qubit = operation.qubits[0]
        target_qubit = operation.qubits[1]
        control_host = topology.get_host(control_qubit)
        target_host = topology.get_host(target_qubit)
        ent_inst = operation.copy()
        epr_control = topology.get_epr_id(control_host)
        epr_target = topology.get_epr_id(target_host)

        epr_qubits = [epr_control, epr_target]
        opr_qubits = [control_qubit, target_qubit]
        if len(deeper_ops) > 0:
            for opi in deeper_ops:
                opr_qubits.append(opi.qubits[1])

        measure_bits = ClassicalRegister(2, "cat_measure")
        circ = QuantumCircuit(epr_qubits, opr_qubits, measure_bits)
        # print(deeper_ops)
        # Generate EPR pair
        circ.h(0)
        circ.cx(0, 1)

        # cat entanglement
        circ.cx(2, 0)
        circ.measure(0, 0)
        circ.x(1).c_if(measure_bits[0], 1)

        ent_inst.qubits = [epr_qubits[1], opr_qubits[1]]
        circ.data.append(ent_inst)
        if len(deeper_ops) > 0:
            ident = 2
            for opi in deeper_ops:
                ent_inst = opi.copy()
                ent_inst.qubits = [epr_qubits[1], opr_qubits[ident]]
                circ.data.append(ent_inst)
                ident += 1

        circ.h(1)
        circ.measure(1, 1)
        circ.z(2).c_if(measure_bits[1], 1)

        circ.reset(epr_qubits)

        # Make layers from this circuit
        new_ops = []
        for opi in circ.data:
            new_ops.append([opi])

        return new_ops

    def remap_circuit(self, circuit: QuantumCircuit, decompose: bool = None,
                      decompose_list: List[str] = None):
        """
        Remap the circuit for the topology.
        Returns: a distributed circuit over the topology
        Args:
            circuit: The circuit to be distributed.
        Returns:
            A distributed circuit over the topology.
        """

        if decompose is not None:
            if decompose_list is not None:
                circuit, _ = self._decompose_ready(circuit, decompose_list)
            else:
                circuit, _ = self._decompose_ready(circuit)
        else:
            _, incompatible = self._decompose_ready(
                circuit, do_decompose=False)
            if incompatible:
                raise CircuitError(
                    "The circuit contains incompatible gates, Please try decompose=True keyword argument.")

        layers = self._circuit_to_layers(circuit=circuit)
        qubits = circuit.qubits
        clbits = circuit.clbits
        distributed_layers = []
        idx = 0
        circ_qubits = self.topology.qubits
        deep_dict = {qubit: 0 for qubit in circ_qubits}

        for a_layer in layers:
            layer_now = Layer(a_layer, self.topology)
            non_local_ops = layer_now.non_local_operations()
            new_layers = [[]]

            if non_local_ops not in [[], None]:
                for operation in non_local_ops:
                    control, target = operation.qubits[0], operation.qubits[1]
                    if deep_dict[control] > 0:
                        deep_dict[control] -= 1
                        continue
                    deeper_ops = self._get_deeper_nlcontrol(
                        layers[idx + 1:], control, target)
                    # deeper_ops = []
                    if len(deeper_ops) > 0:
                        deep_dict[control] += len(deeper_ops)
                    op_replaced = self._replace_nonlocal_control(
                        operation, self.topology, deeper_ops)
                    new_layers.extend(op_replaced)

            local_ops = []
            for operation in a_layer:
                if operation not in non_local_ops:
                    local_ops.append(operation)

            new_layers[0].extend(local_ops)

            distributed_layers.extend(new_layers)
            idx += 1

        dist_circ = self._layer_to_circuit(distributed_layers, qubits, clbits)

        return dist_circ

    @staticmethod
    def _qubit_ops(layers: List[Layer], qubit: Qubit = None):
        """
        Get the operations on each qubit
        Args:
            layers: The list of layers.
            qubit: The qubit to get the operations for.
        Returns: dictionary of qubit to operations
        """
        qubit_ops = []
        for layer in layers:
            for opi in layer:
                for a_qubit in opi.qubits:
                    if qubit == a_qubit:
                        qubit_ops.append(opi)
        return qubit_ops

    def _get_deeper_nlcontrol(self, layers, control_qubit: Qubit, target_qubit: Qubit):
        """
        Get the deeper control operation on a qubit.
        """
        control_ops = self._qubit_ops(layers, control_qubit)
        target_host = self.topology.get_host(target_qubit)
        ops = []
        track_dict = {
            qubit: 0 for qubit in self.topology.get_qubits(target_host)}
        for opi in control_ops:
            if len(opi.qubits) == 2 and opi.qubits[0] == control_qubit:
                if self.topology.get_host(opi.qubits[1]) == target_host:
                    target_ops = self._qubit_ops(layers, opi.qubits[1])
                    # print('here')
                    if target_ops[track_dict[opi.qubits[1]]] == opi:
                        ops.append(opi)
                        track_dict[opi.qubits[1]] += 1
                else:
                    break
            else:
                break

        return ops

    @staticmethod
    def collate_measurements(sim_results: dict, num_qubits: int):
        """
        Collate the measurements from the simulation results.
        Args:
            sim_results: simulation results from the simulator
            num_qubits: number of qubits in the circuit
        Returns: A dictionary of measurements
        """
        sim_dict = {}
        for key in sim_results.keys():
            new_key = key[0:num_qubits]
            dict_keys = sim_dict.keys()
            if new_key not in dict_keys:
                sim_dict[new_key] = sim_results[key]
            else:
                sim_dict[new_key] += sim_results[key]

        return sim_dict

    @staticmethod
    def do_measure_ready(circ: QuantumCircuit, topology: Topology):
        """
        Make the circuit is ready for measurement.
        Args:
            circ: the circuit to measure.
            topology: The network topology.
        Returns: Circuit ready for measurement
        """
        n_q = topology.num_qubits()
        all_qubits = topology.get_all_qubits()
        measure_bits = ClassicalRegister(n_q, "measure")
        circ.add_register(measure_bits)
        circ.measure(all_qubits, measure_bits)

    @staticmethod
    def _decompose_ready(circ: QuantumCircuit, list_of_gates: List[str] = None,
                         do_decompose: bool = True):
        """
        Decompose the circuit into basic gates(1 and 2 qubit gates).
        Args:
            circ: the circuit to decompose.
            topology: The network topology.
        Returns: Decomposed circuit
        """
        timeout = time.time() + 60  # 1 minute from now

        num_large_gates = 1
        circ_copy = circ.copy()
        incompatible_gate_present = False
        if list_of_gates is None:
            list_of_gates = []
        while num_large_gates > 0:
            num_large_gates = 0
            for gate in circ_copy.data:
                if len(gate[1]) > 2:
                    num_large_gates += 1
                    incompatible_gate_present = True
                    if do_decompose is False:
                        break
                    circ_copy = circ_copy.decompose(gate[0].name)
                elif gate[0].name == 'swap':
                    num_large_gates += 1
                    incompatible_gate_present = True
                    if do_decompose is False:
                        break
                    circ_copy = circ_copy.decompose(gate)
                elif gate[0].name in list_of_gates:
                    num_large_gates += 1
                    circ_copy = circ_copy.decompose(gate)
                if time.time() > timeout:
                    break
            if do_decompose is False and num_large_gates > 0:
                break
            if do_decompose is True and time.time() > timeout:
                print("Single level decomposition cutoff of 1 minute reached.",
                      "Performing transpilation with basis gates: cx, u1, u2, u3, id")
                circ_copy = transpile(circ_copy, basis_gates=[
                    'cx', 'u1', 'u2', 'u3', 'id'])
                break

        return circ_copy, incompatible_gate_present
