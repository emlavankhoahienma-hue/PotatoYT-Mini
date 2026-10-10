"""
PotatoYT-Mini - Security & Data Protection Module
Provides Windows DPAPI military-grade encryption for sensitive data,
URL safety whitelisting, origin protection, and secure profile isolation.
"""

import os
import sys
import base64
import ctypes
from ctypes import wintypes
from urllib.parse import urlparse

# Win32 Crypt32 and Kernel32 setup
crypt32 = ctypes.windll.crypt32
kernel32 = ctypes.windll.kernel32


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]


def encrypt_data(data: bytes) -> str:
    """Encrypts raw bytes using Windows Data Protection API (DPAPI)."""
    if not data:
        return ""
    blob_in = DATA_BLOB(
        len(data),
        ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte))
    )
    blob_out = DATA_BLOB()
    # CRYPTPROTECT_UI_FORBIDDEN = 0x1
    if not crypt32.CryptProtectData(ctypes.byref(blob_in), "PotatoYT_Protected", None, None, None, 0x1, ctypes.byref(blob_out)):
        raise ctypes.WinError()
    encrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    kernel32.LocalFree(blob_out.pbData)
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_data(b64_cipher: str) -> bytes:
    """Decrypts DPAPI-encrypted base64 string back to raw bytes."""
    if not b64_cipher:
        return b""
    try:
        raw = base64.b64decode(b64_cipher)
        blob_in = DATA_BLOB(
            len(raw),
            ctypes.cast(ctypes.create_string_buffer(raw), ctypes.POINTER(ctypes.c_byte))
        )
        blob_out = DATA_BLOB()
        if not crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0x1, ctypes.byref(blob_out)):
            raise ctypes.WinError()
        decrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        kernel32.LocalFree(blob_out.pbData)
        return decrypted
    except Exception as e:
        print(f"[Security] Decryption warning: {e}")
        return b""


def encrypt_string(plain_text: str) -> str:
    """Helper to encrypt string to DPAPI-secured base64."""
    if not plain_text:
        return ""
    return encrypt_data(plain_text.encode("utf-8"))


def decrypt_string(b64_cipher: str) -> str:
    """Helper to decrypt DPAPI-secured base64 back to string."""
    if not b64_cipher:
        return ""
    raw = decrypt_data(b64_cipher)
    return raw.decode("utf-8", errors="ignore")


# =========================================================================
# URL Safety & Anti-Phishing Guard
# =========================================================================

ALLOWED_HOST_SUFFIXES = (
    "youtube.com",
    "youtu.be",
    "google.com",
    "googlevideo.com",
    "ytimg.com",
    "gstatic.com",
    "ggpht.com"
)


def is_safe_url(url: str) -> bool:
    """
    Verifies that a URL points to legitimate YouTube or Google services.
    Blocks file://, javascript:, data:, vbscript:, and untrusted third-party redirects.
    """
    if not isinstance(url, str):
        return False

    trimmed = url.strip()
    if not trimmed:
        return False

    # Block local file execution and script pseudo-protocols
    lower = trimmed.lower()
    dangerous_schemes = ("file:", "javascript:", "data:", "vbscript:", "ms-appx:", "shell:", "powershell:")
    for scheme in dangerous_schemes:
        if lower.startswith(scheme):
            return False

    try:
        parsed = urlparse(trimmed)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False

        # Check if hostname matches or ends with allowed domain suffixes
        for allowed in ALLOWED_HOST_SUFFIXES:
            if hostname == allowed or hostname.endswith("." + allowed):
                return True

        return False
    except Exception:
        return False


def get_secure_user_data_dir() -> str:
    """
    Returns an isolated User Data Directory in LocalAppData to store
    encrypted cache, cookies, and local storage, separate from project files.
    """
    local_app_data = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    secure_dir = os.path.join(local_app_data, "PotatoYT-Mini", "UserData")
    os.makedirs(secure_dir, exist_ok=True)
    return secure_dir
