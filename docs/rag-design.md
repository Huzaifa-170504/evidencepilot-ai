# RAG design

PDFs are uploaded directly to the private `research-documents` bucket. The API validates signature, size, page count, encryption, checksum, filename, path ownership, and parser success. PyMuPDF extracts page-aware text; pypdf is a fallback. Chunks preserve page, heading, offsets, and document identity.

Retrieval combines PostgreSQL full-text rank and pgvector cosine distance through reciprocal-rank fusion. RLS filters project access before chunks leave the database. A zero-cost hashing provider supplies deterministic 384-dimensional vectors; the interface can switch to Gemini.
