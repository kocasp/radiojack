# elevenlabs_transcribe.py
import os
import sys
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables from .env file
load_dotenv()

# Get audio file path from command-line argument
if len(sys.argv) < 2:
    print("Usage: python elevenlabs_transcribe.py <audio_file_path>")
    sys.exit(1)

audio_path = sys.argv[1]

# Initialize ElevenLabs client with API key from environment
elevenlabs = ElevenLabs(
    api_key="sk_7b0db686fe3aed6a11e7402eae4d339c2e71db64515a131f",
)

# Open and read the audio file as binary
try:
    with open(audio_path, "rb") as f:
        audio_data = f.read()
except FileNotFoundError:
    print(f"Error: File '{audio_path}' not found.")
    sys.exit(1)

# Transcribe the audio
transcription = elevenlabs.speech_to_text.convert(
    file=audio_data,
    model_id="scribe_v1",         # Required
    tag_audio_events=True,        # Optional
    # language_code="eng",          # Optional (auto-detect if None)
    # diarize=True                  # Optional
)

# Print the transcription result
print(transcription.text)

