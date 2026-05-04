from __future__ import annotations

from pathlib import Path

from utils.ffmpeg_helper import resolve_binary, run_cmd


class AudioManager:
    def __init__(self, on_log):
        self.on_log = on_log
        self.ffmpeg = resolve_binary("ffmpeg")

    def extract(self, video: Path, audio_out: Path) -> None:
        run_cmd([self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vn", "-acodec", "copy", str(audio_out)], self.on_log)

    def mux(self, video: Path, audio: Path, output: Path) -> None:
        try:
            run_cmd([self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-i", str(audio), "-c:v", "copy", "-c:a", "aac", str(output)], self.on_log)
        except RuntimeError:
            run_cmd([self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-i", str(audio), "-c:v", "libx264", "-c:a", "aac", str(output)], self.on_log)
