"""
Verification script for PotatoYT-Mini components.
"""
import os
import sys

# Ensure src is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

def test_config():
    from config_manager import ConfigManager
    cfg = ConfigManager(os.path.join(BASE_DIR, "config.json"))
    assert cfg.get("resolution_cap") == "480p", "Default resolution_cap should be 480p"
    assert cfg.get("always_on_top") is True, "Default always_on_top should be True"
    print("[PASS] ConfigManager tests passed!")

def test_win32_native():
    from win32_native import Win32Controller
    controller = Win32Controller("Test Title")
    assert controller.opacity == 255
    assert controller.is_topmost is False
    assert controller.is_ghost is False
    print("[PASS] Win32Controller unit tests passed!")

def test_assets():
    assets_dir = os.path.join(BASE_DIR, "src", "assets")
    css_path = os.path.join(assets_dir, "inject.css")
    js_path = os.path.join(assets_dir, "inject.js")
    assert os.path.exists(css_path), "inject.css must exist"
    assert os.path.exists(js_path), "inject.js must exist"
    assert os.path.getsize(css_path) > 100, "inject.css must not be empty"
    assert os.path.getsize(js_path) > 100, "inject.js must not be empty"
    print("[PASS] Assets existence and integrity tests passed!")

if __name__ == "__main__":
    print("[*] Running PotatoYT-Mini Component Verification...")
    test_config()
    test_win32_native()
    test_assets()
    print("[OK] ALL COMPONENT TESTS PASSED SUCCESSFULLY!")
