from __future__ import annotations

from pathlib import Path

from utils.ffmpeg_helper import resolve_binary, run_cmd


class Compositor:
    def __init__(self, on_log):
        self.on_log = on_log
        self.ffmpeg = resolve_binary("ffmpeg")

    def compose(self, shuffled_video: Path, image: Path, output_video: Path, crop_focus: str, overlap_percent: int) -> None:
        video_visible = 0.70
        main_video = 0.65

        y_expr = "(ih-oh)/2"
        if crop_focus == "top":
            y_expr = "0"
        elif crop_focus == "bottom":
            y_expr = "ih-oh"

        filter_complex = (
            "[0:v]format=yuv420p[vsrc];"
            "[1:v][vsrc]scale2ref=w=iw:h=ih:force_original_aspect_ratio=increase[imgfit][vtmp];"
            f"[imgfit]crop=w=iw:h=ih*0.35:x=(iw-ow)/2:y={y_expr}[img35];"
            "[vsrc]crop=w=iw:h=ih*0.05:x=0:y=ih*0.95,format=yuva420p,"
            "geq=lum='p(X,Y)':a='255*(1-Y/H)'[vfade];"
            "color=c=black:s=16x16[base0];"
            "[base0][vtmp]scale2ref[base][vkeep];"
            "[base][img35]overlay=x=0:y=H-h[lay1];"
            f"[lay1][vkeep]overlay=x=0:y='-(H*{1.0 - video_visible})'[lay2];"
            f"[lay2][vfade]overlay=x=0:y='H*{main_video}'[vout]"
        )

        run_cmd(
            [
                self.ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(shuffled_video),
                "-loop",
                "1",
                "-i",
                str(image),
                "-filter_complex",
                filter_complex,
                "-map",
                "[vout]",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "20",
                "-shortest",
                str(output_video),
            ],
            self.on_log,
            step="Compositing video + image",
        )
