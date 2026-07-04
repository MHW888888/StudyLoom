from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KeyframeResult:
    status: str
    engine: str
    frames: list[str]
    warnings: list[str]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "engine": self.engine,
            "frames": self.frames,
            "warnings": self.warnings,
        }


def inspect_keyframe_engine() -> dict:
    executable = shutil.which("ffmpeg")
    return {
        "available": bool(executable),
        "engine": "ffmpeg" if executable else "unavailable",
        "executable": executable,
        "note": "Keyframe extraction is optional, local-only, and never downloads platform videos.",
    }


def extract_interval_keyframes(video_path: Path, output_dir: Path, interval_seconds: int = 30) -> KeyframeResult:
    executable = shutil.which("ffmpeg")
    if not executable:
        return KeyframeResult(
            status="unavailable",
            engine="unavailable",
            frames=[],
            warnings=["ffmpeg is not installed; upload screenshots or install ffmpeg for local keyframe extraction."],
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    pattern = output_dir / "frame_%04d.jpg"
    completed = subprocess.run(
        [
            executable,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-vf",
            f"fps=1/{max(1, interval_seconds)}",
            "-q:v",
            "3",
            str(pattern),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=60 * 20,
    )
    frames = [str(path) for path in sorted(output_dir.glob("frame_*.jpg"))]
    if completed.returncode != 0:
        return KeyframeResult(status="fail", engine="ffmpeg", frames=frames, warnings=[(completed.stderr or "ffmpeg failed").strip()])
    return KeyframeResult(status="pass" if frames else "fail", engine="ffmpeg", frames=frames, warnings=[] if frames else ["ffmpeg produced no keyframes."])
