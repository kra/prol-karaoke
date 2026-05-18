from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".afpk", ".wav", ".flac"]


# ffmpeg -i test/media/foo.cdg -i test/media/foo.mp3 -map 0:v -map 1:a -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest test/media/foo.mp4
def convert_cdg(cdg_path: str, overwrite: bool = False) -> None:
    """Convert a CDG file or all CDG files in a directory to MP4 using ffmpeg.

    Args:
        cdg_path: Path to a CDG file or a directory containing CDG files.
        overwrite: When True, replace existing MP4 files.
    """
    path = Path(cdg_path)
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {cdg_path}")

    if path.is_dir():
        cdg_files = sorted(path.glob("*.cdg"))
        if not cdg_files:
            print(f"No CDG files found in directory: {cdg_path}")
            return
        for file_path in cdg_files:
            _convert_single(file_path, overwrite)
    elif path.is_file():
        if path.suffix.lower() != ".cdg":
            raise ValueError(f"Expected a .cdg file, got: {cdg_path}")
        _convert_single(path, overwrite)
    else:
        raise ValueError(f"Unsupported path type: {cdg_path}")


def _find_matching_audio(cdg_file: Path) -> Path | None:
    for ext in SUPPORTED_AUDIO_EXTENSIONS:
        candidate = cdg_file.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def _convert_single(cdg_file: Path, overwrite: bool) -> None:
    mp4_file = cdg_file.with_suffix(".mp4")
    if mp4_file.exists() and not overwrite:
        print(f"Skipping existing output: {mp4_file}")
        return

    audio_file = _find_matching_audio(cdg_file)
    if audio_file is None:
        raise FileNotFoundError(
            f"No matching audio file found for {cdg_file.name}. "
            f"Search for {', '.join(SUPPORTED_AUDIO_EXTENSIONS)} with the same base name"
        )

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise FileNotFoundError("ffmpeg executable not found in PATH")

    print(f"Converting {cdg_file} + {audio_file} -> {mp4_file}")
    command = [
        ffmpeg,
        "-y" if overwrite else "-n",
        "-i",
        str(cdg_file),
        "-i",
        str(audio_file),
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        str(mp4_file),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CDG files to MP4 using ffmpeg.")
    parser.add_argument("path", help="Path to a .cdg file or a directory containing .cdg files.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing MP4 output files.",
    )
    args = parser.parse_args()

    convert_cdg(args.path, overwrite=args.overwrite)
