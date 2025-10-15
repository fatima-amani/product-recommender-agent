import streamlit as st
import asyncio
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
    st.set_page_config(page_title="Product Recommender Agent", layout="centered")
    st.title("🛍️ Product Recommender Agent")
    st.markdown("I'm your smart product assistant. Ask me for recommendations, or tell me what you're looking for!")

    adk_runner, current_session_id = initialize_adk()

    if MESSAGE_HISTORY_KEY not in st.session_state:
        st.session_state[MESSAGE_HISTORY_KEY] = []

    # Display message history
    for msg in st.session_state[MESSAGE_HISTORY_KEY]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Handle user input from voice or text ---
    user_input = None

    # Voice input via sidebar
    with st.sidebar:
        st.subheader("🎙️ Voice Input")
        st.write("Click the button below to record your question.")
        audio_data = mic_recorder(
            start_prompt="Start Recording",
            stop_prompt="Stop Recording",
            key="recorder",
            just_once=False,
        )

    if audio_data:
        with st.spinner("Transcribing your voice..."):
            try:
                user_input = transcribe_audio(audio_data["bytes"])
                st.sidebar.success(f"🗣️ You said: *{user_input}*")
            except Exception as e:
                st.sidebar.error(f"Transcription failed: {e}")
    
    # Text input via main chat interface
    if text_prompt := st.chat_input("Ask a question..."):
        if not user_input: # Prioritize voice input if available
             user_input = text_prompt

    # --- Process and display messages ---
    if user_input:
        # Display user message and save to history
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process message and display assistant response
        with st.chat_message("assistant"):
            final_response = asyncio.run(handle_user_message(adk_runner, current_session_id, user_input))
            
            if final_response:
                # Save assistant response to history
                st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": final_response})

                # Convert response to speech and play it
                with st.spinner("Generating voice..."):
                    audio_bytes = text_to_speech(final_response)
                    if audio_bytes:
                        st.markdown('''<style>.stAudio { display: none; }</style>''', unsafe_allow_html=True)
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            else:
                st.warning("The assistant did not provide a response.")
