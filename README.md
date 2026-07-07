# RAG Chat System

A Retrieval-Augmented Generation (RAG) chat application that answers questions using both your own documents and general knowledge, while maintaining persistent conversation memory across sessions.

## Features

- **Chat Interface** — Interactive chat UI built with Streamlit
- **RAG Pipeline** — Retrieves relevant context from your documents before generating answers
- **Persistent Memory** — Chat history is stored in SQLite and reused across sessions
- **Fast LLM Inference** — Uses Groq's API (Llama 3.3 70B) for high-quality, low-latency responses

## Tech Stack

| Component        | Technology                          |
|-------------------|--------------------------------------|
| Backend API       | FastAPI                             |
| Frontend UI       | Streamlit                           |
| Vector Database   | ChromaDB                            |
| Embeddings        | sentence-transformers (all-MiniLM-L6-v2) |
| Chat History      | SQLite                              |
| LLM               | Groq API (llama-3.3-70b-versatile)  |

## Project Structure

```
rag-chat-system/
├── app/
│   ├── config.py          # Central configuration (paths, model names, chunk settings)
│   ├── embeddings.py       # Converts text into vector embeddings
│   ├── vector_store.py     # ChromaDB wrapper for storing/retrieving document chunks
│   ├── history.py          # SQLite wrapper for persistent chat history
│   ├── llm.py               # Groq API client for generating responses
│   ├── rag_pipeline.py     # Combines retrieval + history + generation
│   └── main.py              # FastAPI backend exposing the /chat endpoint
├── ui/
│   └── streamlit_app.py    # Chat interface
├── data/                    # Source documents to be ingested (.txt files)
├── storage/                 # Auto-generated: ChromaDB + SQLite database files
├── ingest.py                 # Script to chunk and embed documents into the vector store
├── requirements.txt
├── .env                       # API keys (not committed to Git)
└── README.md
```

## How the RAG System Works

1. **Ingestion** (`ingest.py`) — Documents in `data/` are split into overlapping text chunks, converted into vector embeddings using a sentence-transformer model, and stored in a persistent ChromaDB collection.

2. **Retrieval** — When a user sends a message, the same embedding model converts the question into a vector, and ChromaDB returns the most semantically similar document chunks.

3. **Augmentation** — The retrieved chunks are combined with recent conversation history (pulled from SQLite) into a single prompt. If no relevant document chunks are found, the system relies on the LLM's own general knowledge instead.

4. **Generation** — The combined prompt is sent to Groq's `llama-3.3-70b-versatile` model, which generates a context-aware answer.

5. **Memory** — Both the user's message and the assistant's answer are saved to SQLite under a session ID, so future messages in the same (or resumed) session can reference earlier conversation context.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/LaibaMurtaza-21/rag-chat-system.git
cd rag-chat-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com) (no credit card required).

### 5. Add documents and ingest them

Place `.txt` files in the `data/` folder, then run:

```bash
python ingest.py
```

### 6. Start the backend

```bash
uvicorn app.main:app --reload
```

### 7. Start the frontend (in a separate terminal)

```bash
streamlit run ui/streamlit_app.py
```

The chat interface will open at `http://localhost:8501`.

## Example

**User:** Where is the Eiffel Tower?
**Assistant:** The Eiffel Tower is located in Paris, France. *(Answer grounded in an ingested document.)*

**User:** What is the capital of Japan?
**Assistant:** Tokyo. *(Answered from the LLM's general knowledge, since no relevant document was found.)*

## Notes

- The `storage/` folder (ChromaDB + SQLite files) and `venv/` are excluded from version control via `.gitignore`.
- Chat sessions are identified by a UUID generated per browser session; history persists in `storage/history.db` across app restarts.