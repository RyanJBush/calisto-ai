import { Outlet, useLocation, useNavigate } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import TopBar from "../components/TopBar";
import { clearToken } from "../services/api";

export default function AppLayout({ user }) {
  const location = useLocation();
  const navigate = useNavigate();

  function handleLogout() {
    clearToken();
    navigate("/login");
  }

  const title = location.pathname.replace("/", "") || "dashboard";

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <TopBar title={title[0].toUpperCase() + title.slice(1)} user={user} onLogout={handleLogout} />
        <main className="p-6">
          <Outlet context={{ user }} />
        </main>
      </div>
    </div>
  );
}
