from __future__ import annotations

from pathlib import Path

from utils.ffmpeg_helper import resolve_binary, run_cmd


class Compositor:
    def __init__(self, on_log):
        self.on_log = on_log
        self.ffmpeg = resolve_binary("ffmpeg")

    def compose(self, shuffled_video: Path, image: Path, output_video: Path, crop_focus: str, overlap_percent: int) -> None:
        # Target layout (fixed by spec)
        # - visible video total: 70% (main 65% + overlap 5%)
        # - image area: 35%
        video_visible = 0.70
        main_video = 0.65
        overlap = max(0.01, min(overlap_percent / 100.0, 0.20))

        # Image focus for vertical crop after aspect-preserving scale.
        y_expr = "(ih-oh)/2"
        if crop_focus == "top":
            y_expr = "0"
        elif crop_focus == "bottom":
            y_expr = "ih-oh"

        # Important:
        # 1) image is scaled with preserved aspect ratio (no stretch), then center/top/bottom cropped.
        # 2) video is NOT scaled; it is shifted upward by 30%H => only 70% visible in frame.
        # 3) fade strip comes from bottom 5% of original video and overlays at y=65%H with alpha 100%->0%.
        filter_complex = (
            "[0:v]format=yuv420p[vsrc];"
            "[1:v][vsrc]scale2ref=w=iw:h=ih:force_original_aspect_ratio=increase[imgfit][vref];"
            f"[imgfit]crop=w=iw:h=ih*0.35:x=(iw-ow)/2:y={y_expr}[img35];"
            "[vsrc]crop=w=iw:h=ih*0.05:x=0:y=ih*0.95,format=yuva420p,"
            "geq=lum='p(X,Y)':a='255*(1-Y/H)'[vfade];"
            "color=c=black:s=16x16[base0];"
            "[base0][vsrc]scale2ref[base][vtmp];"
            "[base][img35]overlay=x=0:y=H-h[lay1];"
            f"[lay1][vtmp]overlay=x=0:y='-(H*{1.0 - video_visible})'[lay2];"
            f"[lay2][vfade]overlay=x=0:y='H*{main_video}'[vout]"
        )

        run_cmd(
            [
                self.ffmpeg,
                "-y",
                "-i",
                str(shuffled_video),
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
                str(output_video),
            ],
            self.on_log,
        )
