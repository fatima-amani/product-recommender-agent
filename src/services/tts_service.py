from deepgram import DeepgramClient
import os

def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech using Deepgram's TTS API and return audio as bytes.
    
    Args:
        text: The text to convert to speech
        
    Returns:
        bytes: Audio data in MP3 format
        
    Raises:
        Exception: If the API request fails
    """
    try:
        # STEP 1: Create a Deepgram client using the API key from environment variables
        deepgram = DeepgramClient()

        # STEP 2: Call the generate method on the speak property (returns a generator)
        response = deepgram.speak.v1.audio.generate(
            text=text,
            model="aura-2-thalia-en"
        )

        # STEP 3: Collect all the bytes from the generator
        audio_chunks = []
        for chunk in response:
            audio_chunks.append(chunk)
        
        # STEP 4: Combine all chunks into a single bytes object
        audio_bytes = b''.join(audio_chunks)
        
        return audio_bytes

    except Exception as e:
        print(f"Exception: {e}")
        raise