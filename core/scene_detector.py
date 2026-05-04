from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from scenedetect import ContentDetector, SceneManager, open_video


def detect_scenes(video_path: Path, threshold: float) -> List[Tuple[float, float]]:
    video = open_video(str(video_path))
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    manager.detect_scenes(video)
    scene_list = manager.get_scene_list()
    return [(s[0].get_seconds(), s[1].get_seconds()) for s in scene_list]
