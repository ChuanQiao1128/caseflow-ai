import Link from 'next/link';
import { ApprovalQueueCard } from '../components/approval-queue-card';
import { MatterWorkflowCard } from '../components/matter-workflow-card';
import { demoMatter, demoQueueItems, demoWorkflowSteps } from '../data/demo-data';

export default function HomePage() {
  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">CaseFlow demo shell</p>
          <h1>Workflow review for synthetic property matters</h1>
          <p className="lede">
            A compact frontend demo for bounded review of matter progress, evidence, and the human approval queue.
          </p>
        </div>
        <div className="hero-actions">
          <Link className="button button-primary" href="/queue">Open approval queue</Link>
          <span className="disclaimer">Synthetic demo data only. Not legal advice.</span>
        </div>
      </header>

      <section className="grid two-up">
        <MatterWorkflowCard matter={demoMatter} steps={demoWorkflowSteps} />
        <ApprovalQueueCard items={demoQueueItems} />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">Why this demo exists</p>
            <h2>Human-review oriented, bounded by design</h2>
          </div>
          <Link className="button button-secondary" href="/queue">View queue route</Link>
        </div>
        <ul className="bullets">
          <li>Shows the CaseFlow workflow stages from ingestion to approval.</li>
          <li>Highlights missing evidence and items needing human review.</li>
          <li>Uses synthetic data only, with no external actions or live integrations.</li>
        </ul>
      </section>
    </main>
  );
}
