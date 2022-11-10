'''
The circuit remapper logic.
'''
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

    def _circuit_to_layers(self):
        '''Given a Qiskit circuit, return an array of the layers of that circuit'''        
        # TODO implement this
        pass
