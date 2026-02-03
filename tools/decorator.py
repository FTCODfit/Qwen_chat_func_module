from typing import Dict, List, Callable
from tools.schema import ToolSchema, ToolParametersSchema, ToolParameter

"""
tool 裝飾器方便後續擴充 function 功能時，不用在多處重複定義參數與說明，省下掃描、描述與調用。
"""
def tool(
    *,
    name: str,
    description: str,
    parameters: Dict[str, ToolParameter],
    required: List[str] | None = None
):

    # 將一個 function 標記為 Tool，並綁定 ToolSchema。
    def decorator(func: Callable):
        schema = ToolSchema(
            name=name,
            description=description,
            parameters=ToolParametersSchema(
                properties=parameters,
                required=required or []
            ),
            func=func
        )

        # 將 schema 掛在 function (預寫)
        func.__tool_schema__ = schema
 
        return func 

    return decorator
