from pathlib import Path

class HistoryRecorder:
    def __init__(self,
                 base_folder_path:str=None,
                 ):
        self.base_folder_path = Path(
            base_folder_path
            if base_folder_path is not None
            else Path(__file__).resolve().parent.parent
            )  

        self.set_path("prior_conversation")
        
    def set_path(self, name:str, path:str=None):
        if name=="persona_event":
            if path is None:
                self.persona_path = self.base_folder_path/"memories"/"persona"/"event.json"
            else: 
                self.persona_path = path
                
        if name=="prior_conversation":
            if path is None:
                self.conversation_path = self.base_folder_path/"historyRecorder"/"prior_conversation.json"
            else:
                self.conversation_path = path
    
    def load(self, name: str):
        """
        讀取指定紀錄，回傳 Python 物件
        檔案不存在 → 回傳空結構
        """
        path = self._get_path(name)

        if not path.exists():
            # prior_conversation 預設是 list
            if name == "prior_conversation":
                return []
            # persona_event 預設是 dict
            if name == "persona_event":
                return {}

            return None

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def write(self, name: str, data):
        """
        將資料寫入指定紀錄（直接覆蓋）
        """
        path = self._get_path(name)

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # =========================
    # internal helper
    # =========================

    def _get_path(self, name: str) -> Path:
        if name == "prior_conversation":
            return self.conversation_path
        if name == "persona_event":
            return self.persona_path

        raise ValueError(f"Unknown record name: {name}")