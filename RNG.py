from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# CONFIG

total_bits = 127
Sim = True
Simple_Measure = True
Optimization_Level = 3
Circuit_Diagram = 0

if total_bits > 127:
    print("invalid bit length! free QPU limited to 127 qubits.")
    quit()

# Create qiskit service and backend

service = QiskitRuntimeService(channel="ibm_quantum")

if Sim:
    backend = service.backend("ibm_kyiv")
else:
    backend = service.least_busy(simulator=False, operational=True)
    print(f"\nBest fit system: {backend.name}")

# Create the circuit with manually set classical bits OR use measure_all which automatically appends necessary classical bits

if Simple_Measure:
    qreg_q = QuantumRegister(total_bits, "q")
    circuit = QuantumCircuit(qreg_q)
    for x in range(0, total_bits):
        circuit.h(qreg_q[x])
    circuit.measure_all()
else:
    qreg_q = QuantumRegister(total_bits, "q")
    creg_c = ClassicalRegister(total_bits, "c")
    circuit = QuantumCircuit(qreg_q, creg_c)
    for x in range(0, total_bits):
        circuit.h(qreg_q[x])
        circuit.measure(qreg_q[x], creg_c[x])

# Convert the basic circuit to an ISA circuit with or without optimization

pm = generate_preset_pass_manager(backend=backend, optimization_level=Optimization_Level)
isa_circuit = pm.run(circuit)

# Display the circuit diagrams (capped to 16 bits cause any longer can be too big for the terminal)

if total_bits <= 16:
    if Circuit_Diagram == 1:
        print("\nBasic circuit:")
        print(circuit.draw())
    if Circuit_Diagram == 2:
        print("\nISA circuit conversion:")
        print(isa_circuit.draw(idle_wires=False))
    if Circuit_Diagram == 3:
        print("\nBasic circuit:")
        print(circuit.draw())
        print("\nISA circuit conversion:")
        print(isa_circuit.draw(idle_wires=False))

# Run the simulator or run the job on a QPU

if Sim:
    result = AerSimulator().run(isa_circuit, shots=1).result()
    statistics = result.get_counts(isa_circuit)
    print("\nSim result: ", statistics)
else:
    sampler = Sampler(mode=backend, options={"default_shots": 5})
    job = sampler.run([isa_circuit], shots=1)
    job.wait_for_final_state(timeout=300)

    # Wait for the results and parse them for display

    job_result = job.result()
    pub_result = job_result[0]

    combined_counts = pub_result.join_data().get_counts()

    binary_str = list(combined_counts.keys())[0]
    hex_str = f"{int(binary_str, 2):X}"

    if len(binary_str) > 8:  # Dont flood the terminal with binary
        print(f"\nGenerated ({len(binary_str)}) bit random value (0x{hex_str})\n")
    else:
        print(f"\nGenerated ({len(binary_str)}) bit random value (0x{hex_str}) or ({binary_str})\n")
