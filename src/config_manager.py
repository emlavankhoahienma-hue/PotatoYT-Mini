"""
PotatoYT-Mini - Config Manager
Handles persistent settings (window size, position, opacity, quality cap, etc.)
"""

import json
import os
from typing import Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "window_x": None,
    "window_y": None,
    "window_width": 480,
    "window_height": 300,
    "opacity": 100,
    "always_on_top": True,
    "engine_mode": "lite",          # 'lite' (m.youtube.com), 'pure' (embed), 'desktop'
    "resolution_cap": "480p",       # '360p', '480p', '720p', 'auto'
    "adblock_enabled": True,
    "audio_mode": False,
    "last_url": "https://m.youtube.com"
}


class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config.update(data)
            except Exception as e:
                print(f"[Config] Error loading config: {e}. Using defaults.")
        return self.config

    def save(self) -> bool:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Config] Error saving config: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True):
        self.config[key] = value
        if auto_save:
            self.save()
