from fastapi import FastAPI
from pydantic import BaseModel
from app.rag_pipeline import rag_pipeline
from app.history import chat_history

app = FastAPI(title="RAG Chat API")


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = rag_pipeline.answer(request.session_id, request.message)
    return ChatResponse(answer=answer)


@app.get("/history/{session_id}")
def get_history(session_id: str):
    return {"messages": chat_history.get_history(session_id, limit=100)}


@app.get("/sessions")
def get_sessions():
    return {"sessions": chat_history.list_sessions()}


@app.get("/")
def root():
    return {"status": "RAG Chat API is running"}