-- Move policy helpers out of the exposed API schema and apply advisor fixes.

create schema if not exists private;
revoke all on schema private from public;

create or replace function private.can_access_project(target_project_id uuid)
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
        p.owner_id = (select auth.uid())
        or p.is_public_demo
        or exists (
          select 1 from public.project_members pm
          where pm.project_id = p.id and pm.user_id = (select auth.uid())
        )
      )
  );
$$;

create or replace function private.can_edit_project(target_project_id uuid)
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
        p.owner_id = (select auth.uid())
        or exists (
          select 1 from public.project_members pm
          where pm.project_id = p.id
            and pm.user_id = (select auth.uid())
            and pm.role = 'editor'
        )
      )
  );
$$;

revoke all on function private.can_access_project(uuid) from public;
revoke all on function private.can_edit_project(uuid) from public;
grant usage on schema private to anon, authenticated, service_role;
grant execute on function private.can_access_project(uuid) to anon, authenticated, service_role;
grant execute on function private.can_edit_project(uuid) to authenticated, service_role;

alter policy "profiles_select_own" on public.profiles
using (id = (select auth.uid()));
alter policy "profiles_update_own" on public.profiles
using (id = (select auth.uid())) with check (id = (select auth.uid()));

alter policy "projects_select_accessible" on public.projects
using (private.can_access_project(id));
alter policy "projects_insert_own" on public.projects
with check (owner_id = (select auth.uid()) and not is_public_demo);
alter policy "projects_update_editable" on public.projects
using (private.can_edit_project(id)) with check (private.can_edit_project(id));
alter policy "projects_delete_owner" on public.projects
using (owner_id = (select auth.uid()));

alter policy "members_select_accessible" on public.project_members
using (private.can_access_project(project_id));
drop policy "members_manage_owner" on public.project_members;
create policy "members_insert_owner" on public.project_members for insert with check (
  exists (
    select 1 from public.projects p
    where p.id = project_id and p.owner_id = (select auth.uid())
  )
);
create policy "members_update_owner" on public.project_members for update using (
  exists (
    select 1 from public.projects p
    where p.id = project_id and p.owner_id = (select auth.uid())
  )
) with check (
  exists (
    select 1 from public.projects p
    where p.id = project_id and p.owner_id = (select auth.uid())
  )
);
create policy "members_delete_owner" on public.project_members for delete using (
  exists (
    select 1 from public.projects p
    where p.id = project_id and p.owner_id = (select auth.uid())
  )
);

alter policy "documents_select_accessible" on public.documents
using (private.can_access_project(project_id));
alter policy "documents_insert_editable" on public.documents
with check (owner_id = (select auth.uid()) and private.can_edit_project(project_id));
alter policy "documents_update_editable" on public.documents
using (private.can_edit_project(project_id)) with check (private.can_edit_project(project_id));
alter policy "documents_delete_editable" on public.documents
using (private.can_edit_project(project_id));

alter policy "chunks_select_accessible" on public.document_chunks
using (private.can_access_project(project_id));
alter policy "chunks_service_insert" on public.document_chunks
with check (private.can_edit_project(project_id));
alter policy "chunks_service_delete" on public.document_chunks
using (private.can_edit_project(project_id));

alter policy "runs_select_accessible" on public.research_runs
using (private.can_access_project(project_id));
alter policy "runs_insert_editable" on public.research_runs
with check (owner_id = (select auth.uid()) and private.can_edit_project(project_id));
alter policy "runs_update_editable" on public.research_runs
using (private.can_edit_project(project_id)) with check (private.can_edit_project(project_id));
alter policy "runs_delete_owner" on public.research_runs
using (owner_id = (select auth.uid()));

alter policy "tasks_select_accessible" on public.agent_tasks
using (private.can_access_project(project_id));
alter policy "tasks_insert_editable" on public.agent_tasks
with check (private.can_edit_project(project_id));
alter policy "tasks_update_editable" on public.agent_tasks
using (private.can_edit_project(project_id));
alter policy "events_select_accessible" on public.agent_events
using (private.can_access_project(project_id));
alter policy "events_insert_editable" on public.agent_events
with check (private.can_edit_project(project_id));

alter policy "sources_select_accessible" on public.sources
using (private.can_access_project(project_id));
alter policy "sources_insert_editable" on public.sources
with check (private.can_edit_project(project_id));
alter policy "findings_select_accessible" on public.findings
using (private.can_access_project(project_id));
alter policy "findings_insert_editable" on public.findings
with check (private.can_edit_project(project_id));
alter policy "claims_select_accessible" on public.claims
using (private.can_access_project(project_id));
alter policy "claims_insert_editable" on public.claims
with check (private.can_edit_project(project_id));
alter policy "claim_evidence_select_accessible" on public.claim_evidence
using (private.can_access_project(project_id));
alter policy "claim_evidence_insert_editable" on public.claim_evidence
with check (private.can_edit_project(project_id));

alter policy "messages_select_accessible" on public.messages
using (private.can_access_project(project_id));
alter policy "messages_insert_editable" on public.messages
with check (owner_id = (select auth.uid()) and private.can_edit_project(project_id));
alter policy "messages_delete_own" on public.messages
using (owner_id = (select auth.uid()));

alter policy "memories_select_own" on public.memories
using (owner_id = (select auth.uid()));
alter policy "memories_insert_own" on public.memories
with check (
  owner_id = (select auth.uid())
  and (project_id is null or private.can_edit_project(project_id))
);
alter policy "memories_update_own" on public.memories
using (owner_id = (select auth.uid())) with check (owner_id = (select auth.uid()));
alter policy "memories_delete_own" on public.memories
using (owner_id = (select auth.uid()));

alter policy "jobs_select_own" on public.jobs
using (owner_id = (select auth.uid()));
alter policy "jobs_insert_own" on public.jobs
with check (owner_id = (select auth.uid()) and private.can_edit_project(project_id));
alter policy "jobs_update_own" on public.jobs
using (owner_id = (select auth.uid()));
alter policy "feedback_select_own" on public.feedback
using (owner_id = (select auth.uid()));
alter policy "feedback_insert_own" on public.feedback
with check (owner_id = (select auth.uid()) and private.can_access_project(project_id));

drop policy "research_documents_select_own" on storage.objects;
drop policy "research_documents_insert_own" on storage.objects;
drop policy "research_documents_update_own" on storage.objects;
drop policy "research_documents_delete_own" on storage.objects;
create policy "research_documents_select_own" on storage.objects for select to authenticated using (
  bucket_id = 'research-documents'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);
create policy "research_documents_insert_own" on storage.objects for insert to authenticated with check (
  bucket_id = 'research-documents'
  and (storage.foldername(name))[1] = (select auth.uid())::text
  and lower(storage.extension(name)) = 'pdf'
);
create policy "research_documents_update_own" on storage.objects for update to authenticated using (
  bucket_id = 'research-documents' and owner_id = (select auth.uid())::text
) with check (
  bucket_id = 'research-documents' and owner_id = (select auth.uid())::text
);
create policy "research_documents_delete_own" on storage.objects for delete to authenticated using (
  bucket_id = 'research-documents' and owner_id = (select auth.uid())::text
);

create or replace function private.handle_new_user()
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

drop trigger on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function private.handle_new_user();

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
      row_number() over (
        order by dc.embedding operator(extensions.<=>) query_embedding
      ) as rank
    from public.document_chunks dc
    where dc.project_id = target_project_id
      and dc.embedding is not null
      and private.can_access_project(dc.project_id)
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
      and private.can_access_project(dc.project_id)
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

drop function public.can_access_project(uuid);
drop function public.can_edit_project(uuid);
drop function public.handle_new_user();

create index agent_events_project_idx on public.agent_events (project_id);
create index agent_tasks_project_idx on public.agent_tasks (project_id);
create index claim_evidence_project_idx on public.claim_evidence (project_id);
create index claim_evidence_source_idx on public.claim_evidence (run_id, source_id);
create index claims_project_idx on public.claims (project_id);
create index feedback_project_idx on public.feedback (project_id);
create index feedback_run_idx on public.feedback (run_id);
create index findings_project_idx on public.findings (project_id);
create index findings_run_idx on public.findings (run_id);
create index jobs_project_idx on public.jobs (project_id);
create index project_members_user_idx on public.project_members (user_id);
create index sources_document_idx on public.sources (document_id) where document_id is not null;
