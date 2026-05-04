from __future__ import annotations

import random
from pathlib import Path


def shuffle_segments(segments: list[Path], random_mode: str = "keep_first") -> list[Path]:
    if len(segments) < 2:
        return segments
    if random_mode == "full":
        out = segments[:]
        random.shuffle(out)
        return out
    first, rest = segments[0], segments[1:]
    random.shuffle(rest)
    return [first] + rest
