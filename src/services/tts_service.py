from deepgram import DeepgramClient

import os
from dotenv import load_dotenv

from utils.llm_utils import run_llm
from constants import TTS_MINI_LLM_MODEL, ENABLE_TTS
from models.tts import TTSTextModel
from utils.prompts.tts import generate_tts_text_prompt

load_dotenv()

def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech using Deepgram's TTS API and return audio as bytes.
    """
    if not ENABLE_TTS:
        return None
    try:
        # run llm
        tts_text = run_llm(
            llm_model=TTS_MINI_LLM_MODEL,
            pydantic_model=TTSTextModel,
            system_msg=generate_tts_text_prompt(),
            human_msg=f"Text: {text}"
        )

        tts_text = tts_text.text.strip()

        deepgram = DeepgramClient()

        response = deepgram.speak.v1.audio.generate(
            text=tts_text,
            model="aura-2-thalia-en"
        )

        audio_chunks = []
        for chunk in response:
            audio_chunks.append(chunk)
        
        audio_bytes = b''.join(audio_chunks)
        
        return audio_bytes

    except Exception as e:
        print(f"Exception with TTS model: \n{e}")
        return None