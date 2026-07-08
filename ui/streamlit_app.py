import streamlit as st
import requests
import uuid

st.set_page_config(page_title="RAG Chat", page_icon="💬")
st.title("💬 RAG Chat System")

API_URL = "http://localhost:8000/chat"

# Create a session ID that persists during this browser session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

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