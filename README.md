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
