import streamlit as st
import asyncio
from streamlit_mic_recorder import mic_recorder
from services.adk_service import initialize_adk, run_adk_async
from constants import MESSAGE_HISTORY_KEY
from services.stt_service import transcribe_audio
from services.tts_service import text_to_speech


async def get_assistant_response(adk_runner, session_id, prompt):
    """
    Gets assistant response. In this version, we don't stream tool usage to the main UI 
    to keep the display logic simple. A spinner will be shown instead.
    """
    final_text = ""
    async for event in run_adk_async(adk_runner, session_id, prompt):
        if event["type"] == "final_response":
            final_text = event.get("text", "")
    return final_text


def run_streamlit_app():
    """Run the Streamlit web app for the ADK chat assistant."""
    st.set_page_config(page_title="Product Recommender Agent", layout="centered")
    st.title("🛍️ Product Recommender Agent")
    st.markdown("I'm your smart product assistant. Ask me for recommendations, or tell me what you're looking for!")

    adk_runner, current_session_id = initialize_adk()

    if MESSAGE_HISTORY_KEY not in st.session_state:
        st.session_state[MESSAGE_HISTORY_KEY] = []

    # --- Display chat history ---
    for msg in st.session_state[MESSAGE_HISTORY_KEY]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Autoplay audio from the last response ---
    if "autoplay_audio" in st.session_state:
        audio_bytes = st.session_state.pop("autoplay_audio")
        st.markdown('<style>.stAudio { display: none; }</style>', unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # --- Handle user input (voice or text) ---
    user_input = None
    if "user_input_from_voice" in st.session_state:
        user_input = st.session_state.pop("user_input_from_voice")
    with st.sidebar:
        st.subheader("🎙️ Voice Input")
        st.write("Click the button below to record your question.")
        audio_data = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", key="recorder", just_once=False)
    if audio_data:
        with st.spinner("Transcribing your voice..."):
            try:
                transcribed_text = transcribe_audio(audio_data["bytes"])
                st.session_state["user_input_from_voice"] = transcribed_text
                st.sidebar.success(f"🗣️ You said: *{transcribed_text}*")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Transcription failed: {e}")
    if text_prompt := st.chat_input("Ask a question..."):
        if not user_input:
             user_input = text_prompt

    # --- State Machine: Process new input and generate responses ---

    # 1. If there is new user input, add it to history and rerun to display it immediately.
    if user_input:
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "user", "content": user_input})
        st.rerun()

    # 2. If the last message is from the user, generate a response from the agent.
    if st.session_state[MESSAGE_HISTORY_KEY] and st.session_state[MESSAGE_HISTORY_KEY][-1]["role"] == "user":
        last_user_message = st.session_state[MESSAGE_HISTORY_KEY][-1]["content"]
        
        with st.spinner("Thinking..."):
            final_response = asyncio.run(get_assistant_response(adk_runner, current_session_id, last_user_message))

        if final_response:
            with st.spinner("Generating voice..."):
                audio_bytes = text_to_speech(final_response)
            st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": final_response})
            if audio_bytes:
                st.session_state["autoplay_audio"] = audio_bytes
        else:
            st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": "Sorry, I had trouble generating a response."})
        
        st.rerun()