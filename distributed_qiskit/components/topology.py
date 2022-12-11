"""Topology class for mapping distributed quantum computers."""
from typing import List, Dict, Optional

class Topology:
    """
    Topology class for a distributed architecture.
    """

    def __init__(self, q_map : Dict[str, List[str]], e_map:Dict[str, List[str]] = None):
        """Initialize the topology object"""
        self.q_map = q_map
        self.e_map = e_map
        self.q_hosts = list(q_map.keys())
        self.qubits = []
        for qubit in q_map.values():
            self.qubits += qubit
        
    def num_qubits(self):
        """Return the total number of qubits in the topology"""
        return len(self.qubits)

    def num_hosts(self):
        """Return the total number of hosts in the topology"""
        return len(self.q_hosts)

    def are_adjacent(self, qubit1 : str, qubit2 : str):
        """Return True if qubit1 and qubit2 are adjacent"""
        for host in self.q_hosts:
            if qubit1 in self.q_map[host] and qubit2 in self.q_map[host]:
                return True
        return False
    
    def get_host(self, qubit : str):
        """Return the host of qubit"""
        for host in self.q_hosts:
            if qubit in self.q_map[host]:
                return host
        return None

    def get_epr_id(self, host):
        """ Return the epr qubit IDs """
        return self.e_map[host]


    


