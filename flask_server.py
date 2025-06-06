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
    <script>
        function togglePlay(button) {
            const audio = document.getElementById('audioPlayer');
            if (audio.paused) {
                audio.play();
                button.textContent = '';  // Pause icon
            } else {
                audio.pause();
                button.textContent = '►';  // Play icon
            }

            // Sync button state with audio events
            audio.onended = () => {
                button.textContent = '►';
            };
        }
    </script>
</head>
<body class="terminal">
    <div class="container">
        <button onclick="location.href='{{ url_for('list_wav_files') }}'" class="small_button"><</button>
        <button onclick="togglePlay(this)" class="small_button">►</button>
        <p><a href="{{ url_for('list_wav_files') }}">← Back to List</a></p>
        <h2>Recording: {{ filename }}</h2>
        <audio id="audioPlayer" style="width: 100%;">
            <source src="{{ url_for('static', filename='recordings/' + filename) }}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
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
