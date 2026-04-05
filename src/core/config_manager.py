import json
import os
import sys
import shutil
from typing import List, Dict, Optional

def get_app_path():
    """获取应用程序目录路径。"""
    if getattr(sys, 'frozen', False):
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        path = os.path.join(base, "WinStart")
        os.makedirs(path, exist_ok=True)
        return path
    # 开发环境下，回到项目根目录
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_FILE = os.path.join(get_app_path(), "data.json")

class ConfigManager:
    def __init__(self):
        self.data_file = DATA_FILE
        self.legacy_data_file = os.path.join(os.path.dirname(sys.executable), "data.json") if getattr(sys, 'frozen', False) else None
        if self.legacy_data_file and (not os.path.exists(self.data_file)) and os.path.exists(self.legacy_data_file):
            try:
                shutil.copy2(self.legacy_data_file, self.data_file)
            except OSError:
                pass
        self.data = self._load_data()
        self._ensure_three_slots()

    def _load_data(self) -> Dict:
        if not os.path.exists(self.data_file):
            return {"slots": []}
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"slots": []}

    def _ensure_three_slots(self):
        """确保有 3 个固定卡槽。"""
        slots = self.data.get("slots", [])
        while len(slots) < 3:
            slots.append({
                "id": f"slot_{len(slots)}",
                "name": f"卡槽 {len(slots) + 1}",
                "items": []
            })
        self.data["slots"] = slots[:3]
        self._save_data()

    def _save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def get_slots(self) -> List[Dict]:
        return self.data.get("slots", [])

    def update_slot_name(self, slot_id: str, name: str):
        for slot in self.data.get("slots", []):
            if slot["id"] == slot_id:
                slot["name"] = name
                self._save_data()
                return

    def add_item(self, slot_id: str, name: str, path: str, args: str = "", delay: int = 0):
        for slot in self.data.get("slots", []):
            if slot["id"] == slot_id:
                import uuid
                new_item = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "path": path,
                    "args": args,
                    "delay": delay,
                    "enabled": True
                }
                slot.setdefault("items", []).append(new_item)
                self._save_data()
                return new_item
        return None

    def delete_item(self, slot_id: str, item_id: str):
        for slot in self.data.get("slots", []):
            if slot["id"] == slot_id:
                slot["items"] = [i for i in slot.get("items", []) if i["id"] != item_id]
                self._save_data()
                return

    def update_item(self, slot_id: str, item_id: str, name: str, path: str, args: str, delay: int):
        for slot in self.data.get("slots", []):
            if slot["id"] == slot_id:
                for item in slot.get("items", []):
                    if item["id"] == item_id:
                        item["name"] = name
                        item["path"] = path
                        item["args"] = args
                        item["delay"] = delay
                        item.setdefault("enabled", True)
                        self._save_data()
                        return

    def toggle_item_enabled(self, slot_id: str, item_id: str, enabled: bool):
        for slot in self.data.get("slots", []):
            if slot["id"] == slot_id:
                for item in slot.get("items", []):
                    if item["id"] == item_id:
                        item["enabled"] = enabled
                        self._save_data()
                        return

    def reorder_items(self, slot_id: str, new_order_ids: List[str]):
        for slot in self.data.get("slots", []):
            if slot["id"] == slot_id:
                current_items = {item["id"]: item for item in slot.get("items", [])}
                new_items = []
                for item_id in new_order_ids:
                    if item_id in current_items:
                        new_items.append(current_items[item_id])
                slot["items"] = new_items
                self._save_data()
                return
