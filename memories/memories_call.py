import re
import ast
from .prompter import memories_prompt
from .generator_cfg import MEMORIES_GENERATOR_CFG
from .persona.persona_profile import persona
class MemoriesCaller:
    def __init__(self, generator):
        self.gen = generator

    def call(self, text: str):
        history = [
            {"role": "system", "content": memories_prompt},
            {"role": "user", "content": text}
        ]
        
        # 第一段：判斷是否要用
        response = self.gen.generate(
            history,
            gen_cfg=MEMORIES_GENERATOR_CFG
        )

        memories_ids = self._parser_call(response)
        if not memories_ids:
            return None
        
        memories_return = ""
        for memory_id in memories_ids:
            if memory_id not in persona:
                continue
            memories_return += f"- {memory_id}: {persona[memory_id]['document']}\n"
        if memories_return=="":
            return None
        else:
            return memories_return


    def _parser_call(self, text:str=""):
        """
        預期模型回傳格式：
        ["喜歡的水果", "喜歡的運動"]
        """

        if not text:
            return None
        if text==None:
            return []
        match_list = re.search(r"\[[^\]]*\]", text, re.DOTALL) # DATALL 避免 . 無法匹配 \n

        if not match_list:
            return []
        
        # 嘗試只抓 list
        try: 
            payload = ast.literal_eval(match_list.group())
            if isinstance(payload, list) and all(isinstance(x, str) for x in payload):
                return payload
            
        except:
            return None



print(memories_prompt)



