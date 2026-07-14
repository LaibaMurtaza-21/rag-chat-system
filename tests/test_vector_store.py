from unittest.mock import patch, MagicMock
from app.vector_store import VectorStore


@patch("app.vector_store.embedder")
@patch("app.vector_store.chromadb.PersistentClient")
def test_add_texts_calls_collection_add(mock_client_class, mock_embedder):
    mock_collection = MagicMock()
    mock_client_class.return_value.get_or_create_collection.return_value = mock_collection
    mock_embedder.embed_many.return_value = [[0.1, 0.2], [0.3, 0.4]]

    store = VectorStore()
    store.add_texts(["chunk one", "chunk two"], ["id1", "id2"], [{"source": "a.txt"}, {"source": "a.txt"}])

    mock_collection.add.assert_called_once_with(
        documents=["chunk one", "chunk two"],
        embeddings=[[0.1, 0.2], [0.3, 0.4]],
        ids=["id1", "id2"],
        metadatas=[{"source": "a.txt"}, {"source": "a.txt"}]
    )


@patch("app.vector_store.embedder")
@patch("app.vector_store.chromadb.PersistentClient")
def test_query_returns_documents(mock_client_class, mock_embedder):
    mock_collection = MagicMock()
    mock_client_class.return_value.get_or_create_collection.return_value = mock_collection
    mock_embedder.embed_one.return_value = [0.1, 0.2]
    mock_collection.query.return_value = {"documents": [["The Eiffel Tower is in Paris."]]}

    store = VectorStore()
    results = store.query("Where is the Eiffel Tower?")

    assert results == ["The Eiffel Tower is in Paris."]


@patch("app.vector_store.embedder")
@patch("app.vector_store.chromadb.PersistentClient")
def test_query_empty_results_returns_empty_list(mock_client_class, mock_embedder):
    mock_collection = MagicMock()
    mock_client_class.return_value.get_or_create_collection.return_value = mock_collection
    mock_embedder.embed_one.return_value = [0.1, 0.2]
    mock_collection.query.return_value = {"documents": [[]]}

    store = VectorStore()
    results = store.query("irrelevant question")

    assert results == []