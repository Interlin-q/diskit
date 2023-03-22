Quickstart
==========

Diskit is available as a PyPi project and is can be installed with ``pip``. ::

    pip install diskit

Diskit relies on Qiskit and therefore it should also be installed.
Once installed, to generate a distributed circuit, one can simply generate a topology,
create the circuit, perform the remapping, and run it as usual. ::

    from diskit import *

    network_topology = Topology()
    network_topology.create_qmap(2, [1, 1], "sys")
    qregs = circuit_topo.get_regs()

    qc = QuantumCircuit(*qregs)
    # Qubit 0 is on QPU 1, qubit 1 on QPU 2
    qc.h(0)
    qc.cx(0, 1)

    remapper = CircuitRemapper(circuit_topo)
    dist_circ = remapper.remap_circuit(qc)
