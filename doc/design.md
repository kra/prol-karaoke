# Design Document

## Overview

A system to allow a user to select karaoke tracks to stream over video.

## Design

A directory holds pairs of CDG and MP3 files. The CDG files have karaoke video for the associated MP3 audio files. A HTTP server is always running to provide a user interface. A player function is called by the server to stream the audio and video over RTSP.

### Player

A Python function `play_karaoke` uses `ffmpeg` (via `ffmpeg-python`) piped into `ffplay` to play CDG/video and audio locally on the host. `stop_karaoke` stops any currently running `ffmpeg`/`ffplay` processes.

#### Requirements

- The `ffmpeg` and `ffplay` binaries must be installed and available on `PATH` for local playback to work.
- If you need remote clients to connect to streams, run an external RTSP server (for example `aler9/rtsp-simple-server`) and configure `player` to push streams to that server instead of using the local `ffplay` pipeline.

### Server

The server runs a Python HTTP server using Python's built-in `HTTPServer` and `SimpleHTTPRequestHandler`.

#### Endpoints

- **GET /**: Serves the main HTML UI page with an interactive song list
- **POST /api/play**: Accepts a JSON request with a song name and starts playback
- **POST /api/stop**: Stops the current playback, if any
- **GET /api/status**: Returns the current playback status and song info

#### Song Discovery

The server automatically discovers songs by scanning the music directory for CDG files and their paired audio files (MP3, AFPK, WAV, or FLAC formats).

#### UI

The UI is a single interactive HTML page that:
- Displays a list of all available songs
- Allows users to click on any song to add it to the queue
- Shows the currently playing song, playback status, and any errors
- Provides a stop link to stop the current song from playing
- Shows the queue of songs, with cancel links for each which removes them from the queue
- Provides a play button to play the next song in the queue

#### Playback

When a song is selected:
- The song is added to the queue

When the play button is selected:
- If a song is currently playing:
  - An error is displayed and another song is not played
- If a song is not currently playing:
  - The next song is removed from the queue 
  - The UI sends a POST request to `/api/play` with the song name
  - The server validates the request and locates the CDG and audio files
  - The server updates shared playback state and starts `player.play_karaoke()` in a background thread
  - The UI begins polling `/api/status` every second
  - While playback is running, `/api/status` returns `playing` and the currently playing song
  - When the background playback stops or finishes, `/api/status` returns `finished`
  - The status div displays `Song finished` once polling observes the finished state
  - If the POST returns an error, the status div displays `Error playing song`
  - If an unexpected error is caught, the status div displays the error.
        
#### Stop

When the stop link is selected:
- The UI sends a POST request to `/api/stop`
- The current playback is stopped with player.stop_karaoke()
- `/api/status` returns `finshed`
