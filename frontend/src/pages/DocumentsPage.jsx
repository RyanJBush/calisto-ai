import { useEffect, useState } from "react";

import { fetchDocumentIngestionRuns, listDocuments, uploadDocument } from "../services/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [title, setTitle] = useState("Architecture Notes");
  const [content, setContent] = useState("Calisto AI uses retrieval and citations for trustworthy answers.");
  const [status, setStatus] = useState("");
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [ingestionRuns, setIngestionRuns] = useState([]);

  async function loadDocuments() {
    const data = await listDocuments();
    setDocuments(data);
  }

  useEffect(() => {
    loadDocuments().catch(() => setStatus("Unable to load documents."));
  }, []);

  async function onUpload(event) {
    event.preventDefault();
    try {
      await uploadDocument({ title, content, source_name: `${title}.txt` });
      setStatus("Document uploaded successfully.");
      await loadDocuments();
    } catch {
      setStatus("Upload failed. Ensure your role has access.");
    }
  }

  async function onViewIngestion(documentId) {
    try {
      const runs = await fetchDocumentIngestionRuns(documentId);
      setSelectedDocumentId(documentId);
      setIngestionRuns(runs);
    } catch {
      setSelectedDocumentId(documentId);
      setIngestionRuns([]);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <form onSubmit={onUpload} className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Upload Document</h2>
        <label className="mb-2 block text-sm text-slate-700">Title</label>
        <input value={title} onChange={(event) => setTitle(event.target.value)} className="mb-4 w-full rounded-md border px-3 py-2" />
        <label className="mb-2 block text-sm text-slate-700">Content</label>
        <textarea
          rows={6}
          value={content}
          onChange={(event) => setContent(event.target.value)}
          className="mb-4 w-full rounded-md border px-3 py-2"
        />
        <button className="rounded-md bg-brand-600 px-4 py-2 text-white hover:bg-brand-700">Upload</button>
        {status && <p className="mt-3 text-sm text-slate-600">{status}</p>}
      </form>

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Document Library</h2>
        <ul className="space-y-3">
          {documents.map((doc) => (
            <li key={doc.id} className="rounded-md border border-slate-200 p-3">
              <p className="font-medium text-slate-800">{doc.title}</p>
              <p className="text-xs text-slate-500">Source: {doc.source_name}</p>
              <p className="text-xs text-slate-500">Version: v{doc.version}</p>
              <p className="text-xs text-slate-500">Ingestion: {doc.ingestion_status}</p>
              <p className="text-xs text-slate-500">Attempts: {doc.ingestion_attempts}</p>
              {doc.ingestion_error && <p className="text-xs text-rose-600">Error: {doc.ingestion_error}</p>}
              <button
                type="button"
                onClick={() => onViewIngestion(doc.id)}
                className="mt-2 rounded border border-slate-200 px-2 py-1 text-xs text-slate-700 hover:bg-slate-50"
              >
                View ingestion timeline
              </button>
              {selectedDocumentId === doc.id && (
                <ul className="mt-2 space-y-1 rounded bg-slate-50 p-2 text-xs text-slate-600">
                  {ingestionRuns.map((run) => (
                    <li key={run.id}>
                      #{run.id} {run.status} • attempts {run.attempts}
                    </li>
                  ))}
                  {ingestionRuns.length === 0 && <li>No ingestion runs available.</li>}
                </ul>
              )}
            </li>
          ))}
          {documents.length === 0 && <li className="text-sm text-slate-500">No documents uploaded yet.</li>}
        </ul>
      </section>
    </div>
  );
}
