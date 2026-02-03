from transformers import AutoTokenizer

class TokenizerEngine:
    def __init__(self, path):
        self.tokenizer = AutoTokenizer.from_pretrained(path)

    def build_prompt(self, history, thinking=False):
        return self.tokenizer.apply_chat_template(
            conversation=history,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=thinking
        )

    def encode(self, text):
        return self.tokenizer([text], return_tensors="pt", padding=True)

    def decode(self, ids):
        return self.tokenizer.batch_decode(
            ids, skip_special_tokens=True
        )[0].strip()
    
    def count_tokens(self, history:list|str):
        if isinstance(history, str):
            return len(self.tokenizer.encode(history, add_special_tokens=False))
        elif isinstance(history, list):
            prompt = self.build_prompt(history)
            return len(self.tokenizer.encode(prompt, add_special_tokens=False))
