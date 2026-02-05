from .prompter import SUMMARY_PROMPT, USER_PROMPT
from .generator_cfg import SUMMARY_GENERATOR_CFG


class SummaryCaller:
    def __init__(self, generator):
        self.gen = generator

    def call(self, old_history: list[dict], 
             summary_prompt:str=SUMMARY_PROMPT,
             user_prompt:str=USER_PROMPT):
        history = [
            {"role": "system", "content": summary_prompt},
            *old_history,
            {"role": "user", "content": user_prompt}
        ]
        
        # 進行 prompt 輸出
        response = self.gen.generate(
            history,
            gen_cfg=SUMMARY_GENERATOR_CFG
        )
        
        return response

