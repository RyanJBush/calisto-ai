import { useEffect, useState } from "react";

import { fetchHistory, queryChat } from "../services/api";

export default function ChatPage() {
  const [query, setQuery] = useState("What is Calisto AI?");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [history, setHistory] = useState([]);

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
    await loadHistory();
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
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h3 className="text-sm font-semibold uppercase text-slate-500">Answer</h3>
          <p className="mt-2 text-slate-800">{answer}</p>
          <h4 className="mt-4 text-sm font-semibold uppercase text-slate-500">Citations</h4>
          <ul className="mt-2 space-y-2">
            {citations.map((citation) => (
              <li key={citation.chunk_id} className="rounded-md border border-slate-200 p-3 text-sm text-slate-700">
                <p className="font-medium">{citation.document_title}</p>
                <p>{citation.snippet}</p>
              </li>
            ))}
          </ul>
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
