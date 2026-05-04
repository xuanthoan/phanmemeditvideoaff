from __future__ import annotations

import random
import shutil
from pathlib import Path

from core.audio_manager import AudioManager
from core.compositor import Compositor
from core.scene_detector import detect_scenes
from core.segment_shuffler import shuffle_segments
from core.video_processor import VideoProcessor
from utils.file_helper import ensure_output


class BatchRunner:
    def __init__(self, on_log):
        self.on_log = on_log
        self.stop_requested = False

    def stop(self) -> None:
        self.stop_requested = True

    def process(self, videos: list[Path], images: list[Path], output_dir: Path | None, settings: dict, on_progress):
        audio = AudioManager(self.on_log)
        video = VideoProcessor(self.on_log)
        comp = Compositor(self.on_log)
        for idx, input_video in enumerate(videos, start=1):
            if self.stop_requested:
                self.on_log("Dừng theo yêu cầu.")
                break
            try:
                target_out = ensure_output(input_video, output_dir)
                work = target_out / f"_tmp_{input_video.stem}"
                work.mkdir(exist_ok=True)
                image = random.choice(images)
                raw_audio = work / "audio.aac"
                audio.extract(input_video, raw_audio)
                scenes = detect_scenes(input_video, settings["scene_sensitivity"])
                segs = video.cut_segments(input_video, scenes, work)
                shuffled = shuffle_segments(segs, settings["random_mode"])
                shuffled_video = work / "shuffled.mp4"
                video.concat(shuffled, shuffled_video)
                composed = work / "composed.mp4"
                comp.compose(shuffled_video, image, composed, settings["crop_focus"], settings["overlap_percent"])
                final = target_out / f"{input_video.stem}_processed.mp4"
                audio.mux(composed, raw_audio, final)
                self.on_log(f"Hoàn tất: {final}")
            except Exception as exc:
                self.on_log(f"Lỗi {input_video.name}: {exc}")
            finally:
                on_progress(idx, len(videos))
                if settings.get("cleanup_temp", True) and 'work' in locals() and work.exists():
                    shutil.rmtree(work, ignore_errors=True)
