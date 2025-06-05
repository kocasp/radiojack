import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import queue
import os

# Settings
SAMPLE_RATE = 16000
THRESHOLD = 0.01
SILENCE_TIMEOUT = 3  # seconds
CHUNK_DURATION = 0.5  # seconds
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
OUTPUT_FOLDER = "recordings"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

audio_q = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(status)
    audio_q.put(indata.copy())

def rms(data):
    return np.sqrt(np.mean(data**2))

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
                        filename = os.path.join(OUTPUT_FOLDER, f"recording_{int(time.time())}.wav")
                        wav.write(filename, SAMPLE_RATE, (full_recording * 32767).astype(np.int16))
                        print(f"Saved: {filename}")
                        is_recording = False
                        silence_start = None

        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    record_on_sound()


