import Link from 'next/link';
import { ApprovalQueueCard } from '../../components/approval-queue-card';
import { BackendStatusCard } from '../../components/backend-status-card';
import { MatterWorkflowCard } from '../../components/matter-workflow-card';
import { demoWorkflowSteps } from '../../data/demo-data';
import { loadQueuePageState } from '../../lib/backend';

export default async function QueuePage() {
  const { backend, matter, queueItems, mode } = await loadQueuePageState();

  return (
    <main className="shell shell-narrow">
      <header className="hero hero-compact">
        <div>
          <p className="eyebrow">Matter approval queue</p>
          <h1>{matter.title}</h1>
          <p className="lede">
            Review draft outputs before any external action. Items remain pending until a human approves, rejects, or
            requests changes.
          </p>
        </div>
        <div className="hero-side-stack">
          <BackendStatusCard health={backend} />
          <Link className="button button-secondary" href="/matters">
            Back to matters
          </Link>
        </div>
      </header>

      <section className="grid two-up">
        <MatterWorkflowCard matter={matter} steps={demoWorkflowSteps} />
        <ApprovalQueueCard items={queueItems} />
      </section>

      <section className="panel panel-banner">
        <div>
          <p className="eyebrow">Queue context</p>
          <h2>{mode === 'live' ? 'Live backend queue items' : 'Synthetic queue items'}</h2>
          <p>
            {mode === 'live'
              ? 'This page is reading the approval queue directly from the FastAPI backend.'
              : 'This demo queue is synthetic and can be used even when the backend is not configured.'}
          </p>
        </div>
        <Link className="button button-secondary" href={`/matters/${matter.id}`}>
          View matter detail
        </Link>
      </section>
    </main>
  );
}
