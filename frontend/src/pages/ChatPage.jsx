import { useEffect, useState } from "react";

import { fetchHistory, queryChat } from "../services/api";

export default function ChatPage() {
  const [query, setQuery] = useState("What is Calisto AI?");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [history, setHistory] = useState([]);
  const [confidenceScore, setConfidenceScore] = useState(null);
  const [citationCoverage, setCitationCoverage] = useState(null);
  const [insufficientEvidence, setInsufficientEvidence] = useState(false);
  const [rewrittenQuery, setRewrittenQuery] = useState("");

  async function loadHistory() {
    const data = await fetchHistory();
    setHistory(data);
  }

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
  }, []);

  async function onAsk(event) {
    event.preventDefault();
    const response = await queryChat({ query });
    setAnswer(response.answer);
    setCitations(response.citations);
    setSelectedCitation(response.citations[0] || null);
    setConfidenceScore(response.confidence_score);
    setCitationCoverage(response.citation_coverage);
    setInsufficientEvidence(response.insufficient_evidence);
    setRewrittenQuery(response.rewritten_query);
    await loadHistory();
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
    <div className="space-y-6">
      <form onSubmit={onAsk} className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Citation-Aware Chat</h2>
        <textarea
          rows={3}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="mb-3 w-full rounded-md border border-slate-300 px-3 py-2"
        />
        <button className="rounded-md bg-brand-600 px-4 py-2 text-white hover:bg-brand-700">Ask</button>
      </form>

      {answer && (
        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <h3 className="text-sm font-semibold uppercase text-slate-500">Answer</h3>
            <p className="mt-2 text-slate-800">{answer}</p>
            <div className="mt-3 space-y-1 text-xs text-slate-500">
              <p>Rewritten Query: {rewrittenQuery}</p>
              <p>Confidence: {((confidenceScore || 0) * 100).toFixed(0)}%</p>
              <p>Citation Coverage: {((citationCoverage || 0) * 100).toFixed(0)}%</p>
              {insufficientEvidence && <p className="font-medium text-amber-600">Insufficient evidence fallback active.</p>}
            </div>
            <h4 className="mt-4 text-sm font-semibold uppercase text-slate-500">Citations</h4>
            <ul className="mt-2 space-y-2">
              {citations.map((citation) => (
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
                  </button>
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <h3 className="text-sm font-semibold uppercase text-slate-500">Source Preview</h3>
            {selectedCitation ? (
              <p className="mt-3 whitespace-pre-wrap text-sm text-slate-800">{renderHighlightedPreview(selectedCitation)}</p>
            ) : (
              <p className="mt-3 text-sm text-slate-500">Select a citation to preview highlighted source text.</p>
            )}
          </div>
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h3 className="mb-3 text-sm font-semibold uppercase text-slate-500">Recent History</h3>
        <ul className="space-y-2 text-sm text-slate-700">
          {history.slice(-8).map((item) => (
            <li key={item.id}>
              <span className="font-semibold">{item.role}: </span>
              {item.content}
            </li>
          ))}
          {history.length === 0 && <li>No chat history yet.</li>}
        </ul>
      </section>
    </div>
  );
}
