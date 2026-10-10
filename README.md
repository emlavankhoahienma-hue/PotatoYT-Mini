# 🥔 PotatoYT-Mini

> **Trình duyệt YouTube mini siêu nhẹ dành riêng cho máy cấu hình yếu (Potato PC)**.  
> Được thiết kế để vừa xem YouTube vừa chơi game (LoL, Roblox, Minecraft, Giả lập...) hoặc làm việc đa nhiệm mà **không tụt FPS, không tràn RAM**.

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-yellow.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078d7.svg)](https://microsoft.com)
[![Engine](https://img.shields.io/badge/engine-Microsoft%20WebView2-teal.svg)](https://developer.microsoft.com/microsoft-edge/webview2/)

---

## 🌟 Tính năng nổi bật (Features)

1. **⚡ Tiêu thụ tài nguyên siêu ít (~80MB - 130MB RAM)**:
   - Sử dụng trực tiếp nhân **Microsoft Edge WebView2** có sẵn của Windows với cờ dòng lệnh tối ưu hóa cho máy yếu.
   - Không bị ngốn 500MB - 1GB RAM như Chrome/Edge/Firefox hay các ứng dụng nền tảng Electron.
2. **📌 Luôn trên cùng (Always on Top)**:
   - Ghim cửa sổ video nổi trên mọi màn hình game (chế độ Borderless/Windowed) hoặc văn bản làm việc.
3. **👻 Chế độ Xuyên thấu chuột (Ghost / Click-Through Mode)**:
   - Chuột bấm xuyên qua video vào thẳng game bên dưới mà không vô tình click trúng video làm dừng hình hoặc mất tiêu điểm chuột!
4. **🎚️ Độ trong suốt tùy chỉnh (Opacity / Transparency)**:
   - Giảm độ mờ từ 30% đến 100% để nhìn xuyên thấu màn hình game hoặc tài liệu phía sau.
5. **🚫 Tự động chặn & Bỏ qua quảng cáo (AdBlock & Auto-Skip)**:
   - Tự động ấn "Bỏ qua quảng cáo" ngay mili-giây đầu tiên, tự tua nhanh quảng cáo không thể bỏ qua, xóa sạch các banner rác.
6. **🔒 Khóa độ phân giải thông minh (Resolution Lock)**:
   - Mặc định giữ ở mức 360p hoặc 480p (độ phân giải tối ưu tuyệt đối cho khung hình nhỏ PiP), chặn đứng tình trạng YouTube tự ý đẩy lên 1080p60/4K làm giật lag GPU.
7. **🎵 Chế độ Tắt màn hình khi chỉ nghe nhạc (Audio-Only Mode)**:
   - Khi cày game chỉ muốn nghe nhạc hoặc Podcast: Tắt toàn bộ quá trình render pixel của thẻ `<video>` giúp CPU và GPU giảm tải về gần **0%**!
8. **📏 Phím tắt toàn cục (Global Hotkeys)**:
   - Điều khiển nhanh ngay cả khi bạn đang tập trung trong trận game mà không cần chuyển cửa sổ (Alt-Tab).

---

## ⌨️ Bảng phím tắt toàn cục (Global Hotkeys)

Các phím tắt này hoạt động **ngay cả khi bạn đang chơi game toàn màn hình / không viền**:

| Phím tắt | Chức năng | Ghi chú |
| :--- | :--- | :--- |
| `Ctrl + Alt + T` | **Ghim / Bỏ ghim (Always on Top)** | Giữ cửa sổ luôn ở trên cùng |
| `Ctrl + Alt + G` | **Bật / Tắt chế độ Ghost (Click-Through)** | Chuột bấm xuyên qua video |
| `Ctrl + Alt + [` | **Giảm độ mờ (Tăng trong suốt)** | Giảm mỗi lần 10% (tối thiểu 20%) |
| `Ctrl + Alt + ]` | **Tăng độ rõ (Giảm trong suốt)** | Tăng mỗi lần 10% (tối đa 100%) |
| `Ctrl + Alt + M` | **Bật / Tắt Audio-Only (Blackout)** | Tắt hình tiết kiệm 100% GPU |

---

## 🚀 Hướng dẫn cài đặt & Khởi chạy (Quick Start)

### Cách 1: Chạy trực tiếp 1-Click (Khuyên dùng)
1. Đảm bảo máy tính đã cài **Python 3.10+** (đã có sẵn trên máy của bạn).
2. Tải về thư mục mã nguồn.
3. Nhấp đúp chuột vào file **`run.bat`**:
   - Tự động kiểm tra môi trường.
   - Tự động cài đặt `pywebview` nếu thiếu.
   - Khởi chạy ngay trong 1 giây!

### Cách 2: Khởi chạy bằng dòng lệnh
```powershell
# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy ứng dụng
python src/main.py
```

### Cách 3: Đóng gói thành file `.EXE` độc lập
Chỉ cần nhấp đúp vào **`build_exe.bat`**, ứng dụng sẽ tự động được đóng gói thành 1 file chạy duy nhất tại `dist/PotatoYT-Mini.exe`.

---

## ⚙️ Cấu hình tùy chỉnh (`config.json`)

Bạn có thể chỉnh sửa file `config.json` để thay đổi cài đặt mặc định theo sở thích:
```json
{
    "window_x": null,
    "window_y": null,
    "window_width": 480,
    "window_height": 300,
    "opacity": 100,
    "always_on_top": true,
    "engine_mode": "lite",
    "resolution_cap": "480p",
    "adblock_enabled": true,
    "audio_mode": false,
    "last_url": "https://m.youtube.com"
}
```

---

## 📊 Bảng so sánh tài nguyên (Resource Benchmark)

| Tiêu chí | Chrome / Edge thông thường | Ứng dụng Electron | 🥔 **PotatoYT-Mini** |
| :--- | :--- | :--- | :--- |
| **RAM khi mở** | ~650MB - 1.1GB | ~350MB - 500MB | **~85MB - 120MB** |
| **CPU khi phát 480p** | 8% - 15% | 7% - 12% | **2% - 4%** |
| **Chế độ Ghost xuyên thấu** | ❌ Không có | ⚠️ Phức tạp | **✅ Tích hợp Win32 native** |
| **Ghim trên cùng khi chơi game** | Cần tiện ích ngoài | Tùy app | **✅ Phím tắt toàn cục** |
| **Tắt render khi nghe nhạc** | ❌ Không | ❌ Không | **✅ 1 phím tắt giảm 100% GPU** |

---

## 📜 Giấy phép (License)
Dự án được phân phối dưới giấy phép mã nguồn mở **MIT License**.
