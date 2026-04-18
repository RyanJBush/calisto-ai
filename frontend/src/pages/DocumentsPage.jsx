import { useEffect, useState } from "react";

import { listDocuments, uploadDocument } from "../services/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [title, setTitle] = useState("Architecture Notes");
  const [content, setContent] = useState("Calisto AI uses retrieval and citations for trustworthy answers.");
  const [status, setStatus] = useState("");

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
            </li>
          ))}
          {documents.length === 0 && <li className="text-sm text-slate-500">No documents uploaded yet.</li>}
        </ul>
      </section>
    </div>
  );
}
