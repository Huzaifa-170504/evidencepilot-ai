-- Public recruiter snapshot. Application demo data also ships in the frontend
-- so it remains usable when Supabase or the backend is asleep.

insert into public.projects (id, owner_id, name, description, is_public_demo)
values (
  '10000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  'Mamba-YOLO Intelligence',
  'Evidence-backed comparison of selective state-space architectures for object detection.',
  true
)
on conflict (id) do update set
  name = excluded.name,
  description = excluded.description,
  is_public_demo = true;

insert into public.research_runs (
  id, project_id, owner_id, question, depth, status, plan, metrics,
  final_report_markdown, snapshot, correlation_id, completed_at
)
values (
  'run_publicmambasnapshot',
  '10000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-000000000001',
  'Compare Mamba architectures for object detection and identify research gaps',
  'standard',
  'completed',
  '[]'::jsonb,
  '{"sources_found":3,"papers_analyzed":2,"claims_verified":2,"agents_executed":7,"total_duration_ms":619}'::jsonb,
  '# EvidencePilot public Mamba-YOLO research snapshot',
  '{}'::jsonb,
  'run_publicmambasnapshot',
  timezone('utc', now())
)
on conflict (id) do nothing;
