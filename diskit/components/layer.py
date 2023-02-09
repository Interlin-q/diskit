"""Layer object which is a collection of operations to be applied on the qubits in the system."""
from typing import List, Optional
from qiskit.circuit.quantumcircuitdata import CircuitInstruction
from .topology import Topology


class Layer:
    """
    Layer object which is a collection of operations to be applied on the qubits in the system.
    """

    def __init__(self, operations: Optional[List[CircuitInstruction]] = None,
                 topology: Topology = None):
        """
        Returns the important things for a layer in a quantum circuit.

        Args:
            operations (list): List of Operation objects, which contains
            information about the operation to be
            performed on the quantum circuit
        """

        self._operations = operations if operations is not None else []
        self._topology = topology

    def __str__(self):
        layer = ""

        for operation in self._operations:
            layer += f"-{operation}-|\n"

        return layer

    @property
    def operations(self):
        """
        Get the *operations* in the layer.

        Returns:
            (list): List of Operation objects, which contains information about the operation to
                    be performed on the quantum circuit.
        """
        return self._operations

    def add_operation(self, operation: CircuitInstruction):
        """
        Add an operation to the layer.
        Args:
            operation (Operation): Information about the operation to be added in the layer
        """

        self._operations.append(operation)

    def add_operations(self, operations: List[CircuitInstruction]):
        """
        Add multiple operations to the layer.

        Args:
            operations (list): List of Operation objects
        """
        self._operations.extend(operations)

    def non_local_operations(self):
        """
        Check if a control gate is present in the layer between two different
        computing hosts.

        Returns:
            (bool): True if control gate is present between two different computing hosts
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
