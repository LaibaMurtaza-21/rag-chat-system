"""
FastAPI backend entry point.

Exposes HTTP endpoints for chatting with the RAG pipeline and for
retrieving stored conversation history / session lists.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from app.rag_pipeline import rag_pipeline
from app.history import chat_history

app = FastAPI(title="RAG Chat API")


class ChatRequest(BaseModel):
    """Request body schema for the /chat endpoint."""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response body schema for the /chat endpoint."""
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Handle an incoming chat message: run it through the RAG pipeline
    and return the generated answer.
    """
    answer = rag_pipeline.answer(request.session_id, request.message)
    return ChatResponse(answer=answer)


@app.get("/history/{session_id}")
def get_history(session_id: str):
    """Return up to the last 100 messages for a given session."""
    return {"messages": chat_history.get_history(session_id, limit=100)}


@app.get("/sessions")
def get_sessions():
    """Return a list of all known session IDs, most recently active first."""
    return {"sessions": chat_history.list_sessions()}


@app.get("/")
def root():
    """Simple health-check endpoint to confirm the API is running."""
    return {"status": "RAG Chat API is running"}