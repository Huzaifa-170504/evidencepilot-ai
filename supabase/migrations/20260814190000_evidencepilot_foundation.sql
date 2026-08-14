-- EvidencePilot AI production foundation
-- Owner: Huzaifa Waqar Butt

create extension if not exists vector with schema extensions;
create extension if not exists pg_trgm with schema extensions;
create extension if not exists unaccent with schema extensions;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text check (char_length(display_name) <= 120),
  report_preferences jsonb not null default '{"tone":"technical","citation_style":"numeric"}'::jsonb,
  memory_enabled boolean not null default true,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null,
  name text not null check (char_length(name) between 2 and 120),
  description text not null default '' check (char_length(description) <= 1000),
  is_public_demo boolean not null default false,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.project_members (
  project_id uuid not null references public.projects(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null default 'viewer' check (role in ('viewer', 'editor')),
  created_at timestamptz not null default timezone('utc', now()),
  primary key (project_id, user_id)
);

create or replace function public.can_access_project(target_project_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.projects p
    where p.id = target_project_id
      and (
        p.owner_id = auth.uid()
        or p.is_public_demo
        or exists (
          select 1 from public.project_members pm
          where pm.project_id = p.id and pm.user_id = auth.uid()
        )
      )
  );
$$;

create or replace function public.can_edit_project(target_project_id uuid)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1
    from public.projects p
    where p.id = target_project_id
      and (
        p.owner_id = auth.uid()
        or exists (
          select 1 from public.project_members pm
          where pm.project_id = p.id and pm.user_id = auth.uid() and pm.role = 'editor'
        )
      )
  );
$$;

revoke all on function public.can_access_project(uuid) from public;
revoke all on function public.can_edit_project(uuid) from public;
grant execute on function public.can_access_project(uuid) to anon, authenticated, service_role;
grant execute on function public.can_edit_project(uuid) to authenticated, service_role;

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  filename text not null check (char_length(filename) between 1 and 255),
  storage_path text not null unique check (char_length(storage_path) <= 700),
  mime_type text not null default 'application/pdf' check (mime_type = 'application/pdf'),
  size_bytes bigint not null check (size_bytes between 1 and 10485760),
  checksum_sha256 text check (checksum_sha256 ~ '^[a-f0-9]{64}$'),
  page_count integer check (page_count between 1 and 150),
  status text not null default 'uploaded' check (status in ('uploaded', 'processing', 'ready', 'failed')),
  processing_error text check (char_length(processing_error) <= 1000),
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  unique (project_id, checksum_sha256)
);

create table public.document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  chunk_index integer not null check (chunk_index >= 0),
  page_number integer not null check (page_number >= 1),
  section_heading text,
  char_start integer not null default 0 check (char_start >= 0),
  char_end integer not null default 0 check (char_end >= char_start),
  content text not null check (char_length(content) > 0),
  content_tsv tsvector generated always as (to_tsvector('english', content)) stored,
  embedding extensions.vector(384),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  unique (document_id, chunk_index)
);

create table public.research_runs (
  id text primary key check (id ~ '^run_[a-zA-Z0-9]+$'),
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  question text not null check (char_length(question) between 12 and 2000),
  depth text not null default 'standard' check (depth in ('quick', 'standard', 'deep')),
  status text not null default 'queued' check (status in ('queued', 'running', 'cancelled', 'completed', 'failed')),
  plan jsonb not null default '[]'::jsonb,
  budgets jsonb not null default '{"model_calls":5,"search_calls":10,"max_sources":20,"max_retries":1}'::jsonb,
  metrics jsonb not null default '{}'::jsonb,
  final_report_markdown text,
  snapshot jsonb not null default '{}'::jsonb,
  correlation_id text,
  created_at timestamptz not null default timezone('utc', now()),
  started_at timestamptz,
  completed_at timestamptz,
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.agent_tasks (
  id uuid primary key default gen_random_uuid(),
  run_id text not null references public.research_runs(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  task_key text not null,
  agent_name text not null,
  title text not null,
  objective text not null,
  status text not null check (status in ('queued', 'running', 'completed', 'skipped', 'failed')),
  dependencies jsonb not null default '[]'::jsonb,
  input jsonb not null default '{}'::jsonb,
  output jsonb not null default '{}'::jsonb,
  error text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  unique (run_id, task_key)
);

create table public.agent_events (
  id bigint generated always as identity primary key,
  run_id text not null references public.research_runs(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  sequence integer not null check (sequence >= 1),
  agent_name text not null,
  status text not null check (status in ('queued', 'running', 'completed', 'skipped', 'failed')),
  summary text not null check (char_length(summary) <= 2000),
  duration_ms integer not null default 0 check (duration_ms >= 0),
  safe_metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  unique (run_id, sequence)
);

create table public.sources (
  id text not null,
  run_id text not null references public.research_runs(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  title text not null,
  source_type text not null check (source_type in ('paper', 'web', 'repository', 'document', 'dataset')),
  canonical_url text,
  url text,
  publisher text,
  publication_year integer,
  authors jsonb not null default '[]'::jsonb,
  doi text,
  arxiv_id text,
  document_id uuid references public.documents(id) on delete cascade,
  page_number integer,
  excerpt text,
  accessed_at timestamptz not null default timezone('utc', now()),
  metadata jsonb not null default '{}'::jsonb,
  primary key (run_id, id)
);

create table public.findings (
  id uuid primary key default gen_random_uuid(),
  run_id text not null references public.research_runs(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  agent_name text not null,
  summary text not null,
  source_ids text[] not null default '{}',
  uncertainty text,
  created_at timestamptz not null default timezone('utc', now())
);

create table public.claims (
  id text not null,
  run_id text not null references public.research_runs(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  claim_text text not null,
  verdict text not null check (verdict in ('verified', 'partial', 'unsupported', 'conflicting')),
  confidence double precision not null check (confidence between 0 and 1),
  source_ids text[] not null default '{}',
  rationale text,
  created_at timestamptz not null default timezone('utc', now()),
  primary key (run_id, id)
);

create table public.claim_evidence (
  id uuid primary key default gen_random_uuid(),
  run_id text not null,
  claim_id text not null,
  source_id text not null,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  relationship text not null check (relationship in ('supports', 'contradicts', 'context')),
  excerpt text,
  created_at timestamptz not null default timezone('utc', now()),
  foreign key (run_id, claim_id) references public.claims(run_id, id) on delete cascade,
  foreign key (run_id, source_id) references public.sources(run_id, id) on delete cascade,
  unique (run_id, claim_id, source_id, relationship)
);

create table public.messages (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null check (char_length(content) between 1 and 4000),
  created_at timestamptz not null default timezone('utc', now())
);

create table public.memories (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references public.projects(id) on delete cascade,
  owner_id uuid not null,
  memory_type text not null check (memory_type in ('project', 'preference', 'finding', 'terminology')),
  title text not null check (char_length(title) <= 160),
  content text not null check (char_length(content) <= 10000),
  embedding extensions.vector(384),
  enabled boolean not null default true,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.jobs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  job_type text not null check (job_type in ('document_ingestion', 'research_run')),
  entity_id text not null,
  status text not null default 'queued' check (status in ('queued', 'running', 'completed', 'failed', 'cancelled')),
  attempt_count integer not null default 0 check (attempt_count >= 0),
  max_attempts integer not null default 2 check (max_attempts between 1 and 5),
  checkpoint jsonb not null default '{}'::jsonb,
  error text,
  available_at timestamptz not null default timezone('utc', now()),
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table public.feedback (
  id uuid primary key default gen_random_uuid(),
  run_id text not null references public.research_runs(id) on delete cascade,
  project_id uuid not null references public.projects(id) on delete cascade,
  owner_id uuid not null,
  rating integer check (rating between 1 and 5),
  comments text check (char_length(comments) <= 2000),
  labels jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default timezone('utc', now())
);

create index projects_owner_updated_idx on public.projects (owner_id, updated_at desc);
create index documents_project_status_idx on public.documents (project_id, status);
create index document_chunks_project_page_idx on public.document_chunks (project_id, document_id, page_number);
create index document_chunks_tsv_idx on public.document_chunks using gin (content_tsv);
create index document_chunks_embedding_idx on public.document_chunks using hnsw (embedding extensions.vector_cosine_ops);
create index research_runs_project_created_idx on public.research_runs (project_id, created_at desc);
create index agent_events_run_sequence_idx on public.agent_events (run_id, sequence);
create index sources_project_type_idx on public.sources (project_id, source_type);
create index messages_project_created_idx on public.messages (project_id, created_at);
create index memories_project_enabled_idx on public.memories (project_id, enabled);
create index memories_embedding_idx on public.memories using hnsw (embedding extensions.vector_cosine_ops);
create index jobs_ready_idx on public.jobs (status, available_at) where status = 'queued';

create trigger profiles_updated_at before update on public.profiles
for each row execute function public.set_updated_at();
create trigger projects_updated_at before update on public.projects
for each row execute function public.set_updated_at();
create trigger documents_updated_at before update on public.documents
for each row execute function public.set_updated_at();
create trigger research_runs_updated_at before update on public.research_runs
for each row execute function public.set_updated_at();
create trigger memories_updated_at before update on public.memories
for each row execute function public.set_updated_at();
create trigger jobs_updated_at before update on public.jobs
for each row execute function public.set_updated_at();

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'display_name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end;
$$;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

create or replace function public.hybrid_search_document_chunks(
  query_text text,
  query_embedding extensions.vector(384),
  target_project_id uuid,
  match_count integer default 5
)
returns table (
  id uuid,
  document_id uuid,
  page_number integer,
  section_heading text,
  content text,
  filename text,
  score double precision
)
language sql
stable
security invoker
set search_path = ''
as $$
  with semantic as (
    select
      dc.id,
      row_number() over (order by dc.embedding operator(extensions.<=>) query_embedding) as rank
    from public.document_chunks dc
    where dc.project_id = target_project_id
      and dc.embedding is not null
      and public.can_access_project(dc.project_id)
    order by dc.embedding operator(extensions.<=>) query_embedding
    limit least(greatest(match_count * 4, 20), 100)
  ),
  keyword as (
    select
      dc.id,
      row_number() over (
        order by ts_rank_cd(dc.content_tsv, websearch_to_tsquery('english', query_text)) desc
      ) as rank
    from public.document_chunks dc
    where dc.project_id = target_project_id
      and dc.content_tsv @@ websearch_to_tsquery('english', query_text)
      and public.can_access_project(dc.project_id)
    order by ts_rank_cd(dc.content_tsv, websearch_to_tsquery('english', query_text)) desc
    limit least(greatest(match_count * 4, 20), 100)
  ),
  fused as (
    select
      coalesce(s.id, k.id) as id,
      coalesce(1.0 / (60 + s.rank), 0.0) + coalesce(1.0 / (60 + k.rank), 0.0) as score
    from semantic s
    full outer join keyword k on s.id = k.id
  )
  select dc.id, dc.document_id, dc.page_number, dc.section_heading, dc.content, d.filename, fused.score
  from fused
  join public.document_chunks dc on dc.id = fused.id
  join public.documents d on d.id = dc.document_id
  order by fused.score desc
  limit least(greatest(match_count, 1), 20);
$$;

grant execute on function public.hybrid_search_document_chunks(text, extensions.vector, uuid, integer)
to authenticated, service_role;

alter table public.profiles enable row level security;
alter table public.projects enable row level security;
alter table public.project_members enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.research_runs enable row level security;
alter table public.agent_tasks enable row level security;
alter table public.agent_events enable row level security;
alter table public.sources enable row level security;
alter table public.findings enable row level security;
alter table public.claims enable row level security;
alter table public.claim_evidence enable row level security;
alter table public.messages enable row level security;
alter table public.memories enable row level security;
alter table public.jobs enable row level security;
alter table public.feedback enable row level security;

create policy "profiles_select_own" on public.profiles for select using (id = auth.uid());
create policy "profiles_update_own" on public.profiles for update using (id = auth.uid()) with check (id = auth.uid());

create policy "projects_select_accessible" on public.projects for select using (public.can_access_project(id));
create policy "projects_insert_own" on public.projects for insert with check (owner_id = auth.uid() and not is_public_demo);
create policy "projects_update_editable" on public.projects for update using (public.can_edit_project(id)) with check (public.can_edit_project(id));
create policy "projects_delete_owner" on public.projects for delete using (owner_id = auth.uid());

create policy "members_select_accessible" on public.project_members for select using (public.can_access_project(project_id));
create policy "members_manage_owner" on public.project_members for all using (
  exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid())
) with check (
  exists (select 1 from public.projects p where p.id = project_id and p.owner_id = auth.uid())
);

create policy "documents_select_accessible" on public.documents for select using (public.can_access_project(project_id));
create policy "documents_insert_editable" on public.documents for insert with check (
  owner_id = auth.uid() and public.can_edit_project(project_id)
);
create policy "documents_update_editable" on public.documents for update using (public.can_edit_project(project_id)) with check (public.can_edit_project(project_id));
create policy "documents_delete_editable" on public.documents for delete using (public.can_edit_project(project_id));

create policy "chunks_select_accessible" on public.document_chunks for select using (public.can_access_project(project_id));
create policy "chunks_service_insert" on public.document_chunks for insert with check (public.can_edit_project(project_id));
create policy "chunks_service_delete" on public.document_chunks for delete using (public.can_edit_project(project_id));

create policy "runs_select_accessible" on public.research_runs for select using (public.can_access_project(project_id));
create policy "runs_insert_editable" on public.research_runs for insert with check (owner_id = auth.uid() and public.can_edit_project(project_id));
create policy "runs_update_editable" on public.research_runs for update using (public.can_edit_project(project_id)) with check (public.can_edit_project(project_id));
create policy "runs_delete_owner" on public.research_runs for delete using (owner_id = auth.uid());

create policy "tasks_select_accessible" on public.agent_tasks for select using (public.can_access_project(project_id));
create policy "tasks_insert_editable" on public.agent_tasks for insert with check (public.can_edit_project(project_id));
create policy "tasks_update_editable" on public.agent_tasks for update using (public.can_edit_project(project_id));

create policy "events_select_accessible" on public.agent_events for select using (public.can_access_project(project_id));
create policy "events_insert_editable" on public.agent_events for insert with check (public.can_edit_project(project_id));

create policy "sources_select_accessible" on public.sources for select using (public.can_access_project(project_id));
create policy "sources_insert_editable" on public.sources for insert with check (public.can_edit_project(project_id));
create policy "findings_select_accessible" on public.findings for select using (public.can_access_project(project_id));
create policy "findings_insert_editable" on public.findings for insert with check (public.can_edit_project(project_id));
create policy "claims_select_accessible" on public.claims for select using (public.can_access_project(project_id));
create policy "claims_insert_editable" on public.claims for insert with check (public.can_edit_project(project_id));
create policy "claim_evidence_select_accessible" on public.claim_evidence for select using (public.can_access_project(project_id));
create policy "claim_evidence_insert_editable" on public.claim_evidence for insert with check (public.can_edit_project(project_id));

create policy "messages_select_accessible" on public.messages for select using (public.can_access_project(project_id));
create policy "messages_insert_editable" on public.messages for insert with check (owner_id = auth.uid() and public.can_edit_project(project_id));
create policy "messages_delete_own" on public.messages for delete using (owner_id = auth.uid());

create policy "memories_select_own" on public.memories for select using (owner_id = auth.uid());
create policy "memories_insert_own" on public.memories for insert with check (owner_id = auth.uid() and (project_id is null or public.can_edit_project(project_id)));
create policy "memories_update_own" on public.memories for update using (owner_id = auth.uid()) with check (owner_id = auth.uid());
create policy "memories_delete_own" on public.memories for delete using (owner_id = auth.uid());

create policy "jobs_select_own" on public.jobs for select using (owner_id = auth.uid());
create policy "jobs_insert_own" on public.jobs for insert with check (owner_id = auth.uid() and public.can_edit_project(project_id));
create policy "jobs_update_own" on public.jobs for update using (owner_id = auth.uid());
create policy "feedback_select_own" on public.feedback for select using (owner_id = auth.uid());
create policy "feedback_insert_own" on public.feedback for insert with check (owner_id = auth.uid() and public.can_access_project(project_id));

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('research-documents', 'research-documents', false, 10485760, array['application/pdf'])
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

create policy "research_documents_select_own" on storage.objects for select to authenticated using (
  bucket_id = 'research-documents' and (storage.foldername(name))[1] = auth.uid()::text
);
create policy "research_documents_insert_own" on storage.objects for insert to authenticated with check (
  bucket_id = 'research-documents'
  and (storage.foldername(name))[1] = auth.uid()::text
  and lower(storage.extension(name)) = 'pdf'
);
create policy "research_documents_update_own" on storage.objects for update to authenticated using (
  bucket_id = 'research-documents' and owner_id = auth.uid()::text
) with check (
  bucket_id = 'research-documents' and owner_id = auth.uid()::text
);
create policy "research_documents_delete_own" on storage.objects for delete to authenticated using (
  bucket_id = 'research-documents' and owner_id = auth.uid()::text
);

do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'agent_events'
  ) then
    alter publication supabase_realtime add table public.agent_events;
  end if;
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'research_runs'
  ) then
    alter publication supabase_realtime add table public.research_runs;
  end if;
end $$;

grant usage on schema public to anon, authenticated, service_role;
grant select on public.projects, public.research_runs, public.agent_events, public.sources, public.claims to anon;
grant select, insert, update, delete on all tables in schema public to authenticated;
grant usage, select on all sequences in schema public to authenticated;
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
