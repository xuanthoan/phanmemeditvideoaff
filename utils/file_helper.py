from __future__ import annotations

from pathlib import Path
from typing import Iterable

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def collect_videos(paths: Iterable[Path]) -> list[Path]:
    videos: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS:
            videos.append(p)
        elif p.is_dir():
            videos.extend([f for f in p.iterdir() if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS])
    return sorted(set(videos))


def collect_images(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
        return [path]
    if path.is_dir():
        return sorted([f for f in path.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS])
    return []


def ensure_output(video_path: Path, output_dir: Path | None) -> Path:
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    auto = video_path.parent / "output_processed"
    auto.mkdir(parents=True, exist_ok=True)
    return auto
