import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import StatsCard from "../components/StatsCard";
import {
  fetchAdminAnalyticsSummary,
  fetchAdminIngestionBreakdown,
  fetchAdminTopDocuments
} from "../services/api";

export default function DashboardPage() {
  const { user } = useOutletContext();
  const [summary, setSummary] = useState(null);
  const [topDocuments, setTopDocuments] = useState([]);
  const [ingestionBreakdown, setIngestionBreakdown] = useState([]);
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (user?.role !== "admin") {
      setStatus("Admin analytics are available to admin users.");
      return;
    }
    Promise.all([
      fetchAdminAnalyticsSummary(),
      fetchAdminTopDocuments(),
      fetchAdminIngestionBreakdown()
    ])
      .then(([summaryData, topDocumentsData, ingestionData]) => {
        setSummary(summaryData);
        setTopDocuments(topDocumentsData);
        setIngestionBreakdown(ingestionData);
        setStatus("");
      })
      .catch(() => {
        setSummary(null);
        setTopDocuments([]);
        setIngestionBreakdown([]);
        setStatus("Unable to load admin analytics.");
      });
  }, [user?.role]);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatsCard label="Documents Indexed" value={summary?.documents_total ?? "-"} />
        <StatsCard label="Chat Sessions" value={summary?.chat_sessions_total ?? "-"} />
        <StatsCard label="Queries" value={summary?.queries_total ?? "-"} />
      </div>
      <div className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Platform Overview</h2>
        <p className="mt-2 text-sm text-slate-600">
          Calisto AI centralizes enterprise knowledge and generates grounded answers with source citations.
        </p>
        {summary && (
          <div className="mt-4 grid gap-3 text-sm text-slate-700 md:grid-cols-2">
            <p>Chunks Indexed: {summary.chunks_total}</p>
            <p>Ingestions Completed: {summary.ingestions_completed}</p>
            <p>Ingestions Queued: {summary.ingestions_queued}</p>
            <p>Ingestions Processing: {summary.ingestions_processing}</p>
            <p>Ingestions Failed: {summary.ingestions_failed}</p>
          </div>
        )}
        {status && <p className="mt-3 text-sm text-slate-500">{status}</p>}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h3 className="text-sm font-semibold uppercase text-slate-500">Top Indexed Documents</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            {topDocuments.map((doc) => (
              <li key={doc.document_id} className="flex items-center justify-between rounded border border-slate-100 p-2">
                <span>{doc.title}</span>
                <span className="text-slate-500">{doc.indexed_chunks} chunks</span>
              </li>
            ))}
            {topDocuments.length === 0 && <li className="text-slate-500">No indexed documents yet.</li>}
          </ul>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h3 className="text-sm font-semibold uppercase text-slate-500">Ingestion Breakdown</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            {ingestionBreakdown.map((item) => (
              <li key={item.status} className="flex items-center justify-between rounded border border-slate-100 p-2">
                <span className="capitalize">{item.status}</span>
                <span className="text-slate-500">{item.count}</span>
              </li>
            ))}
            {ingestionBreakdown.length === 0 && <li className="text-slate-500">No ingestion runs yet.</li>}
          </ul>
        </section>
      </div>
    </div>
  );
}
