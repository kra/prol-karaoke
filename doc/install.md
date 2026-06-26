# Requirements

- debian box (trixie, ubuntu 23) (this is my testing setup, pi or low budget laptop expected for prod)
- Python 3.12
- ffmpeg, ffplay, etc
---

# Setup

To be done once.

All commands in ~/code/prol-karaoke when on the pi.

## Create deployment virtualenv

- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

## Populate and convert media

Have MP3 and CDG files in `test/media` with no subdirectories. Associated files should have same base filename with mp3 and cdg suffixes.

Note that on the pi the media source is /mnt/usb/karaoke, so link test/media to that.

Create MP4 files from CDG files:

- source venv/bin/activate
- python3 deploy/convert.py test/media/

---

# Run

- on my test box?
 - deploy/mediamtx_v1.18.2_linux_amd64/mediamtx &
- on the pi?
 - deploy/mediamtx_v1.18.2_linux_arm64/mediamtx &
- source venv/bin/activate
- python3 server.py
