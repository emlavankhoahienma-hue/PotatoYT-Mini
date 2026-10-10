"""
Senior QA & Security Automation Test Suite for PotatoYT-Mini
Tests edge cases, input hygiene, security injection vectors, and resilience.
"""

import os
import sys
import json
import tempfile
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config_manager import ConfigManager, DEFAULT_CONFIG
from win32_native import Win32Controller
from main import PotatoApp, PotatoAPI


class MockWindow:
    def __init__(self):
        self.evaluated = []
        self.width = 480
        self.height = 300
        self.x = 100
        self.y = 100

    def evaluate_js(self, js):
        self.evaluated.append(js)

    def resize(self, w, h):
        self.width = w
        self.height = h


class TestConfigManagerQA(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_corrupt_json_file(self):
        """Test how ConfigManager handles a corrupted JSON file."""
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            f.write("{corrupt json, not valid")

        cfg = ConfigManager(self.temp_file.name)
        self.assertEqual(cfg.get("resolution_cap"), "480p")
        self.assertEqual(cfg.get("always_on_top"), True)

    def test_non_dict_json_payload(self):
        """Test how ConfigManager handles JSON that contains a list or string instead of a dict."""
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            f.write('["item1", "item2"]')

        cfg = ConfigManager(self.temp_file.name)
        self.assertEqual(cfg.get("resolution_cap"), "480p")

    def test_null_json_payload(self):
        """Test how ConfigManager handles JSON containing null."""
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            f.write('null')

        cfg = ConfigManager(self.temp_file.name)
        self.assertEqual(cfg.get("resolution_cap"), "480p")

    def test_boundary_values_and_sanitization(self):
        """Test config values out of range are sanitized and clamped."""
        cfg = ConfigManager(self.temp_file.name)
        cfg.set("opacity", 999)
        self.assertEqual(cfg.get("opacity"), 100)

        cfg.set("opacity", -50)
        self.assertEqual(cfg.get("opacity"), 20)

        cfg.set("window_width", -500)
        self.assertEqual(cfg.get("window_width"), 200)

        cfg.set("resolution_cap", "invalid_8k")
        self.assertEqual(cfg.get("resolution_cap"), "480p")


class TestWin32ControllerQA(unittest.TestCase):
    def setUp(self):
        self.controller = Win32Controller("NonExistentWindow_123456")

    def test_adjust_opacity_boundary(self):
        """Test opacity boundaries (20% to 100%)."""
        self.controller.opacity = 255 # 100%
        new_val = self.controller.adjust_opacity(-90)
        self.assertGreaterEqual(new_val, 20)

        new_val = self.controller.adjust_opacity(100)
        self.assertLessEqual(new_val, 100)

    def test_adjust_opacity_invalid_type(self):
        """Ensure adjust_opacity handles non-integer input gracefully."""
        res = self.controller.adjust_opacity("invalid")
        self.assertIsInstance(res, int)

    def test_non_existent_window_graceful_handling(self):
        """Ensure native methods return False gracefully when HWND is None."""
        self.assertFalse(self.controller.set_always_on_top(True))
        self.assertFalse(self.controller.set_opacity(50))
        self.assertFalse(self.controller.set_click_through(True))


class TestSecurityAndInputHygiene(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.app = PotatoApp()
        self.app.config = ConfigManager(self.temp_file.name)
        self.app.window = MockWindow()
        self.api = PotatoAPI(self.app)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_api_adjust_opacity_invalid_type(self):
        """Test sending non-integer to adjust_opacity (Injection & type crash check)."""
        res = self.api.adjust_opacity("'); alert('XSS');//")
        self.assertFalse(res)

        res2 = self.api.adjust_opacity(10)
        self.assertIsInstance(res2, int)

    def test_api_resize_preset_negative_dimensions(self):
        """Test sending invalid dimensions to resize_preset."""
        res1 = self.api.resize_preset(-500, -500)
        self.assertFalse(res1)

        res2 = self.api.resize_preset("invalid", "invalid")
        self.assertFalse(res2)

        res3 = self.api.resize_preset(480, 300)
        self.assertTrue(res3)

    def test_api_set_resolution_invalid(self):
        """Test setting invalid resolution cap."""
        res = self.api.set_resolution("invalid_8k_res")
        self.assertFalse(res)

        res_ok = self.api.set_resolution("720p")
        self.assertTrue(res_ok)
        self.assertEqual(self.app.config.get("resolution_cap"), "720p")

    def test_sync_hud_state_injection_prevention(self):
        """Test that malicious payloads cannot be injected into evaluate_js calls."""
        # Attempt JS injection via opacity
        self.app.sync_hud_state(opacity="100); alert('PWNED');//")
        last_call = self.app.window.evaluated[-1]
        self.assertNotIn("alert", last_call)
        self.assertIn("window.potato_update_opacity(100)", last_call)

        # Attempt JS injection via pin
        self.app.sync_hud_state(pinned="true; evil();//")
        last_pin_call = self.app.window.evaluated[-1]
        self.assertNotIn("evil", last_pin_call)
        self.assertIn("window.potato_update_pin(true)", last_pin_call)


if __name__ == "__main__":
    unittest.main()
