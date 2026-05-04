from __future__ import annotations

from pathlib import Path

from utils.ffmpeg_helper import resolve_binary, run_cmd


class Compositor:
    def __init__(self, on_log):
        self.on_log = on_log
        self.ffmpeg = resolve_binary("ffmpeg")

    def compose(self, shuffled_video: Path, image: Path, output_video: Path, crop_focus: str, overlap_percent: int) -> None:
        y_expr = "(ih-oh)/2"
        if crop_focus == "top":
            y_expr = "0"
        elif crop_focus == "bottom":
            y_expr = "ih-oh"

        overlap = overlap_percent / 100
        filter_complex = (
            "[0:v]split=2[vmain][vtmp];"
            f"[1:v][vmain]scale2ref=w=iw:h=ih*0.35[imgs][vref];"
            f"[imgs]crop=w=iw:h=ih:y={y_expr}[imgc];"
            f"[vref]crop=w=iw:h=ih*0.65:x=0:y=0[vtop];"
            f"[vtmp]crop=w=iw:h=ih*{overlap}:x=0:y=ih-ih*{overlap},format=yuva420p,"
            f"geq=lum='p(X,Y)':a='255*(1-Y/(H))'[vfade];"
            "[imgc][vfade]overlay=x=0:y=0[imgov];"
            "[vtop][imgov]vstack=inputs=2[vout]"
        )
        run_cmd([
            self.ffmpeg, "-y", "-i", str(shuffled_video), "-i", str(image), "-filter_complex", filter_complex,
            "-map", "[vout]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(output_video)
        ], self.on_log)
