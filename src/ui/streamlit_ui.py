import streamlit as st
import asyncio
from services.adk_service import initialize_adk, run_adk_async
from constants import MESSAGE_HISTORY_KEY

async def handle_user_message(adk_runner, session_id, prompt):
    """
    Handles the user message asynchronously, updating Streamlit placeholders dynamically.
    """
    # Placeholder for tool loader and tool responses
    tool_placeholder = st.empty()
    # Placeholder for the final assistant response
    response_placeholder = st.empty()

    async for event in run_adk_async(adk_runner, session_id, prompt):
        # TOOL CALL
        if event["type"] == "tool_call":
            with tool_placeholder.container():
                st.markdown(f"⚙️ Calling tool: **{event['name']}** ...")

        # TOOL RESPONSE (update same placeholder)
        elif event["type"] == "tool_response":
            with tool_placeholder.container():
                st.markdown(f"✅ Tool response received for **{event['name']}**")

        # FINAL RESPONSE (clear tool placeholder)
        elif event["type"] == "final_response":
            tool_placeholder.empty()  # remove loader/tool messages
            response_placeholder.markdown(event["text"])  # display final response
            return event["text"]

def run_streamlit_app():
    """
    Sets up and runs the Streamlit web application for the ADK chat assistant.
    """
    st.set_page_config(page_title="Product Recommender Agent", layout="wide")
    st.title("Product Recommender Agent")
    st.markdown("Developed by Fatima")
    st.divider()

    # Initialize ADK runner and session ID
    adk_runner, current_session_id = initialize_adk()
    
    st.divider()
    st.subheader("Chat with the Assistant")

    # Initialize chat message history
    if MESSAGE_HISTORY_KEY not in st.session_state:
        st.session_state[MESSAGE_HISTORY_KEY] = []

    # Display chat history
    for message in st.session_state[MESSAGE_HISTORY_KEY]:
        with st.chat_message(message["role"]):  # user vs assistant bubble
            st.markdown(message["content"])

    # Handle new user input
    if prompt := st.chat_input("Ask something..."):
        # Display user message
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant bubble and handle tool loader + response
        with st.chat_message("assistant") as assistant_container:
            # Pass the container to placeholders inside async function
            final_response = asyncio.run(handle_user_message(adk_runner, current_session_id, prompt))

        # Store assistant message in session state
        st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": final_response})
