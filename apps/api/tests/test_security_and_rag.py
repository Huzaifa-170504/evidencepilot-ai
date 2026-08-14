from __future__ import annotations

import math

import fitz
import pytest

from app.security import sanitize_filename, validate_pdf_bytes
from app.services.embeddings import HashingEmbeddingProvider
from app.services.pdf_ingestion import chunks_for_storage, parse_pdf


def make_pdf(pages: list[str]) -> bytes:
    document = fitz.open()
    for text in pages:
        page = document.new_page()
        page.insert_textbox(fitz.Rect(50, 50, 545, 790), text, fontsize=11)
    content = document.tobytes()
    document.close()
    return content


def test_filename_and_pdf_validation() -> None:
    assert sanitize_filename("../../Unsafe paper name.pdf") == "Unsafe-paper-name.pdf"
    assert sanitize_filename("notes") == "notes.pdf"
    content = make_pdf(["A valid evidence document with enough text for parsing."])
    checksum = validate_pdf_bytes(content, max_bytes=1_000_000)
    assert len(checksum) == 64

    with pytest.raises(ValueError, match="empty"):
        validate_pdf_bytes(b"", max_bytes=100)
    with pytest.raises(ValueError, match="exceeds"):
        validate_pdf_bytes(b"%PDF-" + b"x" * 200, max_bytes=20)
    with pytest.raises(ValueError, match="signature"):
        validate_pdf_bytes(b"not a pdf", max_bytes=100)


def test_hashing_embeddings_are_normalized_and_stable() -> None:
    provider = HashingEmbeddingProvider(64)
    first = provider.embed("Mamba visual state space model")
    second = provider.embed("Mamba visual state space model")
    assert first == second
    assert math.isclose(sum(value * value for value in first), 1.0)
    assert provider.embed("") == [0.0] * 64
    assert len(provider.embed_many(["one", "two"])) == 2


def test_page_aware_pdf_parsing_and_chunk_storage() -> None:
    long_text = "1 Introduction\n" + "Mamba models process visual sequences efficiently. " * 40
    parsed = parse_pdf(
        make_pdf([long_text, "A second evidence page with enough extractable text for indexing."]),
        max_bytes=2_000_000,
        max_pages=10,
    )
    assert parsed.page_count == 2
    assert len(parsed.chunks) >= 2
    assert parsed.chunks[0].page_number == 1
    assert parsed.chunks[0].section_heading == "1 Introduction"
    stored = chunks_for_storage(
        parsed,
        document_id="10000000-0000-0000-0000-000000000001",
        project_id="20000000-0000-0000-0000-000000000001",
        owner_id="30000000-0000-0000-0000-000000000001",
        dimensions=64,
    )
    assert stored[0]["metadata"] == {"embedding_provider": "hashing-v1"}
    assert len(stored[0]["embedding"]) == 64


def test_pdf_page_limit_is_enforced() -> None:
    with pytest.raises(ValueError, match="page limit"):
        parse_pdf(make_pdf(["one", "two"]), max_bytes=1_000_000, max_pages=1)
