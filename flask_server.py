from flask import Flask, render_template_string, url_for
import os
from datetime import datetime

app = Flask(__name__)
RECORDINGS_DIR = 'recordings'
app.static_folder = '.'  # Serve /recordings and /static properly

# Home page template
TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta http-equiv="refresh" content="10">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="{{ url_for('static', filename='css/terminal.css') }}" rel="stylesheet">
    <style>
        * { user-select: none; }
        .container { -webkit-overflow-scrolling: touch; overscroll-behavior: contain; }
    </style>
    <script>
        ['keydown', 'keypress', 'keyup'].forEach(event => {
            window.addEventListener(event, e => {
                e.stopPropagation(); e.preventDefault();
            }, true);
        });
    </script>
</head>
<body class="terminal">
    <div class="container">
        {% if wav_files %}
            {% for file, readable in wav_files %}
                <button onclick="location.href='{{ url_for('recording_detail', filename=file) }}'" class="recording_button">[ {{ readable }} ]</button>
            {% endfor %}
        {% else %}
            <p><i>No recordings files found. Connect your radio to start receiving signals.</i></p>
        {% endif %}
    </div>
</body>
</html>
"""

# Detail page template
DETAIL_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <title>Recording Detail</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="{{ url_for('static', filename='css/terminal.css') }}" rel="stylesheet">
    <style>
        * { user-select: none; }
        html, body { height: 100%; margin: 0; padding: 0; overflow: hidden; }
        .container { display: flex; flex-direction: column; height: 100%; }
        .top-bar { position: sticky; top: 0; z-index: 10; padding: 10px 10px 0 10px; }
        #progressBar { width: 100%; }
        .scrollable-content { flex: 1; overflow-y: auto; padding: 10px; -webkit-overflow-scrolling: touch; overscroll-behavior: contain; }
    </style>
    <script>
        let audio, progressBar;

        window.onload = () => {
            audio = document.getElementById('audioPlayer');
            progressBar = document.getElementById('progressBar');

            audio.addEventListener('timeupdate', () => {
                progressBar.value = (audio.currentTime / audio.duration) * 100 || 0;
            });

            progressBar.addEventListener('input', () => {
                audio.currentTime = (progressBar.value / 100) * audio.duration;
            });

            typewriterEffect();
        };

        function togglePlay(button) {
            if (audio.paused) {
                audio.play();
                button.textContent = '❚❚';
            } else {
                audio.pause();
                button.textContent = '►';
            }
            audio.onended = () => button.textContent = '►';
            audio.onpause = () => { if (!audio.ended) button.textContent = '►'; };
        }

        function typewriterEffect() {
            const container = document.getElementById("typewriterText");
            const fullHTML = container.getAttribute("data-content") || "";
            const words = fullHTML.split(/(\\s+)/);  // keep spaces
            container.innerHTML = "";
            container.style.visibility = "visible";

            let i = 0;
            function addWord() {
                if (i < words.length) {
                    container.innerHTML += words[i];
                    i++;
                    setTimeout(addWord, 30);
                }
            }

            addWord();
        }
    </script>
</head>
<body class="terminal">
    <div class="container">
        <div class="top-bar">
            <div style="display: flex; align-items: center; gap: 10px;">
                <button onclick="location.href='{{ url_for('list_wav_files') }}'" class="small_button"><</button>
                <button onclick="togglePlay(this)" class="small_button">►</button>
                <input class="jack_player" type="range" id="progressBar" min="0" max="100" value="0" style="flex: 1;">
            </div>
            <h2 id="headline" style="margin: 10px 0;">Rec: {{ readable_timestamp }}</h2>
        </div>

        <div class="scrollable-content">
            <audio id="audioPlayer" style="display: none;" controls>
                <source src="{{ url_for('static', filename='recordings/' + filename) }}" type="audio/wav">
                Your browser does not support the audio element.
            </audio>
            <blockquote>
                <p id="typewriterText" data-content="{{ text_content | e }}" style="visibility: hidden;"></p>
            </blockquote>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def list_wav_files():
    if not os.path.exists(RECORDINGS_DIR):
        os.makedirs(RECORDINGS_DIR)
    files = os.listdir(RECORDINGS_DIR)
    wav_files = [f for f in files if f.lower().endswith('.wav')]

    # Convert timestamps to readable format
    readable_files = []
    for f in wav_files:
        try:
            ts = int(f.replace('.wav', ''))
            readable = datetime.fromtimestamp(ts).strftime("%H:%M:%S %d.%m.%Y")
            readable_files.append((f, readable))
        except ValueError:
            readable_files.append((f, f.replace('.wav', '')))  # fallback

    # Optional: sort newest first
    readable_files.sort(reverse=True)

    return render_template_string(TEMPLATE, wav_files=readable_files)

@app.route('/recording/<filename>')
def recording_detail(filename):
    txt_filename = filename.rsplit('.', 1)[0] + '.txt'
    txt_path = os.path.join(RECORDINGS_DIR, txt_filename)

    text_content = ''
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
    else:
        text_content = '[ No transcription text found. ]'

    try:
        readable_timestamp = datetime.fromtimestamp(int(filename.replace('.wav', ''))).strftime("%H:%M:%S %d.%m.%Y")
    except ValueError:
        readable_timestamp = filename.replace('.wav', '')

    return render_template_string(DETAIL_TEMPLATE, filename=filename, text_content=text_content, readable_timestamp=readable_timestamp)

if __name__ == '__main__':
    app.run(debug=True)
