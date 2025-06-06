import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import queue
import os
from datetime import datetime
from elevenlabs_transcriber import ElevenLabsTranscriber

# Settings
SAMPLE_RATE = 16000
THRESHOLD = 0.01
SILENCE_TIMEOUT = 3  # seconds
CHUNK_DURATION = 0.5  # seconds
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
OUTPUT_FOLDER = "recordings"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

audio_q = queue.Queue()
transcriber = ElevenLabsTranscriber(api_key= "sk_7b0db686fe3aed6a11e7402eae4d339c2e71db64515a131f")

def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_q.put(indata.copy())

def rms(data):
    return np.sqrt(np.mean(data**2))

def transcribe_and_save(file_path: str):
    try:
        print(f"Transcribing: {file_path}")
        text = transcriber.transcribe(file_path)
        print(f"Transcription:\n{text}\n{'-'*50}")

        # Save transcription to .txt file
        txt_path = os.path.splitext(file_path)[0] + ".txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved transcription: {txt_path}")

    except Exception as e:
        print(f"Error transcribing {file_path}: {e}")

def record_on_sound():
    print("Listening for any sound...")
    recording = []
    is_recording = False
    silence_start = None

    with sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE, blocksize=CHUNK_SIZE):
        try:
            while True:
                chunk = audio_q.get()
                volume = rms(chunk)

                if volume > THRESHOLD:
                    if not is_recording:
                        print("Sound detected, recording...")
                        recording = []
                        is_recording = True
                    recording.append(chunk)
                    silence_start = None
                elif is_recording:
                    recording.append(chunk)
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > SILENCE_TIMEOUT:
                        full_recording = np.concatenate(recording, axis=0)
                        timestamp = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
                        filename = os.path.join(OUTPUT_FOLDER, f"{timestamp}.wav")
                        wav.write(filename, SAMPLE_RATE, (full_recording * 32767).astype(np.int16))
                        print(f"Saved: {filename}")
                        transcribe_and_save(filename)
                        is_recording = False
                        silence_start = None

        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    record_on_sound()
