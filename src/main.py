"""
PotatoYT-Mini - Ultra-Lightweight Mini YouTube Browser for Potato PCs
Designed for smooth multitasking, gaming, and low-resource environments.
"""

import os
import sys
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from security import get_secure_user_data_dir, is_safe_url

# Apply potato PC Edge flags before any webview import with secure isolated profile
POTATO_BROWSER_FLAGS = (
    f'--user-data-dir="{get_secure_user_data_dir()}" '
    "--disable-background-networking "
    "--disable-component-update "
    "--disable-extensions "
    "--renderer-process-limit=1 "
    "--enable-features=VaapiVideoDecoder,AudioServiceSandbox,CanvasOopRasterization "
    "--disable-features=TranslateUI,MediaEngagementBypassAutoplayPolicies "
    "--force-dark-mode "
    "--autoplay-policy=no-user-gesture-required"
)
os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = POTATO_BROWSER_FLAGS

import webview
from config_manager import ConfigManager
from win32_native import Win32Controller

APP_TITLE = "PotatoYT Mini Player"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class PotatoAPI:
    """JS Bridge exposed to the webview frontend."""
    def __init__(self, app_controller):
        self._app = app_controller

    def toggle_pin(self) -> bool:
        return bool(self._app.toggle_pin())

    def toggle_ghost(self) -> bool:
        return bool(self._app.toggle_ghost())

    def adjust_opacity(self, delta):
        try:
            delta_val = int(delta)
        except (ValueError, TypeError):
            return False
        return self._app.adjust_opacity(delta_val)

    def set_opacity_direct(self, val) -> bool:
        try:
            opacity_val = max(20, min(100, int(val)))
            self._app.win32.set_opacity(opacity_val)
            self._app.config.set("opacity", opacity_val)
            return True
        except (ValueError, TypeError):
            return False

    def set_resolution(self, res_cap: str) -> bool:
        if not isinstance(res_cap, str) or res_cap not in ("360p", "480p", "720p", "auto"):
            return False
        self._app.config.set("resolution_cap", res_cap)
        return True

    def set_audio_mode(self, enabled) -> bool:
        self._app.config.set("audio_mode", bool(enabled))
        return True

    def resize_preset(self, width, height) -> bool:
        try:
            w = int(width)
            h = int(height)
            if 200 <= w <= 3840 and 150 <= h <= 2160:
                self._app.resize_window(w, h)
                return True
        except (ValueError, TypeError):
            pass
        return False

    def navigate_to(self, url: str) -> bool:
        if not is_safe_url(url):
            print(f"[PotatoYT] Blocked navigation to untrusted URL: {url}")
            return False
        if self._app.window:
            self._app.window.load_url(url)
            self._app.config.set("last_url", url)
            return True
        return False

    def go_home(self):
        if self._app.window:
            self._app.window.load_url("https://m.youtube.com")


class PotatoApp:
    def __init__(self):
        self.config = ConfigManager(os.path.join(BASE_DIR, "..", "config.json"))
        self.win32 = Win32Controller(APP_TITLE)
        self.window = None
        self.api = PotatoAPI(self)

        # Read injection files
        with open(os.path.join(ASSETS_DIR, "inject.css"), "r", encoding="utf-8") as f:
            self.css_content = f.read()

        with open(os.path.join(ASSETS_DIR, "inject.js"), "r", encoding="utf-8") as f:
            self.js_content = f.read()

    def on_loaded(self):
        """Called when WebView finishes loading a page."""
        # Inject custom styles & engine script
        try:
            self.window.load_css(self.css_content)
            self.window.evaluate_js(self.js_content)
        except Exception as e:
            print(f"[PotatoYT] Injection warning: {e}")

        # Update HUD to current settings
        is_pin = self.config.get("always_on_top", True)
        opacity = self.config.get("opacity", 100)
        self.sync_hud_state(pinned=is_pin, opacity=opacity)

    def init_native_window(self):
        """Finds the native HWND and configures Win32 properties."""
        print("[PotatoYT] Locating native window handle...")
        if self.win32.find_window(max_retries=25, delay=0.4):
            print(f"[PotatoYT] HWND found: {self.win32.hwnd}")

            # Apply Always-on-top from config
            if self.config.get("always_on_top", True):
                self.win32.set_always_on_top(True)

            # Apply Opacity from config
            saved_opacity = self.config.get("opacity", 100)
            self.win32.set_opacity(saved_opacity)

            # Register Global Hotkeys
            self.win32.start_global_hotkeys({
                "toggle_pin": self.toggle_pin,
                "toggle_ghost": self.toggle_ghost,
                "opacity_down": lambda: self.adjust_opacity(-10),
                "opacity_up": lambda: self.adjust_opacity(10),
                "toggle_audio": self.toggle_audio_mode
            })
            print("[PotatoYT] Global Hotkeys registered: Ctrl+Alt+T, Ctrl+Alt+G, Ctrl+Alt+[, Ctrl+Alt+], Ctrl+Alt+M")
        else:
            print("[PotatoYT] Notice: Native HWND not acquired. Hotkeys will run in window context.")

    def sync_hud_state(self, pinned=None, ghost=None, opacity=None, audio=None):
        """Dispatches state updates to webview frontend HUD with injection sanitization."""
        if not self.window:
            return
        try:
            if pinned is not None:
                safe_pinned = "true" if bool(pinned) else "false"
                self.window.evaluate_js(f"window.potato_update_pin({safe_pinned})")
            if ghost is not None:
                safe_ghost = "true" if bool(ghost) else "false"
                self.window.evaluate_js(f"window.potato_update_ghost({safe_ghost})")
            if opacity is not None:
                try:
                    safe_opacity = max(20, min(100, int(opacity)))
                except (ValueError, TypeError):
                    safe_opacity = 100
                self.window.evaluate_js(f"window.potato_update_opacity({safe_opacity})")
            if audio is not None:
                safe_audio = "true" if bool(audio) else "false"
                self.window.evaluate_js(f"window.potato_update_audio({safe_audio})")
        except Exception:
            pass

    def toggle_pin(self):
        new_state = self.win32.toggle_always_on_top()
        self.config.set("always_on_top", new_state)
        self.sync_hud_state(pinned=new_state)
        return new_state

    def toggle_ghost(self):
        new_state = self.win32.toggle_click_through()
        self.sync_hud_state(ghost=new_state)
        return new_state

    def adjust_opacity(self, delta):
        new_percent = self.win32.adjust_opacity(delta)
        self.config.set("opacity", new_percent)
        self.sync_hud_state(opacity=new_percent)
        return new_percent

    def toggle_audio_mode(self):
        current = self.config.get("audio_mode", False)
        new_state = not current
        self.config.set("audio_mode", new_state)
        self.sync_hud_state(audio=new_state)
        return new_state

    def resize_window(self, width, height):
        if self.window:
            self.window.resize(width, height)
            self.config.set("window_width", width)
            self.config.set("window_height", height)

    def on_closing(self):
        """Cleanup before window closes (batched config write)."""
        self.win32.stop()
        if self.window:
            try:
                self.config.set("window_width", self.window.width, auto_save=False)
                self.config.set("window_height", self.window.height, auto_save=False)
                self.config.set("window_x", self.window.x, auto_save=False)
                self.config.set("window_y", self.window.y, auto_save=False)
            except Exception:
                pass
        self.config.save()

    def run(self):
        w = self.config.get("window_width", 480)
        h = self.config.get("window_height", 300)
        x = self.config.get("window_x", None)
        y = self.config.get("window_y", None)
        start_url = self.config.get("last_url", "https://m.youtube.com")

        self.window = webview.create_window(
            title=APP_TITLE,
            url=start_url,
            js_api=self.api,
            width=w,
            height=h,
            x=x,
            y=y,
            resizable=True,
            easy_drag=True,
            background_color="#0b0f14"
        )

        self.window.events.loaded += self.on_loaded
        self.window.events.closing += self.on_closing

        # Launch native win32 thread
        threading.Thread(target=self.init_native_window, daemon=True).start()

        print("[PotatoYT] Starting lightweight WebView2 engine...")
        webview.start(debug=False, gui="edgechromium")


if __name__ == "__main__":
    app = PotatoApp()
    app.run()
