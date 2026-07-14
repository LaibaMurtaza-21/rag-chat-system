"""
RAG pipeline module.

Orchestrates the full Retrieval-Augmented Generation flow:
retrieve relevant document chunks -> combine with chat history and
long-term facts -> generate an answer -> persist the conversation
and any newly learned facts.
"""

from app.vector_store import vector_store
from app.history import chat_history
from app.llm import llm


class RAGPipeline:
    """Coordinates retrieval, prompt construction, generation, and memory updates."""

    def answer(self, session_id: str, user_message: str) -> str:
        """
        Generate an answer to the user's message using RAG + persistent memory.

        Args:
            session_id: Unique identifier for the current chat session.
            user_message: The user's latest question/message.

        Returns:
            The assistant's generated answer as a string.
        """
        # 1. Retrieve relevant document chunks from the vector store.
        retrieved_chunks = vector_store.query(user_message)

        # 2. Pull permanent facts learned about the user in ANY past chat.
        facts = chat_history.get_all_facts()
        facts_text = "\n".join(f"- {f}" for f in facts) if facts else "No known facts yet."

        # 3. Get recent conversation for immediate short-term context.
        history = chat_history.get_history(session_id, limit=6)
        history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history)

        # 4. Build the prompt with permanent facts always included, plus
        #    document context (only if any relevant chunks were found).
        context_block = ""
        if retrieved_chunks:
            context_block = f"\nDocument context:\n{chr(10).join(retrieved_chunks)}\n"

        prompt = f"""Known facts about the user (remember these across all chats):
{facts_text}
{context_block}
Recent conversation:
{history_text}

Question: {user_message}
Answer:"""

        # 5. Generate the answer and persist both sides of the exchange.
        answer = llm.generate(prompt)
        chat_history.add_message(session_id, "user", user_message)
        chat_history.add_message(session_id, "assistant", answer)

        # 6. Ask the LLM to extract any new personal facts from this message
        #    so future sessions can reference them too.
        self._extract_and_store_facts(user_message)

        return answer

    def _extract_and_store_facts(self, user_message: str):
        """
        Use the LLM to detect and permanently store personal facts
        the user shares (name, profession, preferences, etc.).

        Args:
            user_message: The raw text of the user's latest message.
        """
        extraction_prompt = f"""Does this message contain a personal fact about the user (like their name, job, field of study, preferences, or similar)? 
If yes, respond with ONLY the fact as a short sentence (e.g., "The user's name is Laiba." or "The user is an AI student.").
If no personal fact is mentioned, respond with exactly: NONE

Message: "{user_message}"
Response:"""

        result = llm.generate(extraction_prompt).strip()

        # Only persist the fact if the model actually found one.
        if result and result.upper() != "NONE":
            chat_history.add_fact(result)


# Singleton instance so the pipeline (and its dependencies) is created once.
rag_pipeline = RAGPipeline()