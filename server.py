import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path

import player
import songlist
import song_list_html

print("initializing")

song_list_html = ""
for song in songlist.songs:
    song_list_html += f'<div class="song-item" onclick="addToQueue(\'{song["base_name"]}\', \'{song["title"]}\')">{song["video"]}</div>\n'

print("built html")

ui_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Karaoke Player</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .song-list {{}}
        .song-item {{
            padding: 10px;
            margin: 5px 0;
            background: #f0f0f0;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .song-item:hover {{ background: #e0e0e0; }}
        .status {{ margin-top: 20px; padding: 10px; background: #e3f2fd; border-radius: 4px; }}
        .error {{ color: red; }}
        .success {{ color: green; }}
        .controls {{ margin-top: 15px; }}
        .controls button {{ padding: 8px 12px; margin-right: 8px; cursor: pointer; }}
        .content-columns {{ display: flex; gap: 20px; margin-top: 20px; }}
        .column {{ flex: 1; }}
        .song-list {{ }}
        .song-list h3 {{ margin-top: 0; }}
        .queue-section {{ }}
        .queue-section h3 {{ margin-top: 0; }}
        .queue-item {{ padding: 8px; margin: 5px 0; background: #fff3cd; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }}
        .queue-item button {{ padding: 4px 8px; font-size: 12px; }}
        #status {{ height: 150px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; background: #f9f9f9; font-family: monospace; font-size: 12px; }}
        .transcript-entry {{ margin: 4px 0; }}
        .transcript-time {{ color: #666; margin-right: 8px; }}
        .transcript-error {{ color: red; }}
        .transcript-success {{ color: green; }}
    </style>
</head>
<body>
    <h1>Karaoke Player</h1>

    <div class="status" id="status"></div>
    <div class="controls">
        <button onclick="playNextFromQueue()">Play</button>
        <button onclick="stopPlayback()">Stop</button>
    </div>

    <div class="content-columns">
        <div class="column">
            <div class="song-list">
                <h3>Available Songs</h3>
                {song_list_html}
            </div>
        </div>
        <div class="column">
            <div class="queue-section">
                <h3>Queue</h3>
                <div id="queue"></div>
            </div>
        </div>
    </div>

    <script>
        let statusTimer = null;
        let currentQueue = [];

        function getTimestamp() {{
            const now = new Date();
            return now.toLocaleTimeString('en-US', {{ hour12: false }});
        }}

        function addToTranscript(message, isError = false) {{
            const statusDiv = document.getElementById('status');
            const entry = document.createElement('div');
            entry.className = 'transcript-entry' + (isError ? ' transcript-error' : '');
            const timestamp = getTimestamp();
            entry.innerHTML = `<span class="transcript-time">[${{timestamp}}]</span> ${{message}}`;
            statusDiv.appendChild(entry);
            // Auto-scroll to bottom
            statusDiv.scrollTop = statusDiv.scrollHeight;
        }}

        let lastKnownStatus = null;

        async function checkPlaybackStatus() {{
            try {{
                const response = await fetch('/api/status');
                const current = await response.json();

                if (current.status === 'playing' && lastKnownStatus !== 'playing') {{
                    addToTranscript(`Playing: ${{current.song}}`);
                    lastKnownStatus = 'playing';
                }} else if (current.status === 'finished' && lastKnownStatus !== 'finished') {{
                    addToTranscript('Song finished');
                    lastKnownStatus = 'finished';
                    if (statusTimer) {{
                        clearInterval(statusTimer);
                        statusTimer = null;
                    }}
                }} else if (current.status === 'error' && lastKnownStatus !== 'error') {{
                    addToTranscript(`Error: ${{current.message}}`, true);
                    lastKnownStatus = 'error';
                    if (statusTimer) {{
                        clearInterval(statusTimer);
                        statusTimer = null;
                    }}
                }}
            }} catch (error) {{
                addToTranscript(`Error: ${{error.message}}`, true);
                if (statusTimer) {{
                    clearInterval(statusTimer);
                    statusTimer = null;
                }}
            }}
        }}

        async function addToQueue(baseName, title) {{
            try {{
                const response = await fetch('/api/add-to-queue', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ song: baseName, title: title }})
                }});

                if (response.ok) {{
                    const data = await response.json();
                    currentQueue = data.queue;
                    updateQueueDisplay();
                    addToTranscript(`Added "${{title}}" to queue`);
                }} else {{
                    const body = await response.text();
                    addToTranscript(`Error adding song: ${{body}}`, true);
                }}
            }} catch (error) {{
                addToTranscript(`Error: ${{error.message}}`, true);
            }}
        }}

        async function removeFromQueue(index) {{
            try {{
                const response = await fetch('/api/remove-from-queue', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ index: index }})
                }});

                if (response.ok) {{
                    const data = await response.json();
                    currentQueue = data.queue;
                    updateQueueDisplay();
                    addToTranscript('Removed song from queue');
                }} else {{
                    addToTranscript('Error removing song from queue', true);
                }}
            }} catch (error) {{
                addToTranscript(`Error: ${{error.message}}`, true);
            }}
        }}

        function updateQueueDisplay() {{
            const queueDiv = document.getElementById('queue');
            if (currentQueue.length === 0) {{
                queueDiv.textContent = 'No songs in queue';
                return;
            }}
            queueDiv.innerHTML = '';
            currentQueue.forEach((song, index) => {{
                const item = document.createElement('div');
                item.className = 'queue-item';
                item.innerHTML = `
                    <span>${{index + 1}}. ${{song.title}}</span>
                    <button onclick="removeFromQueue(${{index}})">Cancel</button>
                `;
                queueDiv.appendChild(item);
            }});
        }}

        async function playNextFromQueue() {{
            try {{
                const response = await fetch('/api/get-queue');
                const data = await response.json();
                currentQueue = data.queue;

                if (currentQueue.length === 0) {{
                    addToTranscript('Queue is empty', true);
                    return;
                }}

                if (statusTimer) {{
                    clearInterval(statusTimer);
                    statusTimer = null;
                }}

                const nextSong = currentQueue[0];
                addToTranscript('Starting playback...');
                const response2 = await fetch('/api/play', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ song: nextSong.base_name }})
                }});

                if (response2.ok) {{
                    await fetch('/api/remove-from-queue', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ index: 0 }})
                    }});
                    const queueRes = await fetch('/api/get-queue');
                    const queueData = await queueRes.json();
                    currentQueue = queueData.queue;
                    updateQueueDisplay();
                    statusTimer = setInterval(checkPlaybackStatus, 1000);
                    lastKnownStatus = null;
                    await checkPlaybackStatus();
                }} else {{
                    const body = await response2.text();
                    addToTranscript(`Error playing song: ${{body}}`, true);
                }}
            }} catch (error) {{
                addToTranscript(`Error: ${{error.message}}`, true);
            }}
        }}

        async function stopPlayback() {{
            try {{
                if (statusTimer) {{
                    clearInterval(statusTimer);
                    statusTimer = null;
                }}

                addToTranscript('Stopping playback...');
                const response = await fetch('/api/stop', {{ method: 'POST' }});

                if (response.ok) {{
                    addToTranscript('Playback stopped');
                    lastKnownStatus = null;
                }} else {{
                    addToTranscript('Error stopping song', true);
                }}
            }} catch (error) {{
                addToTranscript(`Error: ${{error.message}}`, true);
            }}
        }}

        async function loadQueue() {{
            try {{
                const response = await fetch('/api/get-queue');
                const data = await response.json();
                currentQueue = data.queue;
                updateQueueDisplay();
            }} catch (error) {{
                console.error('Error loading queue:', error);
            }}
        }}

        window.addEventListener('load', () => {{
            loadQueue();
            checkPlaybackStatus();
        }});
    </script>
</body>
</html>
""".format(
    song_list_html=song_list_html)

playback_state = {
    "status": "idle",
    "song": None,
    "message": None,
}
playback_lock = threading.Lock()

queue = []
queue_lock = threading.Lock()


def set_playback_state(status: str, song: str = None, message: str = None):
    with playback_lock:
        playback_state["status"] = status
        playback_state["song"] = song
        playback_state["message"] = message


def add_to_queue(base_name: str, title: str):
    """Add a song to the playback queue."""
    with queue_lock:
        queue.append({"base_name": base_name, "title": title})
        return queue.copy()


def remove_from_queue(index: int):
    """Remove a song from the queue by index."""
    with queue_lock:
        if 0 <= index < len(queue):
            queue.pop(index)
        return queue.copy()


def get_queue():
    """Get a copy of the current queue."""
    with queue_lock:
        return queue.copy()


class KaraokeRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for the karaoke server."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/":
            self.serve_html()
        elif path == "/api/status":
            self.serve_status()
        elif path == "/api/get-queue":
            self.serve_queue()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/api/play":
            self.handle_play_request()
        elif path == "/api/stop":
            self.handle_stop_request()
        elif path == "/api/add-to-queue":
            self.handle_add_to_queue_request()
        elif path == "/api/remove-from-queue":
            self.handle_remove_from_queue_request()
        else:
            self.send_error(404)

    def serve_html(self):
        """Serve the HTML UI."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(ui_html.encode())

    def serve_status(self):
        """Serve the current playback status."""
        with playback_lock:
            current_state = playback_state.copy()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(current_state).encode())

    def serve_queue(self):
        """Serve the current queue."""
        current_queue = get_queue()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"queue": current_queue}).encode())

    def start_playback(self, video_path: Path, _audio_path: Path, title: str):
        """Run playback and update status when it finishes or errors."""
        try:
            player.play_karaoke(str(video_path))
            set_playback_state("finished", title, None)
        except Exception as e:
            set_playback_state("error", title, str(e))

    def handle_play_request(self):
        """Handle song playback request."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode())
            song_base_name = data.get("song")

            if not song_base_name:
                self.send_error(400, "Missing 'song' parameter")
                return

            # Check if a song is already playing
            with playback_lock:
                if playback_state["status"] == "playing":
                    self.send_error(400, "A song is already playing")
                    return

            song = next(
                (s for s in songlist.songs if s["base_name"] == song_base_name),
                None)
            if not song:
                self.send_error(404, "Song not found")
                return

            # Stop any current playback before starting a new song.
            player.stop_karaoke()
            set_playback_state("playing", song["title"], None)

            # Send response before playing (non-blocking)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Playing", "song": song["title"]}).encode())

            # Play in background thread to allow server to remain responsive
            thread = threading.Thread(
                target=self.start_playback,
                args=(song["video"], song["audio"], song["title"]),
                daemon=True
            )
            thread.start()

        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, str(e))

    def handle_stop_request(self):
        """Handle stop playback requests."""
        try:
            with playback_lock:
                current_song = playback_state.get("song")

            player.stop_karaoke()
            set_playback_state("finished", current_song, None)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "finished", "song": current_song}).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def handle_add_to_queue_request(self):
        """Handle adding a song to the queue."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode())
            base_name = data.get("song")
            title = data.get("title")

            if not base_name or not title:
                self.send_error(400, "Missing 'song' or 'title' parameter")
                return

            current_queue = add_to_queue(base_name, title)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "added", "queue": current_queue}).encode())
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, str(e))

    def handle_remove_from_queue_request(self):
        """Handle removing a song from the queue."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode())
            index = data.get("index")

            if index is None:
                self.send_error(400, "Missing 'index' parameter")
                return

            current_queue = remove_from_queue(index)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "removed", "queue": current_queue}).encode())
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        """Log HTTP requests."""
        print(f"[SERVER] {format % args}")


def start_server(port: int = 8000):
    """Start the HTTP server."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, KaraokeRequestHandler)
    print(f"Karaoke Server running on http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    start_server()
