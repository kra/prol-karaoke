# Karaoke driver

# Meta-requirements

# Requirements

- debian box (trixie, ubuntu 23)
- Python 3.12
- ffmpeg
---

# Setup

To be done once.

## Populate and convert media

Have MP3 and CDG files in `test/media` with no subdirectories. Associated files should have same base filename with mp3 and cdg suffixes.

Create MP4 files from CDG files:

- python3.12 -m venv venv
- python3 deploy/convert.py test/media/

## Create deployment virtualenv

- python3.12 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

---

# Run

- deploy/mediamtx_v1.18.2_linux_amd64/mediamtx &
- source venv/bin/activate
- python3 server.py

---

# Test

## Test converter and player

Convert a MP4 file from a CDG file:

- source venv/bin/activate
- python3 deploy/convert.py test/media/foo.cdg

Start the mediamtx server:

- deploy/mediamtx_v1.18.2_linux_amd64/mediamtx

In another shell, start the player:

- source venv/bin/activate
- python3 player.py test/media/foo.mp4

In another shell, open the generated stream with ffplay:

- ffplay rtsp://localhost:8554/video

## Test server

Start the mediamtx server:

- deploy/mediamtx_v1.18.2_linux_amd64/mediamtx

In another shell, start the server:
- source venv/bin/activate
- python3 server.py

Visit http://localhost:8000/ with a browser, queue and play a song.

In another shell, open the generated stream with ffplay:

- ffplay rtsp://localhost:8554/video

# TODO

ffplay fails if the media is not currently streaming. Find out how to set up the server, client, or mediamtx RTSP server so that it plays a blank screen when there is no streaming.
