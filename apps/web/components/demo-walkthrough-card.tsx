import Link from 'next/link';

export function DemoWalkthroughCard() {
  return (
    <section className="panel panel-banner">
      <div>
        <p className="eyebrow">Demo ready</p>
        <h2>Prepared for simulation and walkthrough</h2>
        <p>
          The app now includes home, matter list, matter detail, approval queue, and a short runbook so you can
          present the product end-to-end without needing real client data.
        </p>
      </div>
      <div className="hero-actions">
        <Link className="button button-primary" href="/demo-runbook">
          View runbook
        </Link>
        <Link className="button button-secondary" href="/matters">
          Open matters
        </Link>
      </div>
    </section>
  );
}
