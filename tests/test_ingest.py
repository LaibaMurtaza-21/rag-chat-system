from ingest import chunk_text


def test_chunk_text_splits_long_text():
    text = "a" * 250
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_chunk_text_short_text_single_chunk():
    text = "short text"
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_overlap_preserved():
    text = "abcdefghijklmnopqrst"  # 20 chars
    chunks = chunk_text(text, chunk_size=10, overlap=5)
    assert chunks[0][-5:] == chunks[1][:5]


def test_chunk_text_empty_string():
    chunks = chunk_text("", chunk_size=100, overlap=20)
    assert chunks == []


def test_ingest_file_calls_vector_store(tmp_path, monkeypatch):
    """Ensure ingest_file reads the file, chunks it, and calls add_texts correctly."""
    import ingest as ingest_module

    test_file = tmp_path / "sample.txt"
    test_file.write_text("This is a test document about Paris.")

    calls = {}
    def fake_add_texts(chunks, ids, metadatas):
        calls["chunks"] = chunks
        calls["ids"] = ids
        calls["metadatas"] = metadatas

    monkeypatch.setattr(ingest_module.vector_store, "add_texts", fake_add_texts)

    ingest_module.ingest_file(str(test_file))

    assert len(calls["chunks"]) >= 1
    assert calls["ids"][0].startswith("sample.txt-")
    assert calls["metadatas"][0]["source"] == "sample.txt"