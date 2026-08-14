# Database and RLS

Supabase project `dsbxndbbpryisxevjjgc` contains 16 application tables, a private PDF bucket, Realtime publication for runs/events, pgvector HNSW indexes, full-text indexes, hybrid-search RPC, update triggers, and automatic profile creation.

All application tables have RLS. Owner/project access is centralized in security-definer helpers stored in non-exposed schema `private`. Storage object paths begin with authenticated user ID and project ID. The service-role key is backend-only.
