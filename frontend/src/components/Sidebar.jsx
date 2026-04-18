import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/documents", label: "Documents" },
  { to: "/chat", label: "Chat" },
  { to: "/settings", label: "Settings" }
];

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-slate-200 bg-white p-4">
      <div className="mb-8">
        <p className="text-lg font-semibold text-slate-900">Calisto AI</p>
        <p className="text-xs text-slate-500">Enterprise Knowledge</p>
      </div>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block rounded-md px-3 py-2 text-sm ${
                isActive ? "bg-brand-600 text-white" : "text-slate-700 hover:bg-slate-100"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
