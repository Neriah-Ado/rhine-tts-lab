"""Synthesize speech with the local Breeze TTS 2 server; save WAV and optionally play.

Run with the project venv python:
  H:\\Vibe coding\\breeze-tts\\.venv\\Scripts\\python.exe tools\\say.py "你好" -i "温柔的年轻女声"
"""
from __future__ import annotations

import argparse
import base64
import subprocess
import sys
import wave
from pathlib import Path

import requests

API = "http://127.0.0.1:7860"


def main() -> int:
    ap = argparse.ArgumentParser(description="Speak text via local Breeze TTS 2")
    ap.add_argument("text", help="Text to synthesize; inline markers like (laugh) / [笑] are supported")
    ap.add_argument("-o", "--out", help="Output WAV path (default: tools/last-say.wav)")
    ap.add_argument("-i", "--instruction", help="Voice description; enables the CFG instruction path")
    ap.add_argument("--cfg", type=float, help="CFG scale (default: 4 with instruction, 1 without)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("-r", "--ref-audio", help="Reference audio file for voice cloning")
    ap.add_argument("--ref-text", help="Exact transcript of the reference audio")
    ap.add_argument("-n", "--no-play", action="store_true", help="Do not play the result")
    args = ap.parse_args()

    data: dict[str, str] = {
        "text": args.text,
        "seed": str(args.seed),
        "encode": "base64",
        "cfg_scale": str(args.cfg if args.cfg is not None else (4 if args.instruction else 1)),
    }
    if args.instruction:
        data["instruction"] = args.instruction
    if args.ref_audio:
        files = {"ref_audio": open(args.ref_audio, "rb")}
        if not args.ref_text:
            print("error: --ref-text is required with --ref-audio", file=sys.stderr)
            return 2
        data["ref_text"] = args.ref_text
    else:
        files = None

    try:
        r = requests.post(f"{API}/v1/audio/speech", data=data, files=files, timeout=600)
    except requests.ConnectionError:
        print(f"error: server not reachable at {API} — start it with start-breeze-server.cmd", file=sys.stderr)
        return 1
    r.raise_for_status()
    pcm = base64.b64decode(r.json()["audio"])

    out = Path(args.out) if args.out else Path(__file__).resolve().parent / "last-say.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(pcm)
    print(out)

    if not args.no_play:
        subprocess.run(
            ["powershell", "-NoProfile", "-c", f"(New-Object System.Media.SoundPlayer '{out}').PlaySync()"],
            check=False,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
