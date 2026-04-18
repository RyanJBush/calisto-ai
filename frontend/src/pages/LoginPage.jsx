import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../services/api";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@calisto.ai");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");

  async function onSubmit(event) {
    event.preventDefault();
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch {
      setError("Login failed. Verify credentials.");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <form onSubmit={onSubmit} className="w-full max-w-md rounded-lg bg-white p-6 shadow">
        <h1 className="mb-2 text-2xl font-semibold text-slate-900">Calisto AI</h1>
        <p className="mb-6 text-sm text-slate-600">Sign in to access your enterprise knowledge workspace.</p>

        <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
        <input
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="mb-4 w-full rounded-md border border-slate-300 px-3 py-2"
        />

        <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="mb-4 w-full rounded-md border border-slate-300 px-3 py-2"
        />

        {error && <p className="mb-3 text-sm text-red-600">{error}</p>}

        <button type="submit" className="w-full rounded-md bg-brand-600 px-4 py-2 text-white hover:bg-brand-700">
          Sign In
        </button>
      </form>
    </div>
  );
}
