import os
from deepgram import DeepgramClient

# Initialize Deepgram client once
# Make sure to set DEEPGRAM_API_KEY environment variable
deepgram = DeepgramClient()

def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe recorded audio bytes to text using Deepgram."""
    try:
        # Call Deepgram's transcribe_file method with the audio bytes
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model="nova-3",  # You can change this to other models like "base", "enhanced", etc.
            smart_format=True,
            language="en"  # Optional: specify language for better accuracy
        )
        
        # Extract transcription text from response
        if hasattr(response, 'results') and hasattr(response.results, 'channels'):
            transcript = response.results.channels[0].alternatives[0].transcript
            return transcript.strip()
        else:
            return ""
            
    except Exception as e:
        print(f"Deepgram transcription error: {e}")
        return ""

# Alternative version if you need to handle the response differently:
def transcribe_audio_alternative(audio_bytes: bytes) -> str:
    """Alternative implementation with more error handling."""
    try:
        response = deepgram.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model="nova-3",
            smart_format=True
        )
        
        # Convert response to dict and extract transcription
        response_data = response.to_dict()
        transcript = response_data['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript.strip()
        
    except Exception as e:
        print(f"Deepgram transcription error: {e}")
        return ""
