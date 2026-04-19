import Link from 'next/link';
import { BackendStatusCard } from '../../components/backend-status-card';
import { MatterList } from '../../components/matter-list';
import { BackendHealth, loadBackendHealth, loadMatterList } from '../../lib/backend';

export default async function MattersIndexPage() {
  const [health, matters] = await Promise.all([loadBackendHealth(), loadMatterList()]);

  return (
    <main className="shell shell-detail">
      <header className="hero hero-compact">
        <div className="hero-copy">
          <p className="eyebrow">Matter index</p>
          <h1>Browse demo matters or connect live backend data</h1>
          <p className="lede">
            This page can show synthetic matters out of the box, and will switch to live FastAPI data when the backend
            base URL and demo organisation ID are configured.
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/">
              Back to overview
            </Link>
            <Link className="button button-secondary" href="/queue">
              Approval queue
            </Link>
          </div>
        </div>
        <div className="hero-side-stack">
          <BackendStatusCard health={health as BackendHealth} />
        </div>
      </header>

      <MatterList matters={matters} />
    </main>
  );
}
