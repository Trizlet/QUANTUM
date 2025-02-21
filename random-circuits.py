from qiskit.circuit.random import random_circuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService

# Generate a random circuit
total_bits = 10

service = QiskitRuntimeService(channel="ibm_quantum")
backend = service.least_busy(simulator=False, operational=True)
print(backend.name)

circuit = random_circuit(total_bits, total_bits, measure=True)
# Convert the circuit to ISA at optimization level 3
pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
isa_circuit = pm.run(circuit)

print(circuit.draw())
print(isa_circuit.draw(idle_wires=False))

# Run the circuit on quantum hardware
# job = backend.run(isa_circuit)
# result = job.result()
# Print the result
# print(result.get_counts())
