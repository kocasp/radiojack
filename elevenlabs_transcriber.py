import os
from elevenlabs.client import ElevenLabs

class ElevenLabsTranscriber:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API key not found. Provide it explicitly or set ELEVENLABS_API_KEY in .env")
        self.client = ElevenLabs(api_key=self.api_key)

    def transcribe(self, audio_path: str, model_id: str = "scribe_v1", tag_audio_events: bool = True) -> str:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        result = self.client.speech_to_text.convert(
            file=audio_data,
            model_id=model_id,
            # tag_audio_events=tag_audio_events
            # You can expose additional options like language_code or diarize as method parameters
        )
        return result.text
