from numpy import pi

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit_aer import AerSimulator

total_bits = 8

service = QiskitRuntimeService(channel="ibm_quantum")
backend = service.least_busy(simulator=False, operational=True)
print(f"\nBest fit system: {backend.name}")

qreg_q = QuantumRegister(total_bits, "q")
# creg_c = ClassicalRegister(total_bits, "c")
# circuit = QuantumCircuit(qreg_q, qreg_c)
circuit = QuantumCircuit(qreg_q)

for x in range(0, total_bits):
    circuit.h(qreg_q[x])
    # circuit.measure(qreg_q[x], creg_c[x])
circuit.measure_all()

pm = generate_preset_pass_manager(backend=backend, optimization_level=3)
isa_circuit = pm.run(circuit)

if total_bits <= 16:
    print("\nBasic circuit:")
    print(circuit.draw())
    print("\nISA circuit conversion:")
    print(isa_circuit.draw(idle_wires=False))

# result = AerSimulator().run(isa_circuit, shots=1).result()
# statistics = result.get_counts(isa_circuit)
# print(statistics)

sampler = Sampler(mode=backend, options={"default_shots": 5})
job = sampler.run([isa_circuit], shots=1)

job.wait_for_final_state(timeout=300)
job_result = job.result()

# Get the PUB (Primitive Unified Bloc) result.
pub_result = job_result[0]

combined_counts = pub_result.join_data().get_counts()

binary_str = list(combined_counts.keys())[0]
hex_str = f"{int(binary_str, 2):X}"

if len(binary_str) > 8:
    print(f"\nGenerated ({len(binary_str)}) bit random value (0x{hex_str})\n")
else:
    print(f"\nGenerated ({len(binary_str)}) bit random value (0x{hex_str}) or ({binary_str})\n")
