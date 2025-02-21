from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(
    channel="ibm_quantum",
    instance="ibm-q/open/main",
)
job = service.job("cyw04ah4raf0008es90g")
job_result = job.result()

# Get the PUB (Primitive Unified Bloc) result.
pub_result = job_result[0]

spans = job_result.metadata["execution"]["execution_spans"]
print("Duration: ", spans.stop, "-", spans.start)

combined_counts = pub_result.join_data().get_counts()

binary_str = list(combined_counts.keys())[0]
hex_str = f"{int(binary_str, 2):X}"

if len(binary_str) > 8:
    print(f"\nGenerated ({len(binary_str)}) bit random value (0x{hex_str})\n")
else:
    print(f"\nGenerated ({len(binary_str)}) bit random value (0x{hex_str}) or ({binary_str})\n")
