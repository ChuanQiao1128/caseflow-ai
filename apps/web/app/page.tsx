import Link from 'next/link';
import { ApprovalQueueCard } from '../components/approval-queue-card';
import { MatterWorkflowCard } from '../components/matter-workflow-card';
import { StatCard } from '../components/stat-card';
import { demoMatter, demoQueueItems, demoWorkflowSteps, demoMetrics } from '../data/demo-data';

export default function HomePage() {
  return (
    <main className="shell shell-home">
      <header className="hero hero-home">
        <div className="hero-copy">
          <p className="eyebrow">CaseFlow demo shell</p>
          <h1>Elegant, bounded review for synthetic property matters</h1>
          <p className="lede">
            A polished demo UI for settlement review, evidence citations, and the human approval queue — built to
            show the workflow without crossing the line into legal advice.
          </p>

          <div className="hero-actions">
            <Link className="button button-primary" href={`/matters/${demoMatter.id}`}>
              Open matter detail
            </Link>
            <Link className="button button-secondary" href="/queue">
              Open approval queue
            </Link>
          </div>
        </div>

        <aside className="hero-card">
          <span className="pill">{demoMatter.status}</span>
          <h2>{demoMatter.title}</h2>
          <p>{demoMatter.organisation}</p>
          <div className="hero-card-grid">
            <div>
              <span className="label">Matter type</span>
              <strong>{demoMatter.type}</strong>
            </div>
            <div>
              <span className="label">Settlement</span>
              <strong>{demoMatter.settlementDate}</strong>
            </div>
          </div>
        </aside>
      </header>

      <section className="metrics-grid">
        {demoMetrics.map((metric) => (
          <StatCard key={metric.label} label={metric.label} value={metric.value} hint={metric.hint} />
        ))}
      </section>

      <section className="grid two-up">
        <MatterWorkflowCard matter={demoMatter} steps={demoWorkflowSteps} />
        <ApprovalQueueCard items={demoQueueItems} />
      </section>

      <section className="panel panel-banner">
        <div>
          <p className="eyebrow">What the demo shows</p>
          <h2>From citations to queue items, everything stays human-review oriented</h2>
          <ul className="bullets bullets-compact">
            <li>Workflow stages are visualised from ingestion to approval.</li>
            <li>Queue items are framed as draft follow-up work, not external actions.</li>
            <li>Every output is synthetic, scoped, and labelled for manual checking.</li>
          </ul>
        </div>
        <Link className="button button-secondary" href={`/matters/${demoMatter.id}`}>
          See full matter view
        </Link>
      </section>
    </main>
  );
}
