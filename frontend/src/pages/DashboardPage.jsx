function DashboardPage() {
  return (
    <section>
      <h2 className="text-3xl font-semibold">Dashboard</h2>
      <p className="mt-2 text-slate-600">
        Welcome to Calisto AI. This workspace will surface tenant-level ingestion, search, and usage
        analytics.
      </p>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {[
          ['Documents', '0 indexed'],
          ['Queries today', '0'],
          ['Citation coverage', 'N/A'],
        ].map(([label, value]) => (
          <article key={label} className="rounded-xl bg-white p-5 shadow-sm">
            <h3 className="text-sm font-medium text-slate-500">{label}</h3>
            <p className="mt-2 text-2xl font-semibold">{value}</p>
          </article>
        ))}
      </div>
    </section>
  )
}

export default DashboardPage
