"""Test Cases for Topology Module (Test Succeeded for all unit methods)"""

from qiskit.circuit.quantumregister import QuantumRegister, Qubit
from diskit import Topology  # pylint: disable=import-error, wrong-import-position


class TestClass:
    """
    Test Cases for Topology Module
    """
    circuit_topo = Topology()
    circuit_topo.create_qmap(3, [2, 3, 3], "sys")

    def test_one(self):
        """
        Test the create_qmap method
        """
        assert self.circuit_topo.qmap["sys0"] == [Qubit(QuantumRegister(2, 'sys0'), 0), Qubit(
            QuantumRegister(2, 'sys0'), 1)]
        assert self.circuit_topo.qmap["sys1"] == [Qubit(QuantumRegister(3, 'sys1'), 0), Qubit(
            QuantumRegister(3, 'sys1'), 1), Qubit(QuantumRegister(3, 'sys1'), 2)]
        assert self.circuit_topo.qmap["sys2"] == [Qubit(QuantumRegister(3, 'sys2'), 0), Qubit(
            QuantumRegister(3, 'sys2'), 1), Qubit(QuantumRegister(3, 'sys2'), 2)]
        assert self.circuit_topo.emap["sys0"] == Qubit(
            QuantumRegister(1, 'com_sys0'), 0)
        assert self.circuit_topo.emap["sys1"] == Qubit(
            QuantumRegister(1, 'com_sys1'), 0)
        assert self.circuit_topo.emap["sys2"] == Qubit(
            QuantumRegister(1, 'com_sys2'), 0)

    def test_two(self):
        """
        Test add_qpu method
        """
        self.circuit_topo.add_qpu("sys3", 3, "test_name", [0, 1, 2])
        assert self.circuit_topo.qmap["sys3"] == [Qubit(QuantumRegister(3, "test_name"), 0), Qubit(
            QuantumRegister(3, "test_name"), 1), Qubit(QuantumRegister(3, "test_name"), 2)]
        assert self.circuit_topo.emap["sys3"] == Qubit(
            QuantumRegister(1, 'com_sys3'), 0)

    def test_three(self):
        """
        Test num_qubits method
        """
        assert self.circuit_topo.num_qubits() == 11

    def test_four(self):
        """
        Test num_hosts method
        """
        assert self.circuit_topo.num_hosts() == 4

    def test_five(self):
        """
        Test reinitialize method
        """
        self.circuit_topo.reinitialize({"sys0": [Qubit(QuantumRegister(2, 'sys0'), 0), Qubit(
            QuantumRegister(2, 'sys0'), 1)], "sys1": [Qubit(QuantumRegister(3, 'sys1'), 0), Qubit(
            QuantumRegister(3, 'sys1'), 1), Qubit(QuantumRegister(3, 'sys1'), 2)]})
        assert self.circuit_topo.qmap["sys0"] == [Qubit(QuantumRegister(2, 'sys0'), 0), Qubit(
            QuantumRegister(2, 'sys0'), 1)]
        assert self.circuit_topo.qmap["sys1"] == [Qubit(QuantumRegister(3, 'sys1'), 0), Qubit(
            QuantumRegister(3, 'sys1'), 1), Qubit(QuantumRegister(3, 'sys1'), 2)]
        assert self.circuit_topo.emap["sys0"] == Qubit(
            QuantumRegister(1, 'com_sys0'), 0)
        assert self.circuit_topo.emap["sys1"] == Qubit(
            QuantumRegister(1, 'com_sys1'), 0)
        assert self.circuit_topo.num_qubits() == 5
        assert self.circuit_topo.num_hosts() == 2

    def test_six(self):
        """
        Test are_adjacent method
        """
        qubit_1 = self.circuit_topo.qmap["sys1"][2]
        qubit_2 = self.circuit_topo.qmap["sys2"][1]
        assert self.circuit_topo.are_adjacent(qubit_1, qubit_2) is False
        qubit_1 = self.circuit_topo.qmap["sys1"][2]
        qubit_2 = self.circuit_topo.qmap["sys1"][1]
        assert self.circuit_topo.are_adjacent(qubit_1, qubit_2) is True

    def test_seven(self):
        """
        Test get_host method
        """
        qubit_1 = self.circuit_topo.qmap["sys1"][2]
        assert self.circuit_topo.get_host(qubit_1) == "sys1"

    def test_eight(self):
        """
        Test get_qubits method
        """
        assert self.circuit_topo.get_qubits("sys1") == [Qubit(QuantumRegister(3, 'sys1'), 0), Qubit(
            QuantumRegister(3, 'sys1'), 1), Qubit(QuantumRegister(3, 'sys1'), 2)]

    def test_nine(self):
        """
        Test get_all_qubits method
        """
        assert self.circuit_topo.get_all_qubits() == [Qubit(QuantumRegister(2, 'sys0'), 0), Qubit(
            QuantumRegister(2, 'sys0'), 1), Qubit(QuantumRegister(3, 'sys1'), 0), Qubit(
            QuantumRegister(3, 'sys1'), 1), Qubit(QuantumRegister(3, 'sys1'), 2), Qubit(
            QuantumRegister(3, 'sys2'), 0), Qubit(QuantumRegister(3, 'sys2'), 1), Qubit(
            QuantumRegister(3, 'sys2'), 2), Qubit(QuantumRegister(3, "test_name"), 0), Qubit(
            QuantumRegister(3, "test_name"), 1), Qubit(QuantumRegister(3, "test_name"), 2), Qubit(
            QuantumRegister(1, 'com_sys0'), 0), Qubit(QuantumRegister(1, 'com_sys1'), 0), Qubit(
            QuantumRegister(1, 'com_sys2'), 0), Qubit(QuantumRegister(1, 'com_sys3'), 0)]

    def test_ten(self):
        """
        Test remove_qpu method
        """
        self.circuit_topo.remove_qpu("sys1")
        assert "sys1" not in self.circuit_topo.qmap.keys()
        assert "sys1" not in self.circuit_topo.emap.keys()
        assert self.circuit_topo.num_qubits() == 8
        assert self.circuit_topo.num_hosts() == 3

    def test_twelve(self):
        """
        Test get_regs method
        """
        assert self.circuit_topo.get_regs() == [QuantumRegister(2, 'sys0'), QuantumRegister(
            3, 'sys2'), QuantumRegister(3, "test_name"), QuantumRegister(
            1, 'com_sys0'), QuantumRegister(1, 'com_sys2'), QuantumRegister(1, 'com_sys3')]
