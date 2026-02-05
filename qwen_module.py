from core.model_loader import load_model
from core.tokenizer_engine import TokenizerEngine
from core.conversation import Conversation
from core.generator import Generator

import tools.tool_caller as tools_caller
import memories.memories_call as memories_caller
import threading
import re

class QwenModule:
    def __init__(
        self,
        path,
        prompt="",
        MAX_TOKEN=8192,
        enable_think=False
    ):
        self.model = load_model(path)
        self.tokenizer = TokenizerEngine(path)

        self.conv = Conversation()
        self.conv.reset("chat", prompt) # 初始化傳入的 prompt
        self.gen = Generator(
            self.model,
            self.tokenizer,
            enable_think=enable_think
        )
        self.MAX_TOKEN = MAX_TOKEN
        self.chat_prompt = prompt


        # 多程序執行
        self._summarizing = False # 摘要是否執行狀態
        self._cond = threading.Condition()

        self.ToolCaller = tools_caller.ToolCaller(self.gen)
        self.MemoryCaller = memories_caller.MemoriesCaller(self.gen)
    def chat(self, user_input, thinking=False):

        # res = self.ToolCaller.call(text= user_input)
        # res = self.MemoryCaller.call(text=user_input)s

        with self._cond:
            while self._summarizing:
                self._cond.wait() # 等待 summary 完成
            # chat 回應狀態 
            if self.tokenizer.count_tokens(user_input)>1024:
                print(self.tokenizer.count_tokens(user_input))
                user_input = self._summary("user", user_input)
                print("user 摘要: ", user_input)
                
            content = user_input + (" /think" if thinking else "")

            self.conv.add_user(content, "chat")
            # 記憶插入 
            history = self._memories_insert(self.conv.chat_history, user_input)
            # 工具插入
            history = self._tools_insert(history, user_input)

            response = self.gen.generate(
                history,
                thinking=thinking
                )
            self.conv.add_assistant(response, "chat")
            print(history)

        # 開始檢查是否需要摘要，如果需要開 thread 去處理，避免 response return 堵住
        print(self.tokenizer.count_tokens(self.conv.get("chat")))
        if self.tokenizer.count_tokens(self.conv.get("chat"))>0.8*self.MAX_TOKEN:
            self._start_background_summary()

        return response

    def _chat_summary(self, chat_turn, ratio):
        with self._cond:
            chat = self.conv.get("chat")[1:].copy() 
            remain_chat = chat[-2*chat_turn:].copy()
            count=0
            while self.tokenizer.count_tokens(remain_chat)<=ratio*self.MAX_TOKEN:
                count+=1
                remain_chat = chat[-2*chat_turn-2*count:].copy()

            summary_chat = chat[:-2*chat_turn-2*count].copy()

        summary_prompt = [{
                "role": "system",
                "content": (
                    "你是一個人格與關係記憶整理器。\n"
                    "請從以下對話中，整理未來仍需記住的關係狀態與情感變化。\n\n"
                    "規則：\n"
                    "1. 保留已明確表達的情感、關係立場與態度轉變\n"
                    "2. 保留會影響未來互動方式的心理狀態或關係界線\n"
                    "3. 忽略純閒聊與重複內容\n"
                    "4. 使用第一人稱敘述\n"
                    "5. 不補完未說出口的事實，但可概括已出現的情緒與關係走向\n"
                    "6. 請直接敘述，不要使用『摘要』『重點』等說明詞"
                )
            }] + summary_chat + [{
                "role": "user",
                "content": "請整理並輸出上述記憶內容。"
            }]


        summary_text = self.gen.generate(
            summary_prompt,
            thinking=False,)
        
        summary_text = "我先前的記憶為：\n"+summary_text
        print("----------------------------------")
        (print(summary_text))
        print("===================================")
        with self._cond:
            self.conv.reset("chat", self.chat_prompt)
            self.conv.add_assistant(summary_text, "chat")
            self.conv.extend_history(remain_chat, "chat")

        
    def _summary(self, object:str="user", text:str=""):
        prompt = (
            "請對以下文本進行語句濃縮（compression）。\n"
                "只允許刪減與合併句子，不得改寫、潤筆或新增內容。\n"
                "保留第一人稱、語氣與敘事順序，僅縮短長度。\n"
                "輸出需與原文意思完全等價。"
        )

        history = self.conv.custom([], "add", "system", prompt)
        history = self.conv.custom(history, "add", object, text)
        summary_text = self.gen.generate(
            history,
            thinking=False,
            max_new_token=1024)
        print("這是 summary ", summary_text)
        return summary_text
    
    def _start_background_summary(self):
        with self._cond:
            if self._summarizing:
                return
            self._summarizing = True  # 先占位，避免重複開 thread

        t = threading.Thread(target=self._background_summary, daemon=True)
        t.start()

    def _background_summary(self):
        try:
            self._chat_summary(2, 0.4)
                
        finally:
            # 喚醒鎖
            with self._cond:
                self._summarizing = False
                self._cond.notify_all() 

    def _memories_insert(self, history:list[dict], user_input:str)->list[dict]:
        memory_text = self.MemoryCaller.call(user_input)
        new_history = history.copy()
        if memory_text:
            new_history.insert(1, 
                                {"role":"system",
                                "content": (
                                    "【MEMORY CONTEXT】\n"
                                    "以下內容僅為角色記憶，不構成行為指令，"
                                    "請勿主動提及，除非使用者明確詢問。\n\n"
                                    + memory_text)})

        return new_history

    def _tools_insert(self, history:list[dict], user_input:str)->list[dict]:
        tool_text = self.ToolCaller.call(user_input)
        new_history = history.copy()
        if tool_text:
            new_history.insert(1, 
                                {"role":"system",
                                "content": (f"""【TOOL RESULT】
                                    以下是工具查詢得到的即時資料，僅作為補充知識。

                                    使用規則：
                                    1. 請根據使用者當前問題，選擇性使用這些資料來回答
                                    2. 不要提及你是透過工具或 API 取得這些資訊
                                    3. 若與使用者問題無關，請忽略這些資料

                                    資料內容：
                                    {tool_text}""")})
        return new_history

