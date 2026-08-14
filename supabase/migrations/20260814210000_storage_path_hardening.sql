-- Require every uploaded object path to identify both its user and editable project.

create or replace function private.can_upload_research_document(object_name text)
returns boolean
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  folders text[];
  project_id uuid;
begin
  folders := storage.foldername(object_name);
  if array_length(folders, 1) < 2 or folders[1] <> (select auth.uid())::text then
    return false;
  end if;
  begin
    project_id := folders[2]::uuid;
  exception when invalid_text_representation then
    return false;
  end;
  return private.can_edit_project(project_id);
end;
$$;

revoke all on function private.can_upload_research_document(text) from public;
grant execute on function private.can_upload_research_document(text) to authenticated, service_role;

alter policy "research_documents_insert_own" on storage.objects
with check (
  bucket_id = 'research-documents'
  and private.can_upload_research_document(name)
  and lower(storage.extension(name)) = 'pdf'
);

alter policy "research_documents_update_own" on storage.objects
using (
  bucket_id = 'research-documents'
  and owner_id = (select auth.uid())::text
  and private.can_upload_research_document(name)
)
with check (
  bucket_id = 'research-documents'
  and owner_id = (select auth.uid())::text
  and private.can_upload_research_document(name)
);
