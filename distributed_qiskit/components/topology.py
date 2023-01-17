"""Topology class for mapping distributed quantum computers."""
from typing import List, Dict, Optional


class Topology:
    """
    Topology class for a distributed architecture.
    """

    def __init__(self, q_map: Dict[str, List[str]], e_map: Dict[str, List[str]] = None):
        """Initialize the topology object"""
        self.q_map = q_map
        self.e_map = e_map
        self.q_hosts = list(q_map.keys())
        self.qubits = []
        for qubit in q_map.values():
            self.qubits += qubit

    def add_qpus(self, num_qpus: int):
        """Helper function for building out the topology. Given a number of QPUs *num_qpus*,
        create *num_qpus* QPU keys in the q_map"""
        pass

    def add_qubits_to_qpu(self, qpu: int, num_qubits: int):
        """Helper function for adding qubits to QPU *qpu*. Given a number of qubits *num_qubits*,
        create *num_qubits* for QPU *qpu*."""
        pass

    def num_qubits(self):
        """Return the total number of qubits in the topology"""
        return len(self.qubits)

    def num_hosts(self):
        """Return the total number of hosts in the topology"""
        return len(self.q_hosts)

    def are_adjacent(self, qubit1: str, qubit2: str):
        """Return True if qubit1 and qubit2 are adjacent"""
        for host in self.q_hosts:
            if qubit1 in self.q_map[host] and qubit2 in self.q_map[host]:
                return True
        return False

    def get_host(self, qubit: str):
        """Return the host of qubit"""
        for host in self.q_hosts:
            if qubit in self.q_map[host]:
                return host
        return None

    def get_epr_id(self, host):
        """ Return the epr qubit IDs """
        return self.e_map[host]

    def get_qubit_ids(self, host):
        """ Return the qubit IDs """
        return self.q_map[host]
