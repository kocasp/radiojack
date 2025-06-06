from flask import Flask, render_template_string, url_for
import os

app = Flask(__name__)
RECORDINGS_DIR = 'recordings'
app.static_folder = '.'  # Serve /recordings and /static properly

# Home page
TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta http-equiv="refresh" content="200">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="{{ url_for('static', filename='css/terminal.css') }}" rel="stylesheet">
</head>
<body class="terminal">
    <div class="container">
        {% if wav_files %}
            {% for file in wav_files %}
                <button onclick="location.href='{{ url_for('recording_detail', filename=file) }}'" class="recording_button">[ {{ file.replace('.wav', '') }} ]</button>
            {% endfor %}
        {% else %}
            <p><i>No WAV files found in the <code>/recordings</code> directory.</i></p>
        {% endif %}
    </div>
</body>
</html>
"""

# Detail page
DETAIL_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <title>Recording Detail</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="{{ url_for('static', filename='css/terminal.css') }}" rel="stylesheet">
    <style>
        #progressBar {
            width: 100%;
            margin-top: 10px;
        }
    </style>
    <script>
        let audio, progressBar;

        window.onload = () => {
            audio = document.getElementById('audioPlayer');
            progressBar = document.getElementById('progressBar');

            // Sync progress bar with audio
            audio.addEventListener('timeupdate', () => {
                progressBar.value = (audio.currentTime / audio.duration) * 100 || 0;
            });

            // Update audio time when user moves the bar
            progressBar.addEventListener('input', () => {
                audio.currentTime = (progressBar.value / 100) * audio.duration;
            });
        };

        function togglePlay(button) {
            if (audio.paused) {
                audio.play();
                button.textContent = '❚❚';  // Pause icon
            } else {
                audio.pause();
                button.textContent = '►';  // Play icon
            }

            audio.onended = () => {
                button.textContent = '►';
            };
            audio.onpause = () => {
                if (!audio.ended) {
                    button.textContent = '►';
                }
            };
        }
    </script>
</head>
<body class="terminal">
    <div class="container">
        <div style="display: flex; align-items: center; gap: 10px;">
            <button onclick="location.href='{{ url_for('list_wav_files') }}'" class="small_button"><</button>
            <button onclick="togglePlay(this)" class="small_button">►</button>
            <input class="jack_player" type="range" id="progressBar" min="0" max="100" value="0" style="flex: 1;">
        </div>
        <h2 id="headline" >Recording: {{ filename.replace('.wav', '') }}</h2>

        <audio id="audioPlayer" style="display: none;">
            <source src="{{ url_for('static', filename='recordings/' + filename) }}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        <blockquote>
            <p>
                The blockquote element represents content that is quoted from
                another source, optionally with a citation which must be within a
                <code>footer</code> or <code>cite</code> element, and optionally
                with in-line changes such as annotations and abbreviations.
            </p>
        </blockquote>
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
    return render_template_string(TEMPLATE, wav_files=wav_files)

@app.route('/recording/<filename>')
def recording_detail(filename):
    return render_template_string(DETAIL_TEMPLATE, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
