import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";

import { fetchAdminAuditLogs, fetchWorkspaceSettings, updateWorkspaceSettings } from "../services/api";

export default function SettingsPage() {
  const { user } = useOutletContext();
  const [workspace, setWorkspace] = useState(null);
  const [workspaceName, setWorkspaceName] = useState("");
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditAction, setAuditAction] = useState("");
  const [status, setStatus] = useState("");

  async function loadWorkspace() {
    const workspacePayload = await fetchWorkspaceSettings();
    setWorkspace(workspacePayload);
    setWorkspaceName(workspacePayload.organization_name);
  }

  async function loadAuditLogs(action = "") {
    const logs = await fetchAdminAuditLogs(action ? { action } : {});
    setAuditLogs(logs.slice(0, 10));
  }

  useEffect(() => {
    if (user?.role !== "admin") return;
    loadWorkspace().catch(() => setStatus("Unable to load workspace settings."));
    loadAuditLogs().catch(() => setAuditLogs([]));
  }, [user?.role]);

  async function onSaveWorkspace(event) {
    event.preventDefault();
    try {
      const updated = await updateWorkspaceSettings({ organization_name: workspaceName });
      setWorkspace(updated);
      setStatus("Workspace updated.");
    } catch {
      setStatus("Unable to update workspace.");
    }
  }

  async function onApplyAuditFilter(event) {
    event.preventDefault();
    await loadAuditLogs(auditAction).catch(() => setAuditLogs([]));
  }

  if (user?.role !== "admin") {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Settings</h2>
        <p className="mt-2 text-sm text-slate-600">Only administrators can manage workspace and audit settings.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Workspace Settings</h2>
        <form onSubmit={onSaveWorkspace} className="mt-4 space-y-3">
          <div>
            <label className="mb-1 block text-sm text-slate-700">Organization Name</label>
            <input
              value={workspaceName}
              onChange={(event) => setWorkspaceName(event.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2"
            />
          </div>
          <div className="grid gap-2 text-xs text-slate-500 md:grid-cols-3">
            <p>Rate limit: {workspace?.rate_limit_per_minute ?? "-"}/min</p>
            <p>LLM provider: {workspace?.llm_provider ?? "-"}</p>
            <p>Model: {workspace?.llm_model ?? "-"}</p>
          </div>
          <button className="rounded-md bg-brand-600 px-4 py-2 text-sm text-white hover:bg-brand-700">Save</button>
        </form>
        {status && <p className="mt-3 text-sm text-slate-600">{status}</p>}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <h3 className="text-sm font-semibold uppercase text-slate-500">Audit Logs</h3>
        <form onSubmit={onApplyAuditFilter} className="mt-3 flex gap-2">
          <input
            value={auditAction}
            onChange={(event) => setAuditAction(event.target.value)}
            placeholder="Filter by action (e.g. chat_query)"
            className="w-full rounded border border-slate-300 px-3 py-2 text-sm"
          />
          <button className="rounded border border-slate-300 px-3 py-2 text-sm">Apply</button>
        </form>
        <ul className="mt-3 space-y-2 text-sm text-slate-700">
          {auditLogs.map((log) => (
            <li key={log.id} className="rounded border border-slate-100 p-2">
              <p className="font-medium">{log.action}</p>
              <p className="text-xs text-slate-500">
                {log.resource_type} #{log.resource_id ?? "-"} • {log.details || "No details"}
              </p>
            </li>
          ))}
          {auditLogs.length === 0 && <li className="text-slate-500">No audit events for current filter.</li>}
        </ul>
      </section>
    </div>
  );
}
