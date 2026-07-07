from app.vector_store import vector_store
from app.history import chat_history
from app.llm import llm


class RAGPipeline:
    def answer(self, session_id: str, user_message: str) -> str:
        # 1. Retrieve relevant chunks from the vector store
        retrieved_chunks = vector_store.query(user_message)

        # 2. Get recent chat history for this session
        history = chat_history.get_history(session_id, limit=6)
        history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history)

        # 3. Build the prompt — only include context if something was actually retrieved
        if retrieved_chunks:
            context = "\n".join(retrieved_chunks)
            prompt = f"""Use the context below to help answer the question if it's relevant. If the context isn't relevant, just answer the question using your own knowledge.

Context:
{context}

Conversation so far:
{history_text}

Question: {user_message}
Answer:"""
        else:
            prompt = f"""Conversation so far:
{history_text}

Question: {user_message}
Answer:"""

        # 4. Generate the answer and save both messages to history
        answer = llm.generate(prompt)
        chat_history.add_message(session_id, "user", user_message)
        chat_history.add_message(session_id, "assistant", answer)

        return answer


# Singleton instance
rag_pipeline = RAGPipeline()