# Distibuted QC for Qiskit

(in development)

This project is a library for performing distributed quantum computing in Qiskit. The idea is to take a monolithic quantum circuit developed in the Qiskit language and distribute the circuit according to an artificially segmented version of a quantum processor. The input to the algorithm is monolithic circuit and a segmentation topology data structure. Included as input to the algorothm are optimization parameters to make in order to improve aspects like classical communication overhead and algorithm structure.
