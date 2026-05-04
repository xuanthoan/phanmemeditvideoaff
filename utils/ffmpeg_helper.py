from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Callable


def resolve_binary(name: str) -> str:
    local = Path(__file__).resolve().parents[1] / "bin" / f"{name}.exe"
    return str(local if local.exists() else name)


def run_cmd(args: list[str], on_log: Callable[[str], None]) -> None:
    on_log("$ " + " ".join(shlex.quote(a) for a in args))
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    assert proc.stdout is not None
    for line in proc.stdout:
        on_log(line.rstrip())
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"Command failed ({code}): {' '.join(args)}")
