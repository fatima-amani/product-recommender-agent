LLM_MODEL="gemini-2.5-flash"

ROOT_AGENT_MODEL=LLM_MODEL
NEO4J_TOOL_MODEL=LLM_MODEL
MONGO_TOOL_MODEL="gemini-2.5-flash-lite"

ROOT_AGENT_TEMPERATURE=0.1
NEO4J_TOOL_TEMPERATURE=0.1
MONGO_TOOL_TEMPERATURE=0.1

APP_NAME_FOR_ADK = "Product Recommender App" # A unique name for your application within ADK, used for session management.
USER_ID = "fatima" # A default user ID. In a real application, this would be dynamic (e.g., from a login system).
# Defines the initial state for new ADK sessions. This provides default values for user information.
INITIAL_STATE = {}


MESSAGE_HISTORY_KEY = "messages_final_mem_v2" # Key used by Streamlit to store the chat history in its session state.
ADK_SESSION_KEY = "adk_session_id" # Key used by Streamlit to store the unique ADK session ID.
