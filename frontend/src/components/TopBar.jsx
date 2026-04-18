export default function TopBar({ title, user, onLogout }) {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
      <h1 className="text-xl font-semibold text-slate-900">{title}</h1>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-600">
          {user?.full_name} ({user?.role})
        </span>
        <button
          onClick={onLogout}
          className="rounded-md bg-slate-900 px-3 py-2 text-sm text-white hover:bg-slate-700"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
