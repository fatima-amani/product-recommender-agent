import tempfile
import whisper

# Load Whisper model once (tiny for speed, base for accuracy)
model = whisper.load_model("base")

def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe recorded audio bytes to text using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio.flush()
        result = model.transcribe(temp_audio.name)
        return result.get("text", "").strip()
