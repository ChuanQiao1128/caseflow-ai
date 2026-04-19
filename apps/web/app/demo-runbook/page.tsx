import Link from 'next/link';

const steps = [
  {
    title: '1. Start the backend',
    body: 'Run the FastAPI app on localhost:8000 so the frontend can connect to live endpoints if desired.'
  },
  {
    title: '2. Start the frontend',
    body: 'Run the Next.js app on localhost:3000. Without backend env vars, it will fall back to synthetic demo data.'
  },
  {
    title: '3. Demo the workflow',
    body: 'Open Home, Matters, Matter Detail, and Approval Queue to show scoped review, evidence, audit logs, and queue items.'
  },
  {
    title: '4. Explain the boundaries',
    body: 'Emphasize that outputs are bounded, citation-aware, and human-review only — not legal advice or automated approval.'
  }
];

export default function DemoRunbookPage() {
  return (
    <main className="shell shell-detail">
      <header className="hero hero-compact">
        <div className="hero-copy">
          <p className="eyebrow">Demo runbook</p>
          <h1>How to show the product safely</h1>
          <p className="lede">
            This page is a lightweight demo script so the workflow is repeatable during a live walkthrough.
          </p>
        </div>
        <div className="hero-side-stack">
          <Link className="button button-primary" href="/">
            Back to overview
          </Link>
          <Link className="button button-secondary" href="/matters">
            Open matter browser
          </Link>
        </div>
      </header>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Suggested flow</p>
            <h2>Short script for a demo or simulation</h2>
          </div>
        </div>
        <div className="list-stack">
          {steps.map((step) => (
            <article key={step.title} className="info-row">
              <div>
                <span className="label">{step.title}</span>
                <p>{step.body}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
