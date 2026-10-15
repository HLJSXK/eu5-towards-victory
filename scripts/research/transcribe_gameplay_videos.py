"""Transcribe local research media with an explicitly supplied Whisper model.

Requires faster-whisper. No model, media, or dependency is downloaded by this
script. Outputs are research intermediates, not verified gameplay conclusions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def timestamp(seconds: float) -> str:
    whole = int(seconds)
    return f"{whole // 3600:02}:{whole % 3600 // 60:02}:{whole % 60:02}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--media-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dependency-dir", type=Path)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--language", choices=("zh", "en", "auto"), default="auto")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--ids", nargs="+", required=True)
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    handles = []
    if args.dependency_dir:
        deps = args.dependency_dir.resolve()
        sys.path.insert(0, str(deps))
        if os.name == "nt":
            bins = sorted((deps / "nvidia").glob("*/bin"))
            os.environ["PATH"] = os.pathsep.join(map(str, bins)) + os.pathsep + os.environ.get("PATH", "")
            handles = [os.add_dll_directory(str(path)) for path in bins]
    from faster_whisper import BatchedInferencePipeline, WhisperModel

    model_path = args.model.resolve()
    model = WhisperModel(
        str(model_path), device=args.device,
        compute_type="int8_float16" if args.device == "cuda" else "int8",
        cpu_threads=6, local_files_only=True,
    )
    pipeline = BatchedInferencePipeline(model=model)
    args.output.mkdir(parents=True, exist_ok=True)
    prompt = "欧陆风云五，奥斯曼，征召兵，常备军，控制力，接近度，市民，劳工，贵族，教士，王权，税基，阶层满意度，议会，思潮，制度，生产方式，贸易容量，贸易优势。"
    for source_id in args.ids:
        audio = args.media_root / source_id / "audio.m4s"
        destination = args.output / f"{source_id}.json"
        if destination.exists() and not args.overwrite:
            print(f"SKIP {source_id}: existing transcription", flush=True)
            continue
        print(f"START {source_id}", flush=True)
        started = time.monotonic()
        language = None if args.language == "auto" else args.language
        segments, info = pipeline.transcribe(
            str(audio), language=language, beam_size=3,
            batch_size=args.batch_size, vad_filter=True,
            initial_prompt=prompt if language == "zh" else None,
        )
        rows = []
        text_path = args.output / f"{source_id}.txt"
        with text_path.open("w", encoding="utf-8", newline="\n") as stream:
            for segment in segments:
                row = {"start": segment.start, "end": segment.end,
                       "text": segment.text, "avg_logprob": segment.avg_logprob,
                       "no_speech_prob": segment.no_speech_prob}
                rows.append(row)
                stream.write(f"[{timestamp(segment.start)}–{timestamp(segment.end)}] {segment.text.strip()}\n")
                stream.flush()
                if len(rows) % 100 == 0:
                    print(f"PROGRESS {source_id}: {timestamp(segment.end)} / {timestamp(info.duration)}", flush=True)
        record = {
            "source_id": source_id, "method": "machine_audio_transcription",
            "verified": False, "model_directory": model_path.name,
            "device": args.device, "compute_type": "int8_float16" if args.device == "cuda" else "int8",
            "beam_size": 3, "batch_size": args.batch_size,
            "requested_language": args.language,
            "language": info.language, "duration": info.duration,
            "duration_after_vad": info.duration_after_vad,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "audio_sha256": hashlib.sha256(audio.read_bytes()).hexdigest(),
            "transcript_sha256": hashlib.sha256(text_path.read_bytes()).hexdigest(),
            "elapsed_seconds": time.monotonic() - started, "segments": rows,
        }
        destination.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"DONE {source_id}: {len(rows)} segments; {record['elapsed_seconds']:.1f}s", flush=True)
    for handle in handles:
        handle.close()


if __name__ == "__main__":
    main()
