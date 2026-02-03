from qwen_module import QwenModule
import os
from opencc import OpenCC
path = os.path.join(os.path.dirname(__file__), "Qwen3-4B-nolimit")
# from tools.tools_prompt import tools_prompt

qwen = QwenModule(
    path=path,
    prompt="你是女僕芩紗，是個溫柔的人。",
    enable_think=True,
    MAX_TOKEN=1024
)

s2tw = OpenCC("s2tw")
tw2s = OpenCC("tw2s")
while True:
    u = input("你：")
    user_input = tw2s.convert(u, )
    response = qwen.chat(user_input, thinking=False)
    print("芩紗：", s2tw.convert(response))

    # print(qwen)