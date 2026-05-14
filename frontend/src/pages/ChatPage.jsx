import { useEffect, useRef, useState } from "react";

import { fetchHistory, listDocuments, streamChatQuery, submitChatFeedback } from "../services/api";

const DEMO_QUERIES = [
  "What is the leave policy?",
  "How fast do we respond to critical support tickets?",
  "What is the escalation window for P1 incidents?",
  "How often are performance reviews conducted?",
  "What is the data retention period for customer documents?",
  "How do I request reimbursement for business expenses?",
];

function ConfidenceBadge({ score }) {
  const pct = Math.round((score || 0) * 100);
  const color =
    pct >= 70 ? "bg-emerald-100 text-emerald-700" :
    pct >= 40 ? "bg-amber-100 text-amber-700" :
                "bg-rose-100 text-rose-700";
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {pct}% confidence
    </span>
  );
}

function CitationCard({ citation, selected, onSelect }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(citation)}
      className={`w-full rounded-lg border p-3 text-left text-sm transition-colors ${
        selected
          ? "border-blue-500 bg-blue-50 shadow-sm"
          : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <p className="font-medium text-slate-800 leading-tight">{citation.document_title}</p>
        <span className="shrink-0 rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500">
          {Math.round(citation.retrieval_score * 100)}%
        </span>
      </div>
      {citation.section_label && (
        <p className="mt-0.5 text-xs text-blue-600">{citation.section_label}</p>
      )}
      <p className="mt-1.5 line-clamp-2 text-xs text-slate-600">{citation.snippet}</p>
      <p className="mt-1 text-xs text-slate-400">Chunk #{citation.chunk_id}</p>
    </button>
  );
}

function HighlightedPreview({ citation }) {
  const ranges = citation.highlight_ranges?.length
    ? citation.highlight_ranges
    : [[citation.highlight_start, citation.highlight_end]];

  const fragments = [];
  let cursor = 0;
  ranges.forEach(([start, end], index) => {
    const safeStart = Math.max(cursor, start);
    const safeEnd = Math.max(safeStart, end);
    if (safeStart > cursor) {
      fragments.push(
        <span key={`plain-${index}`}>{citation.source_preview.slice(cursor, safeStart)}</span>
      );
    }
    fragments.push(
      <mark key={`mark-${index}`} className="rounded bg-amber-200 px-0.5 text-amber-900">
        {citation.source_preview.slice(safeStart, safeEnd)}
      </mark>
    );
    cursor = safeEnd;
  });
  if (cursor < citation.source_preview.length) {
    fragments.push(<span key="tail">{citation.source_preview.slice(cursor)}</span>);
  }
  return <>{fragments}</>;
}

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [history, setHistory] = useState([]);
  const [confidenceScore, setConfidenceScore] = useState(null);
  const [citationCoverage, setCitationCoverage] = useState(null);
  const [insufficientEvidence, setInsufficientEvidence] = useState(false);
  const [rewrittenQuery, setRewrittenQuery] = useState("");
  const [latencyBreakdown, setLatencyBreakdown] = useState(null);
  const [assistantMessageId, setAssistantMessageId] = useState(null);
  const [answerMode, setAnswerMode] = useState("");
  const [evidenceSummary, setEvidenceSummary] = useState([]);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [feedbackStatus, setFeedbackStatus] = useState("");
  const [historyFilter, setHistoryFilter] = useState("");
  const [collectionFilterId, setCollectionFilterId] = useState("");
  const [citationSort, setCitationSort] = useState("relevance");
  const [sourceDrawerOpen, setSourceDrawerOpen] = useState(true);
  const [documents, setDocuments] = useState([]);
  const [isLoadingAnswer, setIsLoadingAnswer] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [showEvidence, setShowEvidence] = useState(false);
  const [showLatency, setShowLatency] = useState(false);

  const answerRef = useRef(null);

  async function loadHistory() {
    const data = await fetchHistory();
    setHistory(data);
  }

  async function loadDocuments() {
    const data = await listDocuments();
    setDocuments(data);
  }

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
    loadDocuments().catch(() => setDocuments([]));
  }, []);

  async function onAsk(event) {
    if (event) event.preventDefault();
    if (!query.trim()) {
      setErrorMessage("Please enter a question before submitting.");
      return;
    }
    setIsLoadingAnswer(true);
    setErrorMessage("");
    setAnswer("");
    setCitations([]);
    setSelectedCitation(null);
    setEvidenceSummary([]);
    setFeedbackStatus("");
    setFeedbackComment("");
    try {
      let finalResponse = null;
      await streamChatQuery(
        {
          query,
          filters: collectionFilterId ? { collection_id: Number(collectionFilterId) } : undefined,
        },
        (eventData) => {
          if (eventData.token) {
            setAnswer((prev) => prev + eventData.token);
          }
          if (eventData.done) {
            finalResponse = eventData;
          }
        }
      );
      const orderedCitations = [...(finalResponse?.citations || [])].sort(
        (a, b) => b.retrieval_score - a.retrieval_score
      );
      setCitations(orderedCitations);
      setSelectedCitation(orderedCitations[0] || null);
      setSourceDrawerOpen(Boolean(orderedCitations[0]));
      setAnswerMode(finalResponse?.answer_mode);
      setEvidenceSummary(finalResponse?.evidence_summary || []);
      setConfidenceScore(finalResponse?.confidence_score);
      setCitationCoverage(finalResponse?.citation_coverage);
      setInsufficientEvidence(finalResponse?.insufficient_evidence);
      setRewrittenQuery(finalResponse?.rewritten_query);
      setLatencyBreakdown(finalResponse?.latency_breakdown_ms);
      setAssistantMessageId(finalResponse?.assistant_message_id);
      await loadHistory();
      setTimeout(() => answerRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch {
      setErrorMessage("Failed to retrieve answer. Please try again.");
    } finally {
      setIsLoadingAnswer(false);
    }
  }

  const sortedCitations = [...citations].sort((a, b) => {
    if (citationSort === "title") return a.document_title.localeCompare(b.document_title);
    return b.retrieval_score - a.retrieval_score;
  });

  async function onFeedback(rating) {
    if (!assistantMessageId) return;
    try {
      await submitChatFeedback({
        message_id: assistantMessageId,
        rating,
        comment: feedbackComment || null,
      });
      setFeedbackStatus("Feedback submitted. Thank you!");
      await loadHistory();
    } catch {
      setFeedbackStatus("Unable to submit feedback.");
    }
  }

  const filteredHistory = history
    .filter((item) => item.content.toLowerCase().includes(historyFilter.toLowerCase()))
    .slice(-10);

  return (
    <div className="grid gap-6 xl:grid-cols-[260px_minmax(0,1fr)]">
      {/* Left sidebar */}
      <aside className="space-y-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Indexed Sources
          </h3>
          <p className="mb-3 text-xs text-slate-500">
            {documents.length} document{documents.length !== 1 ? "s" : ""} available
          </p>
          <ul className="max-h-[360px] space-y-2 overflow-auto pr-1">
            {documents.map((doc) => (
              <li key={doc.id} className="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2">
                <p className="text-xs font-medium text-slate-700 leading-tight">{doc.title}</p>
                <div className="mt-1 flex items-center gap-1.5">
                  <span
                    className={`inline-block h-1.5 w-1.5 rounded-full ${
                      doc.ingestion_status === "completed"
                        ? "bg-emerald-400"
                        : doc.ingestion_status === "processing"
                        ? "bg-amber-400"
                        : doc.ingestion_status === "failed"
                        ? "bg-rose-400"
                        : "bg-slate-300"
                    }`}
                  />
                  <span className="text-xs text-slate-400 capitalize">{doc.ingestion_status}</span>
                </div>
              </li>
            ))}
            {documents.length === 0 && (
              <li className="rounded-lg border border-dashed border-slate-200 p-3 text-center text-xs text-slate-400">
                No documents yet.
                <br />
                <a href="/documents" className="text-blue-500 underline">
                  Upload one →
                </a>
              </li>
            )}
          </ul>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-400">
            Filter by Collection
          </label>
          <input
            value={collectionFilterId}
            onChange={(e) => setCollectionFilterId(e.target.value)}
            placeholder="Collection ID (optional)"
            className="w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Recent History
          </h3>
          <input
            value={historyFilter}
            onChange={(e) => setHistoryFilter(e.target.value)}
            placeholder="Filter…"
            className="mb-2 w-full rounded-md border border-slate-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <ul className="max-h-[240px] space-y-1.5 overflow-auto">
            {filteredHistory.map((item) => (
              <li key={item.id} className="rounded bg-slate-50 px-2 py-1.5 text-xs text-slate-600">
                <span
                  className={`mr-1 font-semibold ${
                    item.role === "user" ? "text-blue-600" : "text-emerald-600"
                  }`}
                >
                  {item.role === "user" ? "You:" : "AI:"}
                </span>
                <span className="line-clamp-2">{item.content}</span>
              </li>
            ))}
            {filteredHistory.length === 0 && (
              <li className="py-2 text-center text-xs text-slate-400">No history yet.</li>
            )}
          </ul>
        </div>
      </aside>

      {/* Main content */}
      <div className="space-y-5">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="mb-3 text-base font-semibold text-slate-900">Ask your knowledge base</h2>

          <div className="mb-3 flex flex-wrap gap-2">
            {DEMO_QUERIES.map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setQuery(item)}
                className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600 transition-colors hover:border-blue-300 hover:bg-blue-50 hover:text-blue-700"
              >
                {item}
              </button>
            ))}
          </div>

          <form onSubmit={onAsk} className="flex gap-3">
            <textarea
              rows={2}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  onAsk();
                }
              }}
              placeholder="Type your question… (Enter to submit)"
              className="flex-1 resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <button
              type="submit"
              disabled={isLoadingAnswer}
              className="self-end rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoadingAnswer ? (
                <span className="inline-flex items-center gap-1.5">
                  <svg className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"
                    />
                  </svg>
                  Thinking…
                </span>
              ) : (
                "Ask"
              )}
            </button>
          </form>
        </div>

        {errorMessage && (
          <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            <svg className="h-4 w-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm-.75-11.25a.75.75 0 011.5 0v4a.75.75 0 01-1.5 0v-4zm.75 7a.75.75 0 100-1.5.75.75 0 000 1.5z"
                clipRule="evenodd"
              />
            </svg>
            {errorMessage}
          </div>
        )}

        {!answer && !isLoadingAnswer && !errorMessage && (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white px-8 py-12 text-center">
            <svg
              className="mx-auto mb-3 h-8 w-8 text-slate-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-sm text-slate-500">
              Ask a question to receive grounded answers with citations and source previews.
            </p>
            <p className="mt-1 text-xs text-slate-400">Click any example above to get started.</p>
          </div>
        )}

        {answer && (
          <div ref={answerRef} className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
            <div className="space-y-4">
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Answer</h3>
                  <div className="flex items-center gap-2">
                    {confidenceScore !== null && <ConfidenceBadge score={confidenceScore} />}
                    {insufficientEvidence && (
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                        Low evidence
                      </span>
                    )}
                  </div>
                </div>
                <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800">{answer}</p>

                <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 border-t border-slate-100 pt-3 text-xs text-slate-400">
                  {rewrittenQuery && rewrittenQuery !== query && (
                    <span>
                      Rewritten:{" "}
                      <span className="italic text-slate-500">&ldquo;{rewrittenQuery}&rdquo;</span>
                    </span>
                  )}
                  <span>Coverage: {Math.round((citationCoverage || 0) * 100)}%</span>
                  <span>Mode: {answerMode || "n/a"}</span>
                  <button
                    type="button"
                    onClick={() => setShowLatency((v) => !v)}
                    className="text-blue-400 hover:text-blue-600"
                  >
                    {showLatency ? "Hide latency" : "Show latency"}
                  </button>
                </div>
                {showLatency && latencyBreakdown && (
                  <div className="mt-2 grid grid-cols-4 gap-2 rounded-lg bg-slate-50 p-3 text-center text-xs text-slate-500">
                    {Object.entries(latencyBreakdown).map(([k, v]) => (
                      <div key={k}>
                        <p className="font-semibold text-slate-700">{v.toFixed(0)} ms</p>
                        <p className="capitalize">{k}</p>
                      </div>
                    ))}
                  </div>
                )}

                {evidenceSummary.length > 0 && (
                  <div className="mt-3">
                    <button
                      type="button"
                      onClick={() => setShowEvidence((v) => !v)}
                      className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-800"
                    >
                      <svg
                        className={`h-3.5 w-3.5 transition-transform ${showEvidence ? "rotate-90" : ""}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                      {showEvidence ? "Hide" : "Show"} top evidence ({evidenceSummary.length})
                    </button>
                    {showEvidence && (
                      <ul className="mt-2 space-y-1.5 rounded-lg border border-slate-100 bg-slate-50 p-3">
                        {evidenceSummary.map((item) => (
                          <li key={item} className="text-xs leading-relaxed text-slate-600">
                            • {item}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}

                <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-3">
                  <span className="text-xs text-slate-400">Was this helpful?</span>
                  <button
                    type="button"
                    onClick={() => onFeedback(1)}
                    className="rounded-md border border-slate-200 px-2.5 py-1 text-xs text-slate-600 hover:border-emerald-300 hover:bg-emerald-50 hover:text-emerald-700"
                  >
                    👍 Yes
                  </button>
                  <button
                    type="button"
                    onClick={() => onFeedback(-1)}
                    className="rounded-md border border-slate-200 px-2.5 py-1 text-xs text-slate-600 hover:border-rose-300 hover:bg-rose-50 hover:text-rose-700"
                  >
                    👎 No
                  </button>
                  <input
                    value={feedbackComment}
                    onChange={(e) => setFeedbackComment(e.target.value)}
                    placeholder="Optional comment…"
                    className="min-w-0 flex-1 rounded-md border border-slate-200 px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-blue-200"
                  />
                  {feedbackStatus && (
                    <span className="text-xs text-slate-500">{feedbackStatus}</span>
                  )}
                </div>
              </div>

              {citations.length > 0 && (
                <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                      Citations ({citations.length})
                    </h3>
                    <select
                      value={citationSort}
                      onChange={(e) => setCitationSort(e.target.value)}
                      className="rounded border border-slate-200 px-2 py-1 text-xs focus:outline-none"
                    >
                      <option value="relevance">By relevance</option>
                      <option value="title">By title</option>
                    </select>
                  </div>
                  <ul className="space-y-2">
                    {sortedCitations.map((citation) => (
                      <li key={citation.chunk_id}>
                        <CitationCard
                          citation={citation}
                          selected={selectedCitation?.chunk_id === citation.chunk_id}
                          onSelect={setSelectedCitation}
                        />
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Source preview panel */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:sticky lg:top-4 lg:self-start">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                  Source Preview
                </h3>
                <button
                  type="button"
                  onClick={() => setSourceDrawerOpen((v) => !v)}
                  className="text-xs text-blue-500 hover:text-blue-700"
                >
                  {sourceDrawerOpen ? "Collapse" : "Expand"}
                </button>
              </div>

              {!sourceDrawerOpen ? (
                <p className="text-xs text-slate-400">
                  Click Expand to inspect highlighted evidence.
                </p>
              ) : selectedCitation ? (
                <div>
                  <div className="mb-2 rounded-lg bg-blue-50 px-3 py-2">
                    <p className="text-xs font-medium text-blue-700">
                      {selectedCitation.document_title}
                    </p>
                    {selectedCitation.section_label && (
                      <p className="text-xs text-blue-500">{selectedCitation.section_label}</p>
                    )}
                  </div>
                  <p className="whitespace-pre-wrap text-xs leading-relaxed text-slate-700">
                    <HighlightedPreview citation={selectedCitation} />
                  </p>
                  <p className="mt-3 text-xs text-slate-400">
                    Relevance: {Math.round(selectedCitation.retrieval_score * 100)}% · Chunk #
                    {selectedCitation.chunk_id}
                  </p>
                </div>
              ) : (
                <p className="text-xs text-slate-400">
                  Select a citation to preview the source text with highlighted evidence.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

