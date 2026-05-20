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
