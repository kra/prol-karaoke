from pathlib import Path


MUSIC_DIR = Path(__file__).parent / "test" / "media"
SUPPORTED_AUDIO_EXTENSIONS = [".mp3", ".MP3"]


def discover_songs(directory: Path) -> list[dict]:
    """
    Discover video and paired audio files in the given directory.

    Args:
        directory: Path to the directory containing song files.

    Returns:
        List of dicts with 'title', 'video', and 'audio' keys, sorted by title.
    """
    songs = {}

    for file_path in directory.glob("*.mp4"):
        base_name = file_path.stem
        title = base_name.split(" - ", 1)[-1] if " - " in base_name else base_name

        audio_file = None
        for ext in SUPPORTED_AUDIO_EXTENSIONS:
            candidate = file_path.with_suffix(ext)
            if candidate.exists():
                audio_file = candidate
                break

        if audio_file:
            songs[base_name] = {
                "title": title, #
                "video": MUSIC_DIR / file_path.name, #
                "base_name": base_name, #
            }

    #return sorted(songs.values(), key=lambda s: s["title"])
    return sorted(songs.values(), key=lambda s: s["video"])


songs = discover_songs(MUSIC_DIR)
