""" Test Cases for Circuit Remapper Module """
from diskit import Topology, CircuitRemapper
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.quantumregister import QuantumRegister, Qubit


class TestClass:
    """
    Test Cases for Circuit Remapper Module
    """
    circuit_topo = Topology()
    circuit_topo.create_qmap(3, [2, 3, 3], "sys")
    remapper = CircuitRemapper(circuit_topo)
    regs = circuit_topo.get_regs()
    circuit = QuantumCircuit(*regs)
    circuit.h(0)
    circuit.cx(0, 5)

    def test_basic_creation(self):
        """ Test remap_circuit method """
        dist_circ = self.remapper.remap_circuit(self.circuit)
        assert dist_circ.qubits == [Qubit(QuantumRegister(2, 'sys0'), 0), Qubit(
            QuantumRegister(2, 'sys0'), 1), Qubit(QuantumRegister(3, 'sys1'), 0), Qubit(
            QuantumRegister(3, 'sys1'), 1), Qubit(QuantumRegister(3, 'sys1'), 2), Qubit(
            QuantumRegister(3, 'sys2'), 0), Qubit(QuantumRegister(3, 'sys2'), 1), Qubit(
            QuantumRegister(3, 'sys2'), 2), Qubit(QuantumRegister(1, 'com_sys0'), 0), Qubit(
            QuantumRegister(1, 'com_sys1'), 0), Qubit(QuantumRegister(1, 'com_sys2'), 0)]

        assert dist_circ.data[0][0].name == "h"
        assert dist_circ.data[0][1][0] == Qubit(QuantumRegister(2, 'sys0'), 0)
        assert dist_circ.data[2][0].name == "cx"
