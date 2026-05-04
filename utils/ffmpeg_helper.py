from __future__ import annotations

import hashlib
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable


class FFmpegNotFoundError(FileNotFoundError):
    pass


def _candidate_paths(name: str) -> list[Path]:
    exe = f"{name}.exe" if os.name == "nt" else name
    candidates: list[Path] = []

    # PyInstaller onedir/onefile extraction dir.
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "bin" / exe)
        candidates.append(Path(sys.executable).resolve().parent / "bin" / exe)

    repo_root = Path(__file__).resolve().parents[1]
    candidates.append(repo_root / "bin" / exe)
    return candidates


def resolve_binary(name: str) -> str:
    for p in _candidate_paths(name):
        if p.exists():
            return str(p)

    found = shutil.which(name)
    if found:
        return found

    exe = f"{name}.exe" if os.name == "nt" else name
    search_hint = "\n".join(f"- {p}" for p in _candidate_paths(name))
    raise FFmpegNotFoundError(
        f"Không tìm thấy {exe}. Hãy đặt file vào một trong các vị trí sau hoặc thêm vào PATH:\n{search_hint}"
    )


def safe_stem(name: str, limit: int = 64) -> str:
    cleaned = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name).strip("_")
    if not cleaned:
        cleaned = "video"
    if len(cleaned) <= limit:
        return cleaned
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    return f"{cleaned[: limit - 11]}_{digest}"


def run_cmd(args: list[str], on_log: Callable[[str], None]) -> None:
    on_log("$ " + " ".join(shlex.quote(a) for a in args))
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except FileNotFoundError as exc:
        raise FFmpegNotFoundError(f"Không thể chạy lệnh vì thiếu binary: {args[0]}") from exc

    assert proc.stdout is not None
    for line in proc.stdout:
        on_log(line.rstrip())
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"Command failed ({code}): {' '.join(args)}")
