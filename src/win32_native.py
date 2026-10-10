"""
PotatoYT-Mini - Native Windows 32 Integration via ctypes
Provides zero-overhead window controls: Always-on-top, Opacity,
Click-through (Ghost mode), and Global Hotkeys for gaming/multitasking.
"""

import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_SHOWWINDOW = 0x0040

LWA_ALPHA = 0x00000002

# Hotkey modifiers
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312

# Virtual key codes
VK_OEM_4 = 0xDB  # '[' key
VK_OEM_6 = 0xDD  # ']' key


class Win32Controller:
    def __init__(self, window_title: str):
        self.window_title = window_title
        self.hwnd = None
        self.is_topmost = False
        self.opacity = 255  # 0 to 255
        self.is_ghost = False  # Click-through mode
        self.hotkey_thread = None
        self._running = False
        self.hotkey_callbacks = {}

    def find_window(self, max_retries: int = 25, delay: float = 0.4) -> bool:
        """Locates the HWND for the application window by title, or by matching process ID."""
        for _ in range(max_retries):
            hwnd = user32.FindWindowW(None, self.window_title)
            if hwnd:
                self.hwnd = hwnd
                return True

            # Fallback: Enumerate windows for this process
            current_pid = kernel32.GetCurrentProcessId()

            def enum_cb(h, _):
                if user32.IsWindowVisible(h):
                    pid = wintypes.DWORD()
                    user32.GetWindowThreadProcessId(h, ctypes.byref(pid))
                    if pid.value == current_pid:
                        length = user32.GetWindowTextLengthW(h)
                        if length > 0:
                            buff = ctypes.create_unicode_buffer(length + 1)
                            user32.GetWindowTextW(h, buff, length + 1)
                            title = buff.value
                            if self.window_title in title or "PotatoYT" in title:
                                self.hwnd = h
                                return False
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            cb_func = WNDENUMPROC(enum_cb)
            user32.EnumWindows(cb_func, 0)
            if self.hwnd:
                return True

            time.sleep(delay)
        return False

    def set_always_on_top(self, enable: bool) -> bool:
        """Pins or unpins the window to stay on top of all other windows."""
        if not self.hwnd:
            return False
        self.is_topmost = bool(enable)
        flag = HWND_TOPMOST if self.is_topmost else HWND_NOTOPMOST
        result = user32.SetWindowPos(
            self.hwnd,
            flag,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        )
        return bool(result)

    def toggle_always_on_top(self) -> bool:
        return self.set_always_on_top(not self.is_topmost)

    def set_opacity(self, alpha_percent: int) -> bool:
        """
        Sets window transparency.
        alpha_percent: 20 to 100
        """
        if not self.hwnd:
            return False
        try:
            val = int(alpha_percent)
        except (ValueError, TypeError):
            val = 100
        clamped = max(20, min(100, val))
        alpha = int((clamped / 100.0) * 255)
        self.opacity = alpha

        # Ensure WS_EX_LAYERED is set
        ex_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)

        result = user32.SetLayeredWindowAttributes(self.hwnd, 0, alpha, LWA_ALPHA)
        return bool(result)

    def adjust_opacity(self, delta_percent: int) -> int:
        """Increases or decreases opacity by delta (e.g. +10 or -10)."""
        try:
            delta = int(delta_percent)
        except (ValueError, TypeError):
            delta = 0
        current_percent = int((self.opacity / 255.0) * 100)
        new_percent = max(20, min(100, current_percent + delta))
        self.set_opacity(new_percent)
        return new_percent

    def set_click_through(self, enable: bool) -> bool:
        """
        Ghost Mode: When enabled, all mouse clicks pass straight through
        the window to the underlying game or application.
        """
        if not self.hwnd:
            return False
        self.is_ghost = enable
        ex_style = user32.GetWindowLongW(self.hwnd, GWL_EXSTYLE)
        
        # Must have WS_EX_LAYERED
        ex_style |= WS_EX_LAYERED

        if enable:
            new_style = ex_style | WS_EX_TRANSPARENT
        else:
            new_style = ex_style & ~WS_EX_TRANSPARENT

        user32.SetWindowLongW(self.hwnd, GWL_EXSTYLE, new_style)
        return True

    def toggle_click_through(self) -> bool:
        return self.set_click_through(not self.is_ghost)

    def start_global_hotkeys(self, callbacks: dict):
        """
        Starts a message loop in a background thread to listen for global hotkeys.
        callbacks mapping:
        - 'toggle_pin': func
        - 'toggle_ghost': func
        - 'opacity_down': func
        - 'opacity_up': func
        - 'toggle_audio': func
        """
        self.hotkey_callbacks = callbacks
        self._running = True
        self.hotkey_thread = threading.Thread(target=self._hotkey_loop, daemon=True)
        self.hotkey_thread.start()

    def _hotkey_loop(self):
        # Register Hotkeys on thread message queue
        # ID 1: Ctrl + Alt + T -> Toggle Pin
        # ID 2: Ctrl + Alt + G -> Toggle Ghost (Click-Through)
        # ID 3: Ctrl + Alt + [ -> Decrease Opacity
        # ID 4: Ctrl + Alt + ] -> Increase Opacity
        # ID 5: Ctrl + Alt + M -> Toggle Audio-Only / Screen-Off

        user32.RegisterHotKey(None, 1, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, ord('T'))
        user32.RegisterHotKey(None, 2, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, ord('G'))
        user32.RegisterHotKey(None, 3, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_OEM_4)
        user32.RegisterHotKey(None, 4, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, VK_OEM_6)
        user32.RegisterHotKey(None, 5, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, ord('M'))

        msg = wintypes.MSG()
        while self._running:
            # Check for message
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):  # PM_REMOVE = 1
                if msg.message == WM_HOTKEY:
                    hotkey_id = msg.wParam
                    cb_key = {
                        1: 'toggle_pin',
                        2: 'toggle_ghost',
                        3: 'opacity_down',
                        4: 'opacity_up',
                        5: 'toggle_audio'
                    }.get(hotkey_id)
                    if cb_key and cb_key in self.hotkey_callbacks:
                        try:
                            self.hotkey_callbacks[cb_key]()
                        except Exception as e:
                            print(f"[Win32] Error in hotkey callback '{cb_key}': {e}")
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.02)

        # Cleanup
        for i in range(1, 6):
            user32.UnregisterHotKey(None, i)

    def stop(self):
        self._running = False
