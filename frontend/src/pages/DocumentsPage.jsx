import { useEffect, useRef, useState } from "react";

import { createCollection, fetchDocumentIngestionRuns, listCollections, listDocuments, previewChunks, uploadDocument } from "../services/api";

const STATUS_COLORS = {
  completed: "bg-emerald-100 text-emerald-700",
  processing: "bg-amber-100 text-amber-700",
  failed: "bg-rose-100 text-rose-700",
  queued: "bg-slate-100 text-slate-600",
};

function StatusBadge({ status }) {
  const color = STATUS_COLORS[status] || "bg-slate-100 text-slate-500";
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize ${color}`}>
      {status}
    </span>
  );
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [title, setTitle] = useState("Architecture Notes");
  const [content, setContent] = useState(
    "Calisto AI uses retrieval and citations for trustworthy answers."
  );
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState("txt");
  const [redactPii, setRedactPii] = useState(false);
  const [collections, setCollections] = useState([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState("");
  const [newCollectionName, setNewCollectionName] = useState("");
  const [statusMsg, setStatusMsg] = useState("");
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [ingestionRuns, setIngestionRuns] = useState([]);
  const [chunkPreview, setChunkPreview] = useState([]);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [chunkSize, setChunkSize] = useState(700);
  const [overlap, setOverlap] = useState(120);
  const [searchFilter, setSearchFilter] = useState("");
  const fileInputRef = useRef(null);

  async function loadDocuments() {
    const data = await listDocuments();
    setDocuments(data);
  }

  async function loadCollections() {
    const data = await listCollections();
    setCollections(data);
  }

  useEffect(() => {
    loadDocuments().catch(() => setStatusMsg("Unable to load documents."));
    loadCollections().catch(() => setCollections([]));
  }, []);

  async function readFileAsBase64(f) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(",")[1]);
      reader.onerror = reject;
      reader.readAsDataURL(f);
    });
  }

  async function onUpload(event) {
    event.preventDefault();
    setStatusMsg("");
    try {
      let payload = {
        title,
        source_name: file ? file.name : `${title}.txt`,
        file_type: file ? fileType : "txt",
        redact_pii: redactPii,
        collection_id: selectedCollectionId ? Number(selectedCollectionId) : null,
      };
      if (file) {
        payload.file_data_base64 = await readFileAsBase64(file);
      } else {
        payload.content = content;
      }
      await uploadDocument(payload);
      setStatusMsg("Document uploaded successfully.");
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      await loadDocuments();
    } catch (err) {
      const msg = err?.response?.data?.detail || "Upload failed. Ensure your role has access.";
      setStatusMsg(msg);
    }
  }

  async function onPreviewChunks() {
    setPreviewLoading(true);
    setChunkPreview([]);
    try {
      let payload = {
        title,
        file_type: file ? fileType : "txt",
        chunk_size: Number(chunkSize),
        overlap: Number(overlap),
      };
      if (file) {
        payload.file_data_base64 = await readFileAsBase64(file);
      } else {
        payload.content = content;
      }
      const result = await previewChunks(payload);
      setChunkPreview(result.chunks || []);
    } catch {
      setChunkPreview([]);
    } finally {
      setPreviewLoading(false);
    }
  }

  async function onCreateCollection(event) {
    event.preventDefault();
    if (!newCollectionName.trim()) return;
    try {
      await createCollection({ name: newCollectionName.trim() });
      setNewCollectionName("");
      await loadCollections();
    } catch {
      setStatusMsg("Unable to create collection.");
    }
  }

  async function onViewIngestion(documentId) {
    try {
      const runs = await fetchDocumentIngestionRuns(documentId);
      setSelectedDocumentId((prev) => (prev === documentId ? null : documentId));
      setIngestionRuns(runs);
    } catch {
      setSelectedDocumentId((prev) => (prev === documentId ? null : documentId));
      setIngestionRuns([]);
    }
  }

  const filteredDocuments = documents.filter(
    (doc) =>
      !searchFilter ||
      doc.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
      doc.source_name.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="grid gap-6 lg:grid-cols-[400px_minmax(0,1fr)]">
      {/* Upload form */}
      <div className="space-y-4">
        <form onSubmit={onUpload} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="mb-4 text-base font-semibold text-slate-900">Upload Document</h2>

          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Title</label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">
                File (PDF, TXT, MD)
              </label>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.txt,.md"
                onChange={(e) => {
                  const f = e.target.files[0];
                  if (!f) return;
                  setFile(f);
                  const ext = f.name.split(".").pop().toLowerCase();
                  if (["pdf", "txt", "md"].includes(ext)) setFileType(ext);
                }}
                className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-blue-50 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-blue-700 hover:file:bg-blue-100"
              />
              {file && (
                <p className="mt-1 text-xs text-slate-500">
                  {file.name} — {(file.size / 1024).toFixed(1)} KB
                </p>
              )}
            </div>

            {!file && (
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-600">
                  Paste content
                </label>
                <textarea
                  rows={5}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full resize-y rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>
            )}

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Collection</label>
              <select
                value={selectedCollectionId}
                onChange={(e) => setSelectedCollectionId(e.target.value)}
                className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
              >
                <option value="">No collection</option>
                {collections.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <label className="inline-flex items-center gap-2 text-sm text-slate-600">
              <input
                type="checkbox"
                checked={redactPii}
                onChange={(e) => setRedactPii(e.target.checked)}
                className="rounded border-slate-300"
              />
              Redact PII before indexing
            </label>
          </div>

          <div className="mt-4 flex gap-2">
            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Upload
            </button>
            <button
              type="button"
              onClick={onPreviewChunks}
              disabled={previewLoading}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-50"
            >
              {previewLoading ? "Previewing…" : "Preview chunks"}
            </button>
          </div>

          {statusMsg && (
            <p
              className={`mt-3 text-sm ${
                statusMsg.includes("success") ? "text-emerald-600" : "text-rose-600"
              }`}
            >
              {statusMsg}
            </p>
          )}
        </form>

        {/* Chunk settings */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-slate-700">Chunking Settings</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Chunk size (chars)
              </label>
              <input
                type="number"
                value={chunkSize}
                onChange={(e) => setChunkSize(e.target.value)}
                min={100}
                max={4000}
                className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Overlap (chars)
              </label>
              <input
                type="number"
                value={overlap}
                onChange={(e) => setOverlap(e.target.value)}
                min={0}
                max={500}
                className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-sm"
              />
            </div>
          </div>
        </div>

        {/* Chunk preview */}
        {chunkPreview.length > 0 && (
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">
              Chunk Preview ({chunkPreview.length} chunks)
            </h3>
            <ul className="max-h-[360px] space-y-2 overflow-auto">
              {chunkPreview.map((chunk, i) => (
                <li
                  key={i}
                  className="rounded-lg border border-slate-100 bg-slate-50 p-3 text-xs text-slate-700"
                >
                  <p className="mb-1 font-medium text-slate-400">Chunk {i + 1}</p>
                  <p className="leading-relaxed line-clamp-4">{chunk}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Create collection */}
        <form
          onSubmit={onCreateCollection}
          className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
        >
          <h3 className="mb-3 text-sm font-semibold text-slate-700">New Collection</h3>
          <div className="flex gap-2">
            <input
              value={newCollectionName}
              onChange={(e) => setNewCollectionName(e.target.value)}
              placeholder="e.g. HR Policies"
              className="flex-1 rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <button
              type="submit"
              className="rounded-md border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50"
            >
              Create
            </button>
          </div>
        </form>
      </div>

      {/* Document library */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-base font-semibold text-slate-900">
            Document Library ({documents.length})
          </h2>
          <input
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Search…"
            className="rounded-md border border-slate-200 px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>

        {filteredDocuments.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-200 p-8 text-center">
            <p className="text-sm text-slate-400">
              {documents.length === 0
                ? "No documents uploaded yet."
                : "No documents match your search."}
            </p>
          </div>
        ) : (
          <ul className="space-y-3">
            {filteredDocuments.map((doc) => (
              <li
                key={doc.id}
                className="rounded-lg border border-slate-100 bg-slate-50 p-4 transition-colors hover:border-slate-200"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-800">{doc.title}</p>
                    <p className="mt-0.5 truncate text-xs text-slate-400">{doc.source_name}</p>
                  </div>
                  <StatusBadge status={doc.ingestion_status} />
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400">
                  <span>v{doc.version}</span>
                  {doc.collection_id && <span>Collection #{doc.collection_id}</span>}
                  <span>Attempts: {doc.ingestion_attempts}</span>
                </div>
                {doc.ingestion_error && (
                  <p className="mt-1.5 text-xs text-rose-600">Error: {doc.ingestion_error}</p>
                )}
                <button
                  type="button"
                  onClick={() => onViewIngestion(doc.id)}
                  className="mt-2 rounded-md border border-slate-200 px-2.5 py-1 text-xs text-slate-600 hover:bg-white"
                >
                  {selectedDocumentId === doc.id ? "Hide" : "View"} ingestion timeline
                </button>
                {selectedDocumentId === doc.id && (
                  <ul className="mt-2 space-y-1 rounded-lg border border-slate-100 bg-white p-3 text-xs">
                    {ingestionRuns.map((run) => (
                      <li key={run.id} className="flex items-center gap-2 text-slate-600">
                        <StatusBadge status={run.status} />
                        <span>Run #{run.id} · {run.attempts} attempt{run.attempts !== 1 ? "s" : ""}</span>
                        {run.error_message && (
                          <span className="text-rose-500">— {run.error_message}</span>
                        )}
                      </li>
                    ))}
                    {ingestionRuns.length === 0 && (
                      <li className="text-slate-400">No ingestion runs recorded.</li>
                    )}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

