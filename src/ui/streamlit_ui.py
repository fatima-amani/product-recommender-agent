import streamlit as st
import asyncio
import time
from streamlit_mic_recorder import mic_recorder
from services.adk_service import initialize_adk, run_adk_async
from constants import MESSAGE_HISTORY_KEY
from services.stt_service import transcribe_audio
from services.tts_service import text_to_speech


async def handle_user_message(adk_runner, session_id, prompt):
    """Handles user message asynchronously, updating Streamlit placeholders."""
    tool_placeholder = st.empty()
    response_placeholder = st.empty()

    async for event in run_adk_async(adk_runner, session_id, prompt):
        if event["type"] == "tool_call":
            with tool_placeholder.container():
                st.markdown(f"⚙️ Calling tool: **{event['name']}** ...")

        elif event["type"] == "tool_response":
            with tool_placeholder.container():
                st.markdown(f"✅ Tool response received for **{event['name']}**")

        elif event["type"] == "final_response":
            tool_placeholder.empty()
            response_placeholder.markdown(event["text"])
            return event["text"]


def run_streamlit_app():
    """Run the Streamlit web app for the ADK chat assistant."""
    st.set_page_config(page_title="Product Recommender Agent", layout="wide")
    st.title("🛍️ Product Recommender Agent — Voice Conversation Mode")
    st.markdown("Developed by Fatima — now with continuous voice chat 🗣️🤖")
    st.divider()

    adk_runner, current_session_id = initialize_adk()

    st.divider()
    st.subheader("💬 Talk with your Assistant")

    if MESSAGE_HISTORY_KEY not in st.session_state:
        st.session_state[MESSAGE_HISTORY_KEY] = []

    # Show message history
    for msg in st.session_state[MESSAGE_HISTORY_KEY]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # === 🎧 Conversation Mode Toggle ===
    continuous = st.toggle("Enable continuous voice conversation 🔁", value=False)
    st.write("🎙️ Click 'Start Recording' to begin talking." if not continuous else "🗣️ Continuous mode is ON.")

    # === Microphone Recorder ===
    audio_data = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="recorder",
        just_once=False,
    )


    user_input = None

    if audio_data:
        st.info("Transcribing your voice...")
        user_input = transcribe_audio(audio_data["bytes"])
        if user_input:
            st.success(f"🗣️ You said: *{user_input}*")

    # === Manual Text Input (fallback) ===
    text_prompt = st.chat_input("Or type your question here...")
    if text_prompt:
        user_input = text_prompt

    if user_input:
        # Display user message
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process message
        with st.chat_message("assistant"):
            final_response = asyncio.run(handle_user_message(adk_runner, current_session_id, user_input))
            st.markdown(final_response)

            # 🔊 Convert response to speech
            with st.spinner("Converting response to voice..."):
                audio_bytes = text_to_speech(final_response)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

        # Save to history
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": final_response})

        # If conversation mode enabled, short delay → auto restart recording
        if continuous:
            time.sleep(1.5)
            st.experimental_rerun()
