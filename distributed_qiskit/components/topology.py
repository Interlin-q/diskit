"""Topology class for mapping distributed quantum computers."""
from typing import List, Dict, Optional
from qiskit.circuit.quantumregister import QuantumRegister, Qubit
from qiskit.circuit.exceptions import CircuitError


class Topology:
    """
    Topology class for a distributed architecture.
    """

    def __init__(self, qmap: Optional[Dict[str, List[str]]] = None):
        """Initialize the topology object"""
        if qmap is None:
            self._qmap = {}
            self.emap = None
            self.q_hosts = None
            self.qubits = None
        else:
            self._qmap = qmap
            self.emap = self.create_emap()
            self.q_hosts = list(qmap.keys())
            self.qubits = []
            for qubit in qmap.values():
                self.qubits += qubit

    def reinitialize(self, qmap: Dict[str, List[str]]):
        """Reinitialize the topology object by providing a new qmap"""
        self.emap = self.create_emap()
        self.q_hosts = list(qmap.keys())
        self.qubits = []
        for qubit in qmap.values():
            self.qubits += qubit

    def add_qpu(self, qpu: str, num_qubits: int, qreg: str = None, indices: List[int] = None):
        """Add a QPU to the qmap. *qpu* is the name of the QPU, and *num_qubits* is the number of
        qubits on the QPU."""
        if qreg is None:
            qreg = QuantumRegister(num_qubits, qpu)
            self.qmap[qpu] = [Qubit(qreg, i) for i in range(num_qubits)]
            self.reinitialize(self.qmap)
        elif indices is not None:
            if len(indices) != num_qubits:
                raise CircuitError(
                    "QuantumRegister was provided but with a different number of indices.")
            qreg = QuantumRegister(num_qubits, qreg)
            self.qmap[qpu] = [Qubit(qreg, i) for i in indices]
            self.reinitialize(self.qmap)
        else:
            raise CircuitError(
                "QuantumRegister was provided but with no indices.")

    def num_qubits(self):
        """Return the total number of qubits in the topology"""
        return len(self.qubits)

    def num_hosts(self):
        """Return the total number of hosts in the topology"""
        return len(self.q_hosts)

    def are_adjacent(self, qubit1: str, qubit2: str):
        """Return True if qubit1 and qubit2 are adjacent"""
        for host in self.q_hosts:
            if qubit1 in self.qmap[host] and qubit2 in self.qmap[host]:
                return True
        return False

    def get_host(self, qubit: str):
        """Return the host of qubit."""
        for host in self.q_hosts:
            if qubit in self.qmap[host]:
                return host
        return None

    def get_epr_id(self, host):
        """Return the epr qubit IDs."""
        return self.emap[host]

    def get_all_qubits(self):
        """Return all the qubits in the qmap."""
        qubits = []
        for qpu in self.qmap:
            qubits += self.qmap[qpu]
        for qpu in self.emap:
            qubits.append(self.emap[qpu])
        return qubits

    @property
    def qmap(self):
        """The topology map."""
        return self._qmap

    def remove_qpu(self, qpu: str):
        """Remove a QPU from the qmap."""
        self.qmap.pop(qpu)
        self.reinitialize(self.qmap)

    def create_qmap(self, num_qpus: int, num_qubits: List[int], name: str = "qpu"):
        """Create a qmap with *num_qpus* QPUs, each with *num_qubits* qubits."""
        for i in range(num_qpus):
            self.add_qpu(f"{name}{i}", num_qubits[i])
        self.reinitialize(self.qmap)

    def get_qubits(self, qpu: str):
        """Return the qubits on a QPU."""
        return self.qmap[qpu]

    def get_qpu(self, qubit: Qubit):
        """Return the QPU of a qubit."""
        for qpu in self.qmap:
            if qubit in self.qmap[qpu]:
                return qpu
        return None

    def create_emap(self):
        """Create an emap from the qmap."""
        emap = {}
        for qpu in self.qmap:
            ereg = QuantumRegister(1, f"com_{qpu}")
            emap[qpu] = Qubit(ereg, 0)
        return emap

    def get_regs(self):
        """Return the QuantumRegisters in the qmap."""
        regs = []
        for qpu in self.qmap:
            regs.append(self.qmap[qpu][0].register)
        for qpu in self.emap:
            regs.append(self.emap[qpu].register)
        return regs


if __name__ == "__main__":
    t = Topology()
