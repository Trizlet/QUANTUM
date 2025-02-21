import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model name
MODEL_NAME = "Qiskit/granite-8b-qiskit-rc-0.10"

# Load model efficiently
if torch.cuda.is_available():
    print("GPU detected, trying 4-bit loading...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="auto",
            load_in_4bit=True,  # Try 4-bit for lower VRAM usage
        )
    except Exception as e:
        print("4-bit loading failed, falling back to BF16:", str(e))
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
else:
    print("No GPU detected, running on CPU (slow).")
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Chat-style prompt template
chat = [
    {
        "role": "user",
        "content": "modify ``` from qiskit_ibm_runtime import QiskitRuntimeService service = QiskitRuntimeService( channel='ibm_quantum', instance='ibm-q/open/main', token='876bca92009c011aa281f3cb00e9331f2d6d02e0bf62af5477cb7e32d2289eb07035ae2d5dac73268981ac49c23c0f7f75eb4e2c4ec54cb02b3504386e874457',) job = service.job('cyw04ah4raf0008es90g') job_result = job.result() pub_result = job.result()[0] print(pub_result)``` to print all classical bits returned by the job",
    }
]


# Convert chat messages to model's expected format
def format_chat_prompt(chat):
    formatted = ""
    for message in chat:
        if message["role"] == "user":
            formatted += f"User: {message['content']}\n"
        elif message["role"] == "assistant":
            formatted += f"Assistant: {message['content']}\n"
    formatted += "Assistant:"  # Ensure the model knows it's supposed to reply
    return formatted


# Prepare input
formatted_prompt = format_chat_prompt(chat)
inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

# Generate response
with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=2000,  # Adjust based on how much response you want
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )

# Decode and print result
response = tokenizer.decode(output[0], skip_special_tokens=True)
print("\nGenerated Response:\n", response)
