'''
The circuit remapper logic.
'''
from qiskit.circuit import QuantumCircuit
from qiskit import transpile, assemble, Aer, IBMQ
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from sympy import Matrix
import matplotlib.pyplot as plt
from qiskit.circuit.instruction import Instruction
from qiskit.circuit.quantumcircuitdata import QuantumCircuitData, CircuitInstruction
from qiskit.circuit.classicalregister import ClassicalRegister, Clbit
from qiskit.circuit.quantumregister import QuantumRegister, Qubit
from qiskit.circuit.library.standard_gates.h import *
import qiskit
import numpy as np

from typing import (
    Union,
    Optional,
    List,
    Dict,
    Tuple,
    Type,
    TypeVar,
    Sequence,
    Callable,
    Mapping,
    Set,
    Iterable,
)


class CircuitRemapper:
    '''
    The circuit remapper class for remapping a ciruit to a topology.
    '''
    def __init__(self, circuit, topology):
        self.circuit = circuit
        self.topology = topology

    def remap_circuit(self):
        '''
        Remap the circuit for the topology.
        '''
        return None

    def _circuit_to_layers(       
        self,
        filter_function: Optional[callable] = lambda x: not getattr(
            x.operation, "_directive", False
        ),
    ) -> int: 
        '''Given a Qiskit circuit, return an array of the layers of that circuit'''        
        # Assign each bit in the circuit a unique integer
        # to index into op_stack.
        circ = self.circuit
        bit_indices = {bit: idx for idx, bit in enumerate(circ.qubits + circ.clbits)}

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
                considered = False
                for ind, reg in enumerate(instruction.qubits + instruction.clbits):
                    # Add to the stacks of the qubits and
                    # cbits used in the gate.
                    reg_ints.append(bit_indices[reg])
                    if filter_function(instruction):
                        levels.append(op_stack[reg_ints[ind]] + 1)
                        if len(layers) < (op_stack[reg_ints[ind]] + 1):
                            layers.append([])
                        if not considered:
                            layers[op_stack[reg_ints[ind]]].append(instruction)
                            considered = True
                    else:
                        levels.append(op_stack[reg_ints[ind]])
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

    # @staticmethod
    def _layer_to_circuit(self, layers: Iterable[List],*, qubits: Iterable[Qubit] = (),
    clbits: Iterable[Clbit] = (),
    name: Optional[str] = None,
    global_phase = 0,
    metadata: Optional[dict] = None,) -> "QuantumCircuit":
        """Return a circuit from a list of layers.

        Args:
            layers: A list of layers, where each layer is a list of
                :class:`~qiskit.circuit.Instruction`
        """
        circuit = QuantumCircuit(name=name, global_phase=global_phase, metadata=metadata)
        added_qubits = set()
        added_clbits = set()
        if qubits:
            qubits = list(qubits)
            circuit.add_bits(qubits)
            added_qubits.update(qubits)
        if clbits:
            clbits = list(clbits)
            circuit.add_bits(clbits)
            added_clbits.update(clbits)
        for layer in layers:
            for instruction in layer:
    #             print(instruction)
                if not isinstance(instruction, CircuitInstruction):
                    instruction = CircuitInstruction(*instruction)
                qubits = [qubit for qubit in instruction.qubits if qubit not in added_qubits]
                clbits = [clbit for clbit in instruction.clbits if clbit not in added_clbits]
                circuit.add_bits(qubits)
                circuit.add_bits(clbits)
                added_qubits.update(qubits)
                added_clbits.update(clbits)
                circuit._append(instruction)
        self.circuit = circuit

        return None


