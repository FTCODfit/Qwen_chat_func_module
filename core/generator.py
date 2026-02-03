import re
import torch

class Generator:
    def __init__(self, model, tokenizer_engine, enable_think=False):
        self.model = model
        self.tok = tokenizer_engine
        self.enable_think = enable_think

    @torch.inference_mode()
    def generate(
        self,
        history,
        thinking=False,
        gen_cfg=None
    ):
        if gen_cfg==None:
            gen_cfg = {}
        
        # === 預設參數 ===
        default_cfg = dict(
            max_new_tokens=2048,
            do_sample=True,
            temperature=0.6 if thinking else 0.7,
            top_p=0.9,
            repetition_penalty=1.2
        )
        # 外部設置覆蓋 cfg
        default_cfg.update(gen_cfg)

        text = self.tok.build_prompt(history, thinking)
        inputs = self.tok.encode(text).to("cuda")

        ids = self.model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            **default_cfg
        )

        gen_ids = ids[:, inputs.input_ids.shape[1]:]
        response = self.tok.decode(gen_ids)

        if self.enable_think and thinking:
            response = re.sub(
                r"<think>.*?</think>", "", response, flags=re.DOTALL
            ).strip()

        return response
