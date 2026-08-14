# RAG package boundary

Page parsing, chunking, hashing embeddings, and Supabase hybrid retrieval currently live under `apps/api/app/services`. They can be extracted here without changing API contracts because providers are already isolated.
