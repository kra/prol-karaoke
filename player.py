import subprocess
import sys
import threading
import time
import socket
from typing import Optional
from urllib.parse import urlparse

# import ffmpeg

_current_lock = threading.Lock()
# _current_ffmpeg_process: Optional[subprocess.Popen] = None
_stop_event = threading.Event()

# RTSP_SERVER_URL = "rtsp://localhost:8554"


# def _check_rtsp_server(url: str, timeout: float = 2.0) -> None:
#     parsed = urlparse(url)
#     host = parsed.hostname or "localhost"
#     port = parsed.port or 8554
#     try:
#         with socket.create_connection((host, port), timeout=timeout):
#             return
#     except OSError as exc:
#         raise RuntimeError(
#             f"RTSP server at {host}:{port} not reachable: {exc}.\n"
#             "Start an RTSP server (e.g. rtsp-simple-server)."
#         )


# def play_karaoke(video_path: str) -> str:
#     """
#     Push video to an RTSP server using ffmpeg.

#     Args:
#         video_path: Path to the video file containing karaoke graphics.

#     Returns:
#         The video RTSP URL that was pushed.
#     """
#     global _current_ffmpeg_process

#     stop_karaoke()
#     _stop_event.clear()

#     # Verify RTSP server availability before starting ffmpeg so failure is
#     # explicit and actionable.
#     _check_rtsp_server(RTSP_SERVER_URL)

#     video_url = RTSP_SERVER_URL.rstrip("/") + "/video"

#     media_input = ffmpeg.input(video_path, re=None)

#     # pkt_size=1440 to avoid:
#     # [path video] RTP packets are too big (1460 > 1440), remuxing them into smaller ones
#     # max_muxing_queue_size=2048
#     video_output = ffmpeg.output(
#         media_input.video,
#         media_input.audio,
#         video_url,
#         format="rtsp",
#         vcodec="copy",
#         acodec="copy",
#         pkt_size=1440,
#         rtsp_transport="udp")

#     process = video_output.run_async(
#         pipe_stderr=True,
#         overwrite_output=True,
#     )

#     with _current_lock:
#         _current_ffmpeg_process = process

#     try:
#         while True:
#             if _stop_event.is_set():
#                 break

#             if process.poll() is not None:
#                 if process.returncode != 0:
#                     # Read stderr for diagnostic message
#                     try:
#                         stderr = process.stderr.read().decode(errors="replace")
#                     except Exception:
#                         stderr = "(no stderr available)"
#                     raise RuntimeError(f"ffmpeg exited with status {process.returncode}: {stderr}")
#                 break

#             time.sleep(0.25)
#     finally:
#         stop_karaoke()

#     return video_url

def play_karaoke(video_path: str) -> str:
    stop_karaoke()
    command = [
        "ruby",
        "/home/proltv/scheduler/play.rb",
        video_path]
    subprocess.run(command, check=True)

def stop_karaoke() -> None:
    command = [
        "ruby",
        "/home/proltv/scheduler/clear.rb"]
    subprocess.run(command, check=True)

# def stop_karaoke() -> None:
#     """
#     Stop any currently streaming ffmpeg process.
#     """
#     global _current_ffmpeg_process

#     _stop_event.set()

#     with _current_lock:
#         if _current_ffmpeg_process is not None:
#             try:
#                 _current_ffmpeg_process.terminate()
#                 _current_ffmpeg_process.wait(timeout=5)
#             except subprocess.TimeoutExpired:
#                 _current_ffmpeg_process.kill()
#             except Exception:
#                 pass
#             finally:
#                 _current_ffmpeg_process = None


# if __name__ == "__main__":
#     # Command line usage, for testing.
#     if len(sys.argv) != 2:
#         print("Usage: python player.py <video_path>")
#         sys.exit(1)

#     print("Pushing to RTSP server:", RTSP_SERVER_URL)
#     try:
#         v = play_karaoke(sys.argv[1])
#         print("Streaming to:", v)
#     except Exception as e:
#         print("Error starting RTSP push:", e)
#         sys.exit(1)

