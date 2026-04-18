import StatsCard from "../components/StatsCard";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <StatsCard label="Documents Indexed" value="12" />
        <StatsCard label="Chat Sessions" value="34" />
        <StatsCard label="Citation Coverage" value="98%" />
      </div>
      <div className="rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-900">Platform Overview</h2>
        <p className="mt-2 text-sm text-slate-600">
          Calisto AI centralizes enterprise knowledge and generates grounded answers with source citations.
        </p>
      </div>
    </div>
  );
}
