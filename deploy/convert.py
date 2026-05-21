from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".afpk", ".wav", ".flac"]

def convert_cdg(cdg_path: str) -> None:
    """Convert a CDG file or all CDG files in a directory to MP4 using ffmpeg.

    Args:
        cdg_path: Path to a CDG file or a directory containing CDG files.
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
            _convert_single(file_path)
    elif path.is_file():
        if path.suffix.lower() != ".cdg":
            raise ValueError(f"Expected a .cdg file, got: {cdg_path}")
        _convert_single(path)
    else:
        raise ValueError(f"Unsupported path type: {cdg_path}")


def _find_matching_audio(cdg_file: Path) -> Path | None:
    for ext in SUPPORTED_AUDIO_EXTENSIONS:
        candidate = cdg_file.with_suffix(ext)
        if candidate.exists():
            return candidate
    return None


def _convert_single(cdg_file: Path) -> None:
    mp4_file = cdg_file.with_suffix(".mp4")
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
        "-y",                   # overwrite
        "-i",
        str(cdg_file),
        "-i",
        str(audio_file),
        "-map",
        "0:v",
        "-map",
        "1:a",
        "-c:v",                 # codec: video
        "libx264",              # codec
        "-preset",              # encoding preset
        "veryfast",             # default medium, try fast?
        "-crf",                 # Select the quality for constant quality mode (from -1 to FLT_MAX) (default -1)
        "28",                   # example was 23, max 51, lower is better quality
        "-pix_fmt",             # pixel formats
        "yuv420p",
        "-c:a",                 # codec: audio
        "aac",                  # codec
        "-ar",                  # audio sample rate
        "44100",                # 44.1 KHz audio
        "-filter:v",            # video filter
        #"fps=30, scale=480x360", # framerate to 30 fps, size to 480x360
                                  # use Y scale of -1 to maintain aspect ratio
        "fps=30",               # framerate to 30 fps
        # XXX maxrate and bufsize to avoid high bitrate, but is this incompatible
        #     with -crf?
        #     this should also use -b:v, or only -b:v?
        #     use -bufsize to avoid bitrate spikes, poss degrade video?
        #     try equal or half bitrate?
        #"-maxrate",              # max bitrate video
        #"56k",
        #"-b:a",                 # bitrate video bitrate (please use -b:v) ???
        #"192k",
        "-shortest",            # finish encoding within shortest input
        str(mp4_file),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert CDG files to MP4 using ffmpeg.")
    parser.add_argument(
        "path",
        help="Path to a .cdg file or a directory containing .cdg files.")
    args = parser.parse_args()

    convert_cdg(args.path)
