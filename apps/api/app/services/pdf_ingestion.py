from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from uuid import uuid4

import fitz
from pypdf import PdfReader

from app.security import validate_pdf_bytes
from app.services.embeddings import HashingEmbeddingProvider


@dataclass(frozen=True)
class ParsedChunk:
    chunk_index: int
    page_number: int
    content: str
    section_heading: str | None
    char_start: int
    char_end: int


@dataclass(frozen=True)
class ParsedPdf:
    page_count: int
    chunks: list[ParsedChunk]
    possible_scan_pages: list[int]
    checksum_sha256: str


def _clean_text(text: str) -> str:
    text = text.replace("\u00ad", "").replace("\x00", " ")
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _heading_for(text: str) -> str | None:
    for line in text.splitlines()[:8]:
        candidate = line.strip()
        if 3 <= len(candidate) <= 120 and (
            candidate.isupper() or re.match(r"^\d+(?:\.\d+)*\s+[A-Z]", candidate)
        ):
            return candidate
    return None


def _split_page(
    text: str, *, target_chars: int = 4_000, overlap_chars: int = 600
) -> list[tuple[int, int, str]]:
    if len(text) <= target_chars:
        return [(0, len(text), text)] if text else []
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    results: list[tuple[int, int, str]] = []
    cursor = 0
    buffer = ""
    start = 0
    for sentence in sentences:
        if buffer and len(buffer) + len(sentence) + 1 > target_chars:
            end = start + len(buffer)
            results.append((start, end, buffer.strip()))
            overlap = buffer[-overlap_chars:]
            boundary = overlap.find(" ")
            overlap = overlap[boundary + 1 :] if boundary >= 0 else overlap
            start = max(0, end - len(overlap))
            buffer = f"{overlap} {sentence}"
        else:
            if not buffer:
                start = cursor
            buffer = f"{buffer} {sentence}".strip()
        cursor += len(sentence) + 1
    if buffer.strip():
        results.append((start, start + len(buffer), buffer.strip()))
    return results


def parse_pdf(content: bytes, *, max_bytes: int, max_pages: int) -> ParsedPdf:
    checksum = validate_pdf_bytes(content, max_bytes=max_bytes)
    try:
        document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise ValueError("The PDF parser could not open this document.") from exc
    if document.needs_pass:
        raise ValueError("Password-protected PDFs are not supported.")
    if document.page_count > max_pages:
        raise ValueError(f"The PDF exceeds the {max_pages}-page limit.")

    chunks: list[ParsedChunk] = []
    possible_scans: list[int] = []
    chunk_index = 0
    try:
        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            text = _clean_text(page.get_text("text"))
            if len(text) < 40:
                possible_scans.append(page_index + 1)
                continue
            heading = _heading_for(text)
            for start, end, chunk_text in _split_page(text):
                chunks.append(
                    ParsedChunk(
                        chunk_index=chunk_index,
                        page_number=page_index + 1,
                        content=chunk_text,
                        section_heading=heading,
                        char_start=start,
                        char_end=end,
                    )
                )
                chunk_index += 1
    finally:
        document.close()

    if not chunks:
        # pypdf occasionally extracts text from files that PyMuPDF sees as scans.
        try:
            reader = PdfReader(BytesIO(content))
            if reader.is_encrypted:
                raise ValueError("Password-protected PDFs are not supported.")
            for page_index, page in enumerate(reader.pages):
                text = _clean_text(page.extract_text() or "")
                if text:
                    chunks.append(
                        ParsedChunk(
                            chunk_index=len(chunks),
                            page_number=page_index + 1,
                            content=text,
                            section_heading=_heading_for(text),
                            char_start=0,
                            char_end=len(text),
                        )
                    )
        except ValueError:
            raise
        except Exception:
            pass

    return ParsedPdf(
        page_count=len(PdfReader(BytesIO(content)).pages),
        chunks=chunks,
        possible_scan_pages=possible_scans,
        checksum_sha256=checksum,
    )


def chunks_for_storage(
    parsed: ParsedPdf,
    *,
    document_id: str,
    project_id: str,
    owner_id: str,
    dimensions: int = 384,
) -> list[dict[str, object]]:
    provider = HashingEmbeddingProvider(dimensions)
    return [
        {
            "id": str(uuid4()),
            "document_id": document_id,
            "project_id": project_id,
            "owner_id": owner_id,
            "chunk_index": chunk.chunk_index,
            "page_number": chunk.page_number,
            "section_heading": chunk.section_heading,
            "char_start": chunk.char_start,
            "char_end": chunk.char_end,
            "content": chunk.content,
            "embedding": provider.embed(chunk.content),
            "metadata": {"embedding_provider": "hashing-v1"},
        }
        for chunk in parsed.chunks
    ]
