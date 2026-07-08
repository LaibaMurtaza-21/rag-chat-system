from app.vector_store import vector_store
from app.history import chat_history
from app.llm import llm


class RAGPipeline:
    def answer(self, session_id: str, user_message: str) -> str:
        # 1. Retrieve relevant document chunks
        retrieved_chunks = vector_store.query(user_message)

        # 2. Pull permanent facts learned about the user in ANY past chat
        facts = chat_history.get_all_facts()
        facts_text = "\n".join(f"- {f}" for f in facts) if facts else "No known facts yet."

        # 3. Get recent conversation for immediate context
        history = chat_history.get_history(session_id, limit=6)
        history_text = "\n".join(f"{h['role']}: {h['content']}" for h in history)

        # 4. Build the prompt with permanent facts always included
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

        # 5. Generate the answer
        answer = llm.generate(prompt)
        chat_history.add_message(session_id, "user", user_message)
        chat_history.add_message(session_id, "assistant", answer)

        # 6. Ask the LLM to extract any new personal facts from this message
        self._extract_and_store_facts(user_message)

        return answer

    def _extract_and_store_facts(self, user_message: str):
        """Uses the LLM to detect and permanently store personal facts
        the user shares (name, profession, preferences, etc.)."""
        extraction_prompt = f"""Does this message contain a personal fact about the user (like their name, job, field of study, preferences, or similar)? 
If yes, respond with ONLY the fact as a short sentence (e.g., "The user's name is Laiba." or "The user is an AI student.").
If no personal fact is mentioned, respond with exactly: NONE

Message: "{user_message}"
Response:"""

        result = llm.generate(extraction_prompt).strip()

        if result and result.upper() != "NONE":
            chat_history.add_fact(result)


# Singleton instance
rag_pipeline = RAGPipeline()