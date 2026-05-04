# Auto Video Shuffle + Image Compositor (PySide6 + FFmpeg)

## Chạy local

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
python main.py
```

## Build portable EXE

```bash
pyinstaller --noconfirm --onedir --windowed main.py \
  --add-binary "bin/ffmpeg.exe;bin" \
  --add-binary "bin/ffprobe.exe;bin"
```

> Đặt `ffmpeg.exe` và `ffprobe.exe` vào thư mục `bin/` trước khi build.

## Khắc phục lỗi `[WinError 2] The system cannot find the file specified`

App sẽ tìm `ffmpeg(.exe)` theo thứ tự:
1. `dist/main/bin/ffmpeg.exe` (PyInstaller)
2. `bin/ffmpeg.exe` cạnh source code
3. `PATH` hệ thống

Nếu vẫn lỗi, hãy kiểm tra:
- có tồn tại file `ffmpeg.exe` thực sự (không chỉ shortcut),
- antivirus không chặn file exe,
- đường dẫn không chứa ký tự bất thường do copy/paste.

Trong code mới, tên thư mục tạm đã được rút gọn/an toàn để tránh lỗi đường dẫn quá dài trên Windows.
