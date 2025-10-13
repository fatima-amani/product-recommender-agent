# speech/tts_service.py
from gtts import gTTS
import tempfile

def text_to_speech(text: str) -> bytes:
    """Convert text to speech (MP3) using gTTS and return audio bytes."""
    if not text.strip():
        return b""
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tts.save(tmp.name)
        tmp.seek(0)
        audio_bytes = tmp.read()
    return audio_bytes