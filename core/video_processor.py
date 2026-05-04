from __future__ import annotations

from pathlib import Path

from utils.ffmpeg_helper import resolve_binary, run_cmd


class VideoProcessor:
    def __init__(self, on_log):
        self.on_log = on_log
        self.ffmpeg = resolve_binary("ffmpeg")

    def cut_segments(self, input_video: Path, scenes: list[tuple[float, float]], out_dir: Path) -> list[Path]:
        segments: list[Path] = []
        if not scenes:
            out = out_dir / "seg_000.mp4"
            run_cmd([self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(input_video), "-c", "copy", str(out)], self.on_log, step="Create segment")
            return [out]
        for idx, (start, end) in enumerate(scenes):
            out = out_dir / f"seg_{idx:03d}.mp4"
            run_cmd([self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(start), "-to", str(end), "-i", str(input_video), "-c", "copy", str(out)], self.on_log, step=f"Create segment {idx+1}/{len(scenes)}")
            segments.append(out)
        return segments

    def concat(self, segments: list[Path], out_path: Path) -> None:
        list_file = out_path.parent / "concat.txt"
        list_file.write_text("\n".join(f"file '{p.as_posix()}'" for p in segments), encoding="utf-8")
        run_cmd([self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out_path)], self.on_log, step="Concatenate shuffled segments")
