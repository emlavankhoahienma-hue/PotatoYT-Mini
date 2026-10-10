"""
PotatoYT-Mini - Config Manager
Handles persistent settings (window size, position, opacity, quality cap, etc.)
"""

import json
import os
from typing import Dict, Any

try:
    from security import is_safe_url, encrypt_string, decrypt_string
except ImportError:
    try:
        from src.security import is_safe_url, encrypt_string, decrypt_string
    except ImportError:
        def is_safe_url(u): return isinstance(u, str) and (u.startswith("https://m.youtube.com") or u.startswith("https://www.youtube.com"))
        def encrypt_string(s): return s
        def decrypt_string(s): return s

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

    def _validate_value(self, key: str, value: Any) -> Any:
        """Sanitizes and validates individual configuration settings."""
        if key == "window_width":
            try:
                val = int(value)
                return max(200, min(3840, val))
            except (ValueError, TypeError):
                return DEFAULT_CONFIG["window_width"]
        elif key == "window_height":
            try:
                val = int(value)
                return max(150, min(2160, val))
            except (ValueError, TypeError):
                return DEFAULT_CONFIG["window_height"]
        elif key == "opacity":
            try:
                val = int(value)
                return max(20, min(100, val))
            except (ValueError, TypeError):
                return DEFAULT_CONFIG["opacity"]
        elif key in ("always_on_top", "adblock_enabled", "audio_mode"):
            return bool(value)
        elif key == "engine_mode":
            return value if value in ("lite", "pure", "desktop") else DEFAULT_CONFIG["engine_mode"]
        elif key == "resolution_cap":
            return value if value in ("360p", "480p", "720p", "auto") else DEFAULT_CONFIG["resolution_cap"]
        elif key == "last_url":
            if isinstance(value, str) and is_safe_url(value):
                return value
            return DEFAULT_CONFIG["last_url"]
        elif key in ("window_x", "window_y"):
            if value is None:
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        return value

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if k in DEFAULT_CONFIG:
                                self.config[k] = self._validate_value(k, v)
                    else:
                        print(f"[Config] Non-dictionary data in {self.config_path}. Using defaults.")
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
        self.config[key] = self._validate_value(key, value)
        if auto_save:
            self.save()

    def set_secure(self, key: str, value: str, auto_save: bool = True):
        """Stores a sensitive value encrypted with Windows DPAPI."""
        encrypted_val = encrypt_string(str(value))
        self.config[f"_sec_{key}"] = encrypted_val
        if auto_save:
            self.save()

    def get_secure(self, key: str, default: str = "") -> str:
        """Retrieves and decrypts a DPAPI-protected value."""
        enc = self.config.get(f"_sec_{key}", "")
        if not enc:
            return default
        dec = decrypt_string(enc)
        return dec if dec else default

