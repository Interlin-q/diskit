Welcome to Diskit documentation!
================================


..  toctree::
    :caption: Contents
    :includehidden:
    :maxdepth: 2

    quick_start
    examples
    source

Introduction
============

Distributed quantum computing is a concept that proposes to connect multiple quantum computers in a network to leverage a collection of more, but physically separated, qubits. In order to perform distributed quantum computing, it is necessary to add the addition of classical communication and entanglement distribution so that the control information from one qubit can be applied to another that is located on another quantum computer. For more details on distributed quantum computing, see this blog post: `Distributed Quantum Computing: A path to large scale quantum computing <https://medium.com/@stephen.diadamo/distributed-quantum-computing-1c5d38a34c50>`_

In this project, we aim to validate distributed quantum algorithms using Qiskit. Because Qiskit does not yet come with networking features, we embed a "virtual network topology" into large circuits to mimic distributed quantum computing. The idea is to take a monolithic quantum circuit developed in the Qiskit language and distribute the circuit according to an artificially segmented version of a quantum processor. The inputs to the library are a quantum algorithm written monolithically (i.e., in a single circuit) and a topology parameter that represents the artificial segmentation of the single quantum processor.

The algorithm takes these two inputs and remaps the Qiskit circuit to the specified segmentation, adding all necessary steps to perform an equivalent distributed quantum circuit. Our algorithm for achieving this is based on the work: `Distributed Quantum Computing and Network Control for Accelerated VQE
<https://ieeexplore.ieee.org/document/9351762>`_. The algorithm output is another Qiskit circuit with the equivalent measurement statistics but with all of the additional logic needed to perform a distributed version.

..  figure:: ./images/SEG-QPU.png
    :align: center
    :width: 500
    :alt: Segmented QPU

The algorithm proposed in the linked work is not yet optimized, and so we encourage users to contribute by adding other methods of distributing circuits to the library.
