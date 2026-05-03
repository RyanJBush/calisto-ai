import { useEffect, useState } from "react";

import { fetchHistory, listDocuments, queryChat, submitChatFeedback } from "../services/api";

export default function ChatPage() {
  const demoQueries = [
    "What is the leave policy?",
    "How fast do we respond to critical support tickets?",
    "What is the escalation window for P1 incidents?"
  ];
  const [query, setQuery] = useState("What is Calisto AI?");
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
  const [sourceDrawerOpen, setSourceDrawerOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [isLoadingAnswer, setIsLoadingAnswer] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

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
    event.preventDefault();
    if (!query.trim()) {
      setErrorMessage("Please enter a question before submitting.");
      return;
    }
    setIsLoadingAnswer(true);
    setErrorMessage("");
    try {
      const response = await queryChat({
        query,
        filters: collectionFilterId ? { collection_id: Number(collectionFilterId) } : undefined
      });
      const orderedCitations = [...response.citations].sort((left, right) => right.retrieval_score - left.retrieval_score);
      setAnswer(response.answer);
      setCitations(orderedCitations);
      setSelectedCitation(orderedCitations[0] || null);
      setSourceDrawerOpen(Boolean(orderedCitations[0]));
      setAnswerMode(response.answer_mode);
      setEvidenceSummary(response.evidence_summary || []);
      setConfidenceScore(response.confidence_score);
      setCitationCoverage(response.citation_coverage);
      setInsufficientEvidence(response.insufficient_evidence);
      setRewrittenQuery(response.rewritten_query);
      setLatencyBreakdown(response.latency_breakdown_ms);
      setAssistantMessageId(response.assistant_message_id);
      setFeedbackStatus("");
      setFeedbackComment("");
      await loadHistory();
    } catch {
      setErrorMessage("Failed to retrieve answer. Please try again.");
    } finally {
      setIsLoadingAnswer(false);
    }
  }

  const sortedCitations = [...citations].sort((left, right) => {
    if (citationSort === "title") {
      return left.document_title.localeCompare(right.document_title);
    }
    return right.retrieval_score - left.retrieval_score;
  });

  async function onFeedback(rating) {
    if (!assistantMessageId) {
      return;
    }
    try {
      await submitChatFeedback({ message_id: assistantMessageId, rating, comment: feedbackComment || null });
      setFeedbackStatus("Feedback submitted.");
      await loadHistory();
    } catch {
      setFeedbackStatus("Unable to submit feedback.");
    }
  }

  function renderHighlightedPreview(citation) {
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
        <mark key={`mark-${index}`} className="rounded bg-amber-200 px-0.5">
          {citation.source_preview.slice(safeStart, safeEnd)}
        </mark>
      );
      cursor = safeEnd;
    });
    if (cursor < citation.source_preview.length) {
      fragments.push(<span key="tail">{citation.source_preview.slice(cursor)}</span>);
    }
    return fragments;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)]">
      <aside className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Documents</h3>
        <p className="mt-1 text-xs text-slate-500">Indexed sources available for retrieval.</p>
        <ul className="mt-3 max-h-[460px] space-y-2 overflow-auto pr-1">
          {documents.map((doc) => (
            <li key={doc.id} className="rounded-lg border border-slate-200 px-3 py-2">
              <p className="text-sm font-medium text-slate-800">{doc.title}</p>
              <p className="text-xs text-slate-500">Status: {doc.ingestion_status}</p>
            </li>
          ))}
          {documents.length === 0 && <li className="rounded-lg bg-slate-50 p-3 text-xs text-slate-500">No documents yet.</li>}
        </ul>
      </aside>
      <div className="space-y-6">
      <form onSubmit={onAsk} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Citation-Aware Chat</h2>
        <textarea
          rows={3}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="mb-3 w-full rounded-md border border-slate-300 px-3 py-2"
        />
        <div className="mb-3 flex flex-wrap gap-2">
          {demoQueries.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setQuery(item)}
              className="rounded-full border border-slate-300 px-3 py-1 text-xs text-slate-600 hover:bg-slate-100"
            >
              {item}
            </button>
          ))}
        </div>
        <button disabled={isLoadingAnswer} className="rounded-md bg-brand-600 px-4 py-2 text-white hover:bg-brand-700 disabled:opacity-60">{isLoadingAnswer ? "Thinking..." : "Ask"}</button>
        <input
          value={collectionFilterId}
          onChange={(event) => setCollectionFilterId(event.target.value)}
          placeholder="Collection ID filter (optional)"
          className="ml-3 rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
      </form>

      {errorMessage && <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{errorMessage}</div>}
      {answer && (
        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <h3 className="text-sm font-semibold uppercase text-slate-500">Answer</h3>
            <p className="mt-2 text-slate-800">{answer}</p>
            <div className="mt-3 space-y-1 text-xs text-slate-500">
              <p>Rewritten Query: {rewrittenQuery}</p>
              <p>Confidence: {((confidenceScore || 0) * 100).toFixed(0)}%</p>
              <p>Citation Coverage: {((citationCoverage || 0) * 100).toFixed(0)}%</p>
              <p>Answer Mode: {answerMode || "n/a"}</p>
              {latencyBreakdown && (
                <p>
                  Latency (ms): rewrite {latencyBreakdown.rewrite}, retrieval {latencyBreakdown.retrieval}, answer{" "}
                  {latencyBreakdown.answer}, total {latencyBreakdown.total}
                </p>
              )}
              {insufficientEvidence && <p className="font-medium text-amber-600">Insufficient evidence fallback active.</p>}
            </div>
            {evidenceSummary.length > 0 && (
              <div className="mt-3 rounded border border-slate-200 bg-slate-50 p-2">
                <p className="text-xs font-semibold uppercase text-slate-500">Top Evidence</p>
                <ul className="mt-1 list-disc space-y-1 pl-4 text-xs text-slate-700">
                  {evidenceSummary.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            <div className="mt-3 flex items-center gap-2">
              <button
                type="button"
                onClick={() => onFeedback(1)}
                className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-700 hover:bg-slate-50"
              >
                👍 Helpful
              </button>
              <button
                type="button"
                onClick={() => onFeedback(-1)}
                className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-700 hover:bg-slate-50"
              >
                👎 Not helpful
              </button>
              <input
                value={feedbackComment}
                onChange={(event) => setFeedbackComment(event.target.value)}
                placeholder="Optional feedback"
                className="w-full rounded border border-slate-300 px-2 py-1 text-xs"
              />
            </div>
            {feedbackStatus && <p className="mt-1 text-xs text-slate-500">{feedbackStatus}</p>}
            <h4 className="mt-4 text-sm font-semibold uppercase text-slate-500">Citations</h4>
            <div className="mt-2">
              <select
                value={citationSort}
                onChange={(event) => setCitationSort(event.target.value)}
                className="rounded border border-slate-300 px-2 py-1 text-xs"
              >
                <option value="relevance">Sort by relevance</option>
                <option value="title">Sort by title</option>
              </select>
            </div>
            <ul className="mt-2 space-y-2">
              {sortedCitations.map((citation) => (
                <li key={citation.chunk_id}>
                  <button
                    type="button"
                    onClick={() => setSelectedCitation(citation)}
                    className={`w-full rounded-md border p-3 text-left text-sm ${
                      selectedCitation?.chunk_id === citation.chunk_id
                        ? "border-brand-600 bg-brand-50 text-slate-800"
                        : "border-slate-200 text-slate-700"
                    }`}
                  >
                    <p className="font-medium">{citation.document_title}</p>
                    <p>{citation.snippet}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      Relevance: {(citation.retrieval_score * 100).toFixed(0)}%
                    </p>
                    <p className="mt-1 text-xs text-slate-500">Chunk #{citation.chunk_id}</p>
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase text-slate-500">Source Preview</h3>
              <button onClick={() => setSourceDrawerOpen((prev) => !prev)} type="button" className="text-xs text-brand-700">
                {sourceDrawerOpen ? "Hide" : "Show"}
              </button>
            </div>
            {!sourceDrawerOpen ? (
              <p className="text-sm text-slate-500">Open source panel to inspect highlighted evidence.</p>
            ) : selectedCitation ? (
              <p className="mt-3 whitespace-pre-wrap text-sm text-slate-800">{renderHighlightedPreview(selectedCitation)}</p>
            ) : (
              <p className="mt-3 text-sm text-slate-500">Select a citation to preview highlighted source text.</p>
            )}
          </div>
        </section>
      )}
      {!answer && !isLoadingAnswer && (
        <section className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
          Ask a question to see grounded answers, citations, and source previews.
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h3 className="mb-3 text-sm font-semibold uppercase text-slate-500">Recent History</h3>
        <input
          value={historyFilter}
          onChange={(event) => setHistoryFilter(event.target.value)}
          placeholder="Filter history..."
          className="mb-3 w-full rounded border border-slate-300 px-2 py-1 text-sm"
        />
        <ul className="space-y-2 text-sm text-slate-700">
          {history
            .filter((item) => item.content.toLowerCase().includes(historyFilter.toLowerCase()))
            .slice(-8)
            .map((item) => (
            <li key={item.id}>
              <span className="font-semibold">{item.role}: </span>
              {item.content}
            </li>
            ))}
          {history.length === 0 && <li>No chat history yet.</li>}
        </ul>
      </section>
      </div>
    </div>
  );
}
