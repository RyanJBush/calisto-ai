import { useEffect, useState } from "react";

import {
  createCollection,
  fetchDocumentIngestionRuns,
  listCollections,
  listDocuments,
  retryDocumentIngestion,
  uploadDocument,
  uploadDocumentFile
} from "../services/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [title, setTitle] = useState("Architecture Notes");
  const [content, setContent] = useState("Calisto AI uses retrieval and citations for trustworthy answers.");
  const [redactPii, setRedactPii] = useState(false);
  const [collections, setCollections] = useState([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState("");
  const [newCollectionName, setNewCollectionName] = useState("");
  const [status, setStatus] = useState("");
  const [file, setFile] = useState(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [ingestionRuns, setIngestionRuns] = useState([]);

  async function loadDocuments() {
    const data = await listDocuments();
    setDocuments(data);
  }

  async function loadCollections() {
    const data = await listCollections();
    setCollections(data);
  }

  useEffect(() => {
    loadDocuments().catch(() => setStatus("Unable to load documents."));
    loadCollections().catch(() => setCollections([]));
  }, []);

  async function onUpload(event) {
    event.preventDefault();
    try {
      await uploadDocument({
        title,
        content,
        source_name: `${title}.txt`,
        redact_pii: redactPii,
        collection_id: selectedCollectionId ? Number(selectedCollectionId) : null
      });
      setStatus("Document uploaded successfully.");
      await loadDocuments();
    } catch {
      setStatus("Upload failed. Ensure your role has access.");
    }
  }

  async function onUploadFile(event) {
    event.preventDefault();
    if (!file) {
      setStatus("Choose a file before uploading.");
      return;
    }
    try {
      await uploadDocumentFile({
        title,
        file,
        source_name: file.name,
        redact_pii: redactPii,
        collection_id: selectedCollectionId ? Number(selectedCollectionId) : null
      });
      setStatus("File uploaded successfully.");
      setFile(null);
      await loadDocuments();
    } catch {
      setStatus("File upload failed.");
    }
  }

  async function onCreateCollection(event) {
    event.preventDefault();
    if (!newCollectionName.trim()) {
      return;
    }
    try {
      await createCollection({ name: newCollectionName.trim() });
      setNewCollectionName("");
      await loadCollections();
    } catch {
      setStatus("Unable to create collection.");
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

  async function onRetryIngestion(documentId) {
    try {
      await retryDocumentIngestion(documentId);
      setStatus("Ingestion retry queued.");
      await onViewIngestion(documentId);
      await loadDocuments();
    } catch {
      setStatus("Unable to retry ingestion.");
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
        <label className="mb-2 block text-sm text-slate-700">Collection</label>
        <select
          value={selectedCollectionId}
          onChange={(event) => setSelectedCollectionId(event.target.value)}
          className="mb-4 w-full rounded-md border px-3 py-2"
        >
          <option value="">No collection</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
        <button className="rounded-md bg-brand-600 px-4 py-2 text-white hover:bg-brand-700">Upload</button>
        <label className="ml-3 inline-flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" checked={redactPii} onChange={(event) => setRedactPii(event.target.checked)} />
          Redact PII before indexing
        </label>
        {status && <p className="mt-3 text-sm text-slate-600">{status}</p>}

        <div className="mt-4 border-t pt-4">
          <label className="mb-2 block text-sm text-slate-700">Upload File (TXT/MD/JSON/PDF)</label>
          <div className="space-y-2">
            <input
              type="file"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
              className="w-full rounded-md border px-3 py-2 text-sm"
            />
            <button type="button" onClick={onUploadFile} className="rounded-md border border-slate-300 px-3 py-2 text-sm">
              Upload File
            </button>
          </div>
        </div>

        <div className="mt-4 border-t pt-4">
          <label className="mb-2 block text-sm text-slate-700">Create Collection</label>
          <div className="flex gap-2">
            <input
              value={newCollectionName}
              onChange={(event) => setNewCollectionName(event.target.value)}
              className="w-full rounded-md border px-3 py-2"
              placeholder="e.g. Product Docs"
            />
            <button type="button" onClick={onCreateCollection} className="rounded-md border border-slate-300 px-3 py-2 text-sm">
              Create
            </button>
          </div>
        </div>
      </form>

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Document Library</h2>
        <ul className="space-y-3">
          {documents.map((doc) => (
            <li key={doc.id} className="rounded-md border border-slate-200 p-3">
              <p className="font-medium text-slate-800">{doc.title}</p>
              <p className="text-xs text-slate-500">Source: {doc.source_name}</p>
              <p className="text-xs text-slate-500">Version: v{doc.version}</p>
              <p className="text-xs text-slate-500">Collection ID: {doc.collection_id ?? "None"}</p>
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
              <button
                type="button"
                onClick={() => onRetryIngestion(doc.id)}
                className="ml-2 mt-2 rounded border border-amber-200 px-2 py-1 text-xs text-amber-700 hover:bg-amber-50"
              >
                Retry ingestion
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
