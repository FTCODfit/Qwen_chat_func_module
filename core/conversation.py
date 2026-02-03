class Conversation:
    def __init__(self):
        self.chat_history = []
        self.summary_history = []
        self.memory_history = []

    def _get_history(self, target):
        if target == "chat":
            return self.chat_history
        if target == "summary":
            return self.summary_history
        if target == "memory":
            return self.memory_history
        raise ValueError(f"Unknown history target: {target}")

    def add_system(self, content, target="chat"):
        self._get_history(target).append({
            "role": "system",
            "content": content
        })

    def add_user(self, content, target="chat"):
        self._get_history(target).append({
            "role": "user",
            "content": content
        })

    def add_assistant(self, content, target="chat"):
        self._get_history(target).append({
            "role": "assistant",
            "content": content
        })

    def reset(self, target="summary", sys_prompt=""):
        self._get_history(target).clear()
        if sys_prompt:
            self.add_system(sys_prompt, target)

    def get(self, target="chat"):
        return self._get_history(target)
    
    def extend_history(self, history, target="chat"):
        self._get_history(target).extend(history)

    def custom(self, history, operate="add", object="user",  content=""):
        if operate=="add":
            history.append({
                "role": object,
                "content": content})
        elif operate=="reset":
            history.clear()
            history.append({
                "role": "system",
                "content": content})
        
        elif operate=="extend":
            history.extend(content)
        
        return history
        