import { Link } from 'react-router-dom'

function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <section className="w-full max-w-md rounded-2xl bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Sign in to Calisto AI</h1>
        <p className="mt-2 text-sm text-slate-500">Enterprise knowledge platform</p>
        <form className="mt-6 space-y-4">
          <label className="block">
            <span className="mb-1 block text-sm font-medium">Email</span>
            <input
              type="email"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none ring-indigo-500 focus:ring"
              placeholder="you@company.com"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-sm font-medium">Password</span>
            <input
              type="password"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none ring-indigo-500 focus:ring"
              placeholder="••••••••"
            />
          </label>
          <button
            type="button"
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-500"
          >
            Sign in
          </button>
        </form>
        <Link to="/" className="mt-4 inline-block text-sm text-indigo-600 hover:text-indigo-500">
          Continue to demo shell
        </Link>
      </section>
    </main>
  )
}

export default LoginPage
