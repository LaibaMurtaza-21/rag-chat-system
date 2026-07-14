import pytest
from app.history import ChatHistory


@pytest.fixture
def history(tmp_path, monkeypatch):
    """Fresh ChatHistory instance backed by a temp SQLite file, not the real DB."""
    import app.history as history_module
    fake_db_path = str(tmp_path / "test_history.db")
    monkeypatch.setattr(history_module, "SQLITE_DB_PATH", fake_db_path)
    return ChatHistory()


def test_add_and_get_message(history):
    history.add_message("session-1", "user", "Hello")
    history.add_message("session-1", "assistant", "Hi there")

    result = history.get_history("session-1")
    assert len(result) == 2
    assert result[0] == {"role": "user", "content": "Hello"}
    assert result[1] == {"role": "assistant", "content": "Hi there"}


def test_get_history_respects_limit(history):
    for i in range(5):
        history.add_message("session-1", "user", f"message {i}")

    result = history.get_history("session-1", limit=2)
    assert len(result) == 2
    # should be the two most recent, oldest-first
    assert result[-1]["content"] == "message 4"


def test_get_history_empty_session_returns_empty_list(history):
    assert history.get_history("nonexistent-session") == []


def test_list_sessions_returns_distinct_sessions(history):
    history.add_message("session-a", "user", "hi")
    history.add_message("session-b", "user", "hello")
    sessions = history.list_sessions()
    assert set(sessions) == {"session-a", "session-b"}


def test_add_fact_and_get_all_facts(history):
    history.add_fact("User's name is Laiba")
    facts = history.get_all_facts()
    assert "User's name is Laiba" in facts


def test_add_fact_deduplicates(history):
    history.add_fact("User likes Python")
    history.add_fact("User likes Python")  # duplicate
    facts = history.get_all_facts()
    assert facts.count("User likes Python") == 1