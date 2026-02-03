def build_tools_prompt(tool_schemas: list) -> str:
    tools_desc = "\n\n".join(
        schema.to_prompt_str() for schema in tool_schemas
    )

    return f"""
你正在进行【工具调用判断】。

当问题涉及实时信息、计算或外部数据时，必须使用工具。
否则，直接输出 None。

可用工具：
{tools_desc}

【输出规则（严格）】
- 需要工具时，只能输出 JSON
- 不需要工具时，只能输出 None
- 不得输出任何解释或多余文字

JSON 格式如下：
{{
  "name": "<工具名>",
  "arguments": {{
    "<参数名>": "<参数值>"
  }}
}}

【严格规则】
1. name 必须完全匹配工具名
2. arguments 必须是 JSON 对象
3. 禁止猜测或伪造工具结果
4. 输出不符合格式将被视为错误

你不是在回答用户，只是在决定是否调用工具。
"""
