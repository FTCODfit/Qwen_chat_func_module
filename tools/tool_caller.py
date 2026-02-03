import re
import json
from .prompter import build_tools_prompt
from .builtins import TOOLS
from .generator_cfg import TOOLS_GENERATOR_CFG


class ToolCaller:
    def __init__(self, generator):
        self.gen = generator
        self.tool_map = {schema.name: schema for schema in TOOLS}

    def call(self, text: str):
        history = [
            {"role": "system", "content": build_tools_prompt(TOOLS)},
            {"role": "user", "content": text}
        ]
        
        # 第一段：判斷是否要用工具
        response = self.gen.generate(
            history,
            gen_cfg=TOOLS_GENERATOR_CFG
        )
        print(response)
        result = self._parser_call(response)
        if not result:
            return None
        
        name, arguments = result
        response = self._dispatch(name, arguments)
        
        if not response:
            return None
        else:
            return response


    def _parser_call(self, text:str=""):
        if not text:
            return None

        match_json = re.search(r"\{.*\}", text, re.DOTALL) # DATALL 避免 . 無法匹配 \n
        if not match_json:
            return None
        
        # 嘗試只抓 json
        try: 
            payload = json.loads(match_json.group(0))
        except json.JSONDecodeError:
            return None
        
            # 最小結構驗證
        if not isinstance(payload, dict):
            return None
        
        name = payload.get("name")
        arguments = payload.get("arguments")

        if not isinstance(name, str):
            return None

        if not isinstance(arguments, dict):
            return None

        return name, arguments

    def _dispatch(self, name: str, arguments: dict):
        schema = self.tool_map.get(name)
        if not schema:
            # raise ValueError(f"Tool not registered: {name}")
            return None

        return schema.func(**arguments)

