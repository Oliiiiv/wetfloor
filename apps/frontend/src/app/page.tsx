import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-xl text-center space-y-6">
        <h1 className="text-5xl font-bold tracking-tight">Wetfloor</h1>
        <p className="text-neutral-600">
          A self-hosted IBKR dashboard for retail investors. Phase 0
          de-risk complete; Phase 1 in progress.
        </p>
        <div className="flex justify-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center px-5 py-2 rounded-md bg-neutral-900 text-white text-sm font-medium hover:bg-neutral-700 transition-colors"
          >
            Open dashboard
          </Link>
          <a
            href="https://github.com/oliiiiv/wetfloor"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center px-5 py-2 rounded-md border border-neutral-200 text-sm font-medium hover:bg-neutral-50 transition-colors"
          >
            GitHub
          </a>
        </div>
      </div>
    </main>
  );
}
