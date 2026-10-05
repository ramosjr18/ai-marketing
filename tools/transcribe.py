#!/usr/bin/env python3
"""Transcribe a recording to text, on this machine, uploading nothing.

Used by `/client`: drop a call recording in `clients/<case>/material/` and this turns it into
text the agent can read. The model runs locally (faster-whisper, CPU); the recording never
leaves the laptop.

What it does NOT do, worth knowing before trusting the output:

  - **It does not tell speakers apart.** One block of text with timestamps.
  - **It gets figures, proper nouns and acronyms wrong.** Exactly what a diagnosis needs to be
    exact about. Every transcript carries that warning inside it.

Usage:
    .venv/bin/python tools/transcribe.py <audio>                    one file, .md beside it
    .venv/bin/python tools/transcribe.py <folder>                   every untranscribed audio
    .venv/bin/python tools/transcribe.py <audio> --out clients/x/transcripts/
                                                  into that folder, named <uuid7>.md
    .venv/bin/python tools/transcribe.py <audio> --model medium     slower, better with figures
    .venv/bin/python tools/transcribe.py <audio> --lang auto        detect the language
    .venv/bin/python tools/transcribe.py <audio> --plain            no timestamps
    .venv/bin/python tools/transcribe.py <audio> --force            redo an existing one

Outputs markdown with frontmatter: UUID v7 id, source file, model, duration. The model
downloads once to ~/.cache/huggingface and stays there.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from id7 import uuid7  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
AUDIO_EXT = {".m4a", ".mp3", ".wav", ".ogg", ".opus", ".flac", ".mp4", ".webm", ".aac"}

# Audio is decoded with ffmpeg rather than PyAV, which is what faster-whisper reaches for on
# its own: PyAV 19 changed the signature of `open()` and there is no wheel of an earlier
# version for Python 3.14. Handing it a decoded array avoids that dependency entirely.
SAMPLE_RATE = 16000

AVISO = (
    "AVISO: transcripción automática. No distingue quién habla y puede equivocarse con "
    "cifras,\nnombres propios y siglas. Confirma cualquier número antes de usarlo en un "
    "diagnóstico\no en una propuesta."
)


def hhmmss(seconds: float) -> str:
    s = int(seconds)
    h, rest = divmod(s, 3600)
    m, s = divmod(rest, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def decode_audio(path: Path):
    """PCM mono a 16 kHz, en memoria, con el ffmpeg del sistema."""
    import numpy as np

    if not shutil.which("ffmpeg"):
        sys.exit("Falta ffmpeg en el sistema. En Arch: sudo pacman -S ffmpeg")
    cmd = [
        "ffmpeg", "-nostdin", "-threads", "0", "-i", str(path),
        "-f", "s16le", "-ac", "1", "-acodec", "pcm_s16le", "-ar", str(SAMPLE_RATE), "-",
    ]
    done = subprocess.run(cmd, capture_output=True)
    if done.returncode != 0:
        tail = done.stderr.decode("utf-8", "replace").strip().splitlines()[-3:]
        sys.exit(f"ffmpeg no pudo leer {path.name}:\n" + "\n".join(tail))
    return np.frombuffer(done.stdout, np.int16).astype(np.float32) / 32768.0


def load_model(name: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit(
            "Falta faster-whisper. Instálalo con:\n"
            "    uv pip install -r tools/requirements.txt"
        )
    print(f"Cargando el modelo {name} (la primera vez se descarga)…", file=sys.stderr)
    return WhisperModel(name, device="cpu", compute_type="int8")


def transcribe_one(model, model_name: str, audio: Path, out: Path, lang: str, plain: bool) -> Path:
    segments, info = model.transcribe(
        decode_audio(audio),
        language=None if lang == "auto" else lang,
        vad_filter=True,
        beam_size=5,
    )

    lines = []
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        lines.append(text if plain else f"[{hhmmss(seg.start)}] {text}")
        print(".", end="", flush=True, file=sys.stderr)
    print("", file=sys.stderr)

    ident = out.stem if is_uuid_name(out.stem) else str(uuid7())
    header = f"""---
id: {ident}
kind: transcript
source: {audio.name}
model: faster-whisper {model_name}
duration: {hhmmss(info.duration)}
lang: {info.language} ({info.language_probability:.2f})
transcribed: {date.today().isoformat()}
---

# Transcripción de {audio.name}

{AVISO}

---

"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    return out


def is_uuid_name(stem: str) -> bool:
    return len(stem) == 36 and stem.count("-") == 4


def targets(path: Path, force: bool) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        sys.exit(f"No existe: {path}")
    found = sorted(p for p in path.iterdir() if p.suffix.lower() in AUDIO_EXT)
    if not force:
        pending = [p for p in found if not p.with_suffix(p.suffix + ".md").exists()]
        skipped = len(found) - len(pending)
        if skipped:
            print(f"{skipped} ya transcrito(s), se saltan. --force para rehacerlos.")
        return pending
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe audio en local para un caso de cliente.")
    ap.add_argument("path", help="fichero de audio o carpeta (normalmente clients/<caso>/material)")
    ap.add_argument("--out", help="fichero de salida, o carpeta (se nombra <uuid7>.md)")
    ap.add_argument("--model", default="small", help="tiny · base · small (def.) · medium · large-v3")
    ap.add_argument("--lang", default="es", help="código de idioma, o 'auto' (def. es)")
    ap.add_argument("--plain", action="store_true", help="sin marcas de tiempo")
    ap.add_argument("--force", action="store_true", help="rehace transcripciones existentes")
    args = ap.parse_args()

    path = Path(args.path).expanduser()
    files = targets(path, args.force)
    if not files:
        print("Nada que transcribir.")
        return

    model = load_model(args.model)
    for audio in files:
        out = resolve_out(audio, args.out)
        if out.exists() and not args.force:
            print(f"{out.name} ya existe, se salta (--force para rehacerla).")
            continue
        print(f"\n{audio.name} → {out.name}", file=sys.stderr)
        transcribe_one(model, args.model, audio, out, args.lang, args.plain)
        try:
            rel = out.relative_to(REPO)
        except ValueError:
            rel = out
        print(f"Escrito: {rel}")


def resolve_out(audio: Path, out_arg: str | None) -> Path:
    """Sin --out, un .md al lado del audio. Con una carpeta, <uuid7>.md dentro."""
    if not out_arg:
        return audio.with_suffix(audio.suffix + ".md")
    out = Path(out_arg).expanduser()
    if out.is_dir() or out_arg.endswith("/"):
        existing = already_there(out, audio)
        return existing if existing else out / f"{uuid7()}.md"
    return out


def already_there(folder: Path, audio: Path) -> Path | None:
    """Una transcripción de este audio en la carpeta. Los nombres son UUID, así que la
    pertenencia se lee del frontmatter y no del nombre del fichero."""
    if not folder.is_dir():
        return None
    for md in folder.glob("*.md"):
        head = md.read_text(encoding="utf-8", errors="replace")[:400]
        if f"source: {audio.name}" in head:
            return md
    return None


if __name__ == "__main__":
    main()
