function ChatPage() {
  return (
    <section>
      <h2 className="text-3xl font-semibold">Chat</h2>
      <p className="mt-2 text-slate-600">
        Ask grounded questions against indexed enterprise knowledge and receive citation-based
        responses.
      </p>
      <div className="mt-6 rounded-xl bg-white p-6 shadow-sm">
        <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="query">
          Ask a question
        </label>
        <textarea
          id="query"
          className="w-full rounded-lg border border-slate-300 p-3 outline-none ring-indigo-500 focus:ring"
          placeholder="What changed in our SOC 2 policy this quarter?"
          rows={4}
        />
        <button
          type="button"
          className="mt-4 rounded-lg bg-indigo-600 px-4 py-2 font-medium text-white hover:bg-indigo-500"
        >
          Submit
        </button>
      </div>
    </section>
  )
}

export default ChatPage
