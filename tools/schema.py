from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable
import json

@dataclass(slots=True)
class ToolParameter:
    type: str
    description: str


@dataclass(slots=True)
class ToolParametersSchema:
    type: str = "object"
    properties: Dict[str, ToolParameter] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)


@dataclass(slots=True)
class ToolSchema:
    name: str
    description: str
    parameters: ToolParametersSchema
    func: Callable | None = None

    # 給 tools_caller 裡面工具呼叫 system 用的
    def to_prompt_str(self)->str:
        schema_dict = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": self.parameters.type,
                "properties": {
                    k: {
                        "type": v.type,
                        "description": v.description
                    }
                    for k, v in self.parameters.properties.items()
                },
            "required": self.parameters.required
            }
        }
        return json.dumps(schema_dict, ensure_ascii=False, indent=2)

