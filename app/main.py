from fastapi import FastAPI
from pydantic import BaseModel
from app.rag_pipeline import rag_pipeline

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


@app.get("/")
def root():
    return {"status": "RAG Chat API is running"}