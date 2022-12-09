from typing import List, Optional
from qiskit.circuit.quantumcircuitdata import CircuitInstruction
from .topology import Topology
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.quantumregister import QuantumRegister, Qubit
from qiskit.circuit.classicalregister import ClassicalRegister, Clbit
class Layer(object):
    """
    Layer object which is a collection of operations to be applied on the qubits in the system.
    """

    def __init__(self, operations: Optional[List[CircuitInstruction]] = None, topology:Topology=None):
        """
        Returns the important things for a layer in a quantum circuit
        Args:
            operations (list): List of Operation objects, which contains information
               about the operation to be performed on the quantum circuit
        """

        self._operations = operations if operations is not None else []
        self._topology = topology

    def __str__(self):
        layer = ""

        for o in self._operations:
            layer += f"-{o}-|\n"

        return layer

    @property
    def operations(self):
        """
        Get the *operations* in the layer
        Returns:
            (list): List of Operation objects, which contains information about the operation to
                    be performed on the quantum circuit.
        """
        return self._operations

    def add_operation(self, operation: CircuitInstruction):
        """
        Add a operation to the layer
        Args:
            operation (Operation): Information about the operation to be added in the layer
        """

        self._operations.append(operation)

    def add_operations(self, operations: List[CircuitInstruction]):
        """
        Add multiple operations to the layer
        Args:
            operations (list): List of Operation objects
        """

        self._operations.extend(operations)

    def non_local_operations(self):
        """
        Check if a control gate is present in the layer between two different
        computing hosts
        Returns:
            (bool): True if control gate is present between two different computing
                hosts
        """

        non_local_ops = []

        for operation in self._operations:
            if len(operation.qubits) == 2:
                if not self._topology.are_adjacent(operation.qubits[0], operation.qubits[1]):
                    non_local_ops.append(operation)

        return non_local_ops

    def remove_operation(self, index: int):
        """
        Remove an operation from the layer.
        Args:
            index (int): Index of the operation to be removed
        """

        self._operations.pop(index)

    @staticmethod
    def replace_nonlocal_controls(non_local_ops:List[CircuitInstruction], topology:Topology):
        """
        Replace the non-local control gates with Cat entanglement gates for a given layer
        Args:
            non_local_ops (list): List of non-local control gates
        Returns:
            (list): List of new operations to be added in the layer
        """
        #TODO: Implement this function

        for operation in non_local_ops:
            control_qubit = operation.qubits[0]
            target_qubit = operation.qubits[1]
            control_host = topology.get_host(control_qubit)
            target_host = topology.get_host(target_qubit)

            
            epr_qubits = QuantumRegister(2, "epr")
            opr_qubits = QuantumRegister(2, "opr")
            measure_bits = ClassicalRegister(2, "measure")
            qc = QuantumCircuit(epr_qubits, opr_qubits, measure_bits)

            # Generate EPR pair
            qc.h(0)
            qc.cx(0, 1)
            
            # cat entanglement
            qc.cx(2,0)
            qc.measure(0,0)
            qc.x(1).c_if(measure_bits[0], 1)
            qc.cx(1,3)
            qc.h(1)
            qc.measure(1,1)
            qc.z(2).c_if(measure_bits[1], 1)
            
            qc.reset(epr_qubits)

            # Add the new operations to the layer
            new_ops = []
            for op in qc.data:
                new_ops.append(op)
            
        return new_ops

    
    
