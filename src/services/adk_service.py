import streamlit as st
import asyncio
import time
import os
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types
from agent.agent import create_product_recommender_agent
from constants import APP_NAME_FOR_ADK, USER_ID, INITIAL_STATE, ADK_SESSION_KEY

@st.cache_resource
def get_session_service():
    return InMemorySessionService()

@st.cache_resource
def get_runner():
    root_agent = create_product_recommender_agent()
    session_service = get_session_service()
    return Runner(agent=root_agent, app_name=APP_NAME_FOR_ADK, session_service=session_service)

def initialize_adk():
    runner = get_runner()
    session_service = runner.session_service

    if ADK_SESSION_KEY not in st.session_state:
        session_id = f"streamlit_adk_session_{int(time.time())}_{os.urandom(4).hex()}"
        st.session_state[ADK_SESSION_KEY] = session_id

        asyncio.run(session_service.create_session(
            app_name=APP_NAME_FOR_ADK,
            user_id=USER_ID,
            session_id=session_id,
            state=INITIAL_STATE
        ))
    else:
        session_id = st.session_state[ADK_SESSION_KEY]
        # Verify session still exists
        session = asyncio.run(session_service.get_session(
            app_name=APP_NAME_FOR_ADK,
            user_id=USER_ID,
            session_id=session_id
        ))
        if not session:
            asyncio.run(session_service.create_session(
                app_name=APP_NAME_FOR_ADK,
                user_id=USER_ID,
                session_id=session_id,
                state=INITIAL_STATE
            ))

    return runner, session_id

async def run_adk_async(runner: Runner, session_id: str, user_message_text: str):
    session = await runner.session_service.get_session(
        app_name=APP_NAME_FOR_ADK, user_id=USER_ID, session_id=session_id
    )
    if not session:
        yield {"type": "error", "text": "ADK session not found."}
        return

    content = genai_types.Content(role='user', parts=[genai_types.Part(text=user_message_text)])

    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=content):
        # TOOL CALL
        if event.get_function_calls():
            for fc in event.get_function_calls():
                yield {"type": "tool_call", "name": fc.name}

        # TOOL RESPONSE
        if event.get_function_responses():
            for fr in event.get_function_responses():
                yield {"type": "tool_response", "name": fr.name}

        # FINAL RESPONSE
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text
            yield {"type": "final_response", "text": final_text}
            break

def run_adk_sync(runner: Runner, session_id: str, user_message_text: str) -> str:
    """
    Synchronous wrapper for running ADK, as Streamlit does not directly support async calls in the main thread.
    """
    # Runs the asynchronous function in a new event loop.
    return asyncio.run(run_adk_async(runner, session_id, user_message_text))
