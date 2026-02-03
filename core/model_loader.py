from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

def load_model(path):
    quant_config = BitsAndBytesConfig()

    model = AutoModelForCausalLM.from_pretrained(
        path,
        torch_dtype="auto",
        device_map="auto",
        quantization_config=quant_config,
        attn_implementation="sdpa"
    )
    return model
