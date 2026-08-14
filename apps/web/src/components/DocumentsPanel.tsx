import { FileText, LoaderCircle, Trash2, UploadCloud } from "lucide-react";
import { ChangeEvent, useState } from "react";

import { deleteDocument, ingestDocument, registerDocument } from "../api/client";
import { supabase } from "../lib/supabase";
import type { ResearchDocument } from "../types/research";

interface DocumentsPanelProps {
  accessToken: string;
  projectId: string;
  userId: string;
  documents: ResearchDocument[];
  onChange: (documents: ResearchDocument[]) => void;
}

export function DocumentsPanel({ accessToken, projectId, userId, documents, onChange }: DocumentsPanelProps) {
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || !supabase) return;
    if (file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) {
      setMessage("Choose a PDF file.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setMessage("PDFs must be 10 MB or smaller.");
      return;
    }
    if (documents.length >= 2) {
      setMessage("The public MVP allows two PDFs per project run.");
      return;
    }
    setWorking(true);
    setMessage("Uploading to your private Supabase bucket…");
    const safeName = file.name.replace(/[^A-Za-z0-9._-]+/g, "-");
    const path = `${userId}/${projectId}/${crypto.randomUUID()}-${safeName}`;
    const uploaded = await supabase.storage.from("research-documents").upload(path, file, {
      contentType: "application/pdf",
      upsert: false,
    });
    if (uploaded.error) {
      setWorking(false);
      setMessage(uploaded.error.message);
      return;
    }
    try {
      const registered = await registerDocument(accessToken, projectId, {
        filename: file.name,
        storage_path: path,
        mime_type: "application/pdf",
        size_bytes: file.size,
      });
      onChange([registered, ...documents]);
      setMessage("Parsing pages, creating chunks, and indexing retrieval vectors…");
      const result = await ingestDocument(accessToken, registered.id);
      onChange([result.document, ...documents]);
      setMessage(
        `Ready: ${result.chunk_count} page-aware chunks${
          result.possible_scan_pages.length ? `; possible scans on pages ${result.possible_scan_pages.join(", ")}` : ""
        }.`,
      );
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Document processing failed.");
    } finally {
      setWorking(false);
    }
  }

  async function remove(document: ResearchDocument) {
    if (!window.confirm(`Delete ${document.filename} and all of its chunks?`)) return;
    await deleteDocument(accessToken, document.id);
    onChange(documents.filter((item) => item.id !== document.id));
  }

  return (
    <section className="panel documents-panel">
      <div className="panel-header">
        <div><span className="eyebrow">Private project evidence</span><h2>Documents</h2></div>
        <label className={`upload-button ${working ? "disabled" : ""}`}>
          {working ? <LoaderCircle className="spin" size={17} /> : <UploadCloud size={17} />}
          Upload PDF
          <input type="file" accept="application/pdf,.pdf" onChange={upload} disabled={working} />
        </label>
      </div>
      <p className="panel-intro">PDFs are private, owner-scoped, limited to 10 MB and 150 pages, and cited by filename and page.</p>
      {message && <div className="status-message">{message}</div>}
      <div className="document-list">
        {documents.length === 0 && <div className="empty-state">No project PDFs yet.</div>}
        {documents.map((document) => (
          <article className="document-row" key={document.id}>
            <FileText size={20} />
            <div><strong>{document.filename}</strong><small>{(document.size_bytes / 1024 / 1024).toFixed(2)} MB · {document.page_count ?? "—"} pages</small></div>
            <span className={`document-status ${document.status}`}>{document.status}</span>
            <button type="button" aria-label={`Delete ${document.filename}`} onClick={() => void remove(document)}><Trash2 size={16} /></button>
          </article>
        ))}
      </div>
    </section>
  );
}
