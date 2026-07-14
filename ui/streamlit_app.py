"""
Streamlit frontend for the RAG Chat System.

Provides a chat-style UI that sends user messages to the FastAPI
backend and displays the conversation. Includes a sidebar for
starting a new session or resuming any previous session, using
the /sessions and /history endpoints already exposed by the backend.
"""

import streamlit as st
import requests
import uuid

st.set_page_config(page_title="RAG Chat", page_icon="💬")
st.title("💬 RAG Chat System")

# Base URL of the FastAPI backend; individual endpoints are built from this.
BASE_URL = "http://localhost:8000"
CHAT_URL = f"{BASE_URL}/chat"
SESSIONS_URL = f"{BASE_URL}/sessions"
HISTORY_URL = f"{BASE_URL}/history"

# Create a session ID that persists for the duration of this browser session.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Local (client-side) copy of the conversation, used purely for rendering the UI.
if "messages" not in st.session_state:
    st.session_state.messages = []


def load_session(session_id: str):
    """
    Switch the active chat to a given session ID and pull its full
    message history from the backend so it renders in the UI.
    """
    st.session_state.session_id = session_id
    try:
        response = requests.get(f"{HISTORY_URL}/{session_id}")
        st.session_state.messages = response.json().get("messages", [])
    except requests.exceptions.ConnectionError:
        st.session_state.messages = []
        st.sidebar.error("Could not reach backend to load history.")


def start_new_session():
    """Reset to a brand new, empty session."""
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []


# ----- Sidebar: session management -----
with st.sidebar:
    st.header("Session")

    st.markdown(f"**Current:** `{st.session_state.session_id}`")

    st.subheader("Resume a past session")

    try:
        sessions_response = requests.get(SESSIONS_URL)
        all_sessions = sessions_response.json().get("sessions", [])
    except requests.exceptions.ConnectionError:
        all_sessions = []
        st.error("Backend not reachable. Is uvicorn running on port 8000?")

    # Dropdown options: "(new session)" first, followed by all past session IDs.
    dropdown_options = ["(new session)"] + all_sessions

    selected = st.selectbox(
        "Resume a past session",
        options=dropdown_options,
        index=0,
        label_visibility="collapsed",
    )

    # If the user picked an existing session from the dropdown, load it.
    if selected != "(new session)" and selected != st.session_state.session_id:
        load_session(selected)
        st.rerun()

    if st.button("Start new session"):
        start_new_session()
        st.rerun()

# ----- Main chat area -----

# Re-render the full chat history on every Streamlit rerun.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box pinned to the bottom of the page.
user_input = st.chat_input("Ask a question...")

if user_input:
    # Display the user's message immediately.
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send the message to the backend and display the assistant's reply.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(CHAT_URL, json={
                    "session_id": st.session_state.session_id,
                    "message": user_input
                })
                answer = response.json().get("answer", "Sorry, something went wrong.")
            except requests.exceptions.ConnectionError:
                answer = "⚠️ Could not reach the backend. Make sure `uvicorn app.main:app --reload` is running."
        st.markdown(answer)

    # Save the assistant's reply to the local session state for re-rendering.
    st.session_state.messages.append({"role": "assistant", "content": answer})