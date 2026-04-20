import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import StatsCard from "../components/StatsCard";
import { fetchAdminAnalyticsSummary } from "../services/api";

export default function DashboardPage() {
  const { user } = useOutletContext();
  const [summary, setSummary] = useState(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (user?.role !== "admin") {
      setStatus("Admin analytics are available to admin users.");
      return;
    }
    fetchAdminAnalyticsSummary()
      .then((data) => {
        setSummary(data);
        setStatus("");
      })
      .catch(() => {
        setSummary(null);
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
            <p>Ingestions Processing: {summary.ingestions_processing}</p>
            <p>Ingestions Failed: {summary.ingestions_failed}</p>
          </div>
        )}
        {status && <p className="mt-3 text-sm text-slate-500">{status}</p>}
      </div>
    </div>
  );
}
