import streamlit as st
import requests
import uuid

st.set_page_config(page_title="RAG Chat", page_icon="💬")
st.title("💬 RAG Chat System")

API_URL = "http://localhost:8000/chat"
HISTORY_URL = "http://localhost:8000/history"
SESSIONS_URL = "http://localhost:8000/sessions"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: resume a previous session
with st.sidebar:
    st.subheader("Session")
    st.caption(f"Current: `{st.session_state.session_id}`")

    try:
        sessions = requests.get(SESSIONS_URL).json().get("sessions", [])
    except Exception:
        sessions = []

    if sessions:
        chosen = st.selectbox("Resume a past session", ["(new session)"] + sessions)
        if chosen != "(new session)" and chosen != st.session_state.session_id:
            if st.button("Load this session"):
                st.session_state.session_id = chosen
                history = requests.get(f"{HISTORY_URL}/{chosen}").json().get("messages", [])
                st.session_state.messages = history
                st.rerun()

    if st.button("Start new session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask a question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = requests.post(API_URL, json={
                "session_id": st.session_state.session_id,
                "message": user_input
            })
            answer = response.json().get("answer", "Sorry, something went wrong.")
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})