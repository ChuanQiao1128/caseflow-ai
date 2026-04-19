import Link from 'next/link';
import { ApprovalQueueCard } from '../../../components/approval-queue-card';
import { MatterWorkflowCard } from '../../../components/matter-workflow-card';
import { StatCard } from '../../../components/stat-card';
import {
  demoChecklist,
  demoDocuments,
  demoEvidence,
  demoFields,
  demoMatter,
  demoQueueItems,
  demoReview,
  demoWorkflowSteps
} from '../../../data/demo-data';

export default function MatterDetailPage({ params }: { params: { matterId: string } }) {
  const isKnownMatter = params.matterId === demoMatter.id;

  return (
    <main className="shell shell-detail">
      <header className="hero hero-detail">
        <div className="hero-copy">
          <p className="eyebrow">Matter detail</p>
          <h1>{isKnownMatter ? demoMatter.title : 'Synthetic matter not found'}</h1>
          <p className="lede">
            {isKnownMatter
              ? 'A richer view of the review flow: extracted facts, cited evidence, checklist findings, and queued human actions.'
              : 'This demo only includes one synthetic matter. Use the navigation to jump back to the known example.'}
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/queue">
              View queue
            </Link>
            <Link className="button button-secondary" href="/">
              Back to overview
            </Link>
          </div>
        </div>

        <aside className="hero-card hero-card-accent">
          <span className="pill">{demoReview.status}</span>
          <h2>{demoReview.summary}</h2>
          <p>{demoReview.disclaimer}</p>
          <div className="hero-card-grid">
            <div>
              <span className="label">Client</span>
              <strong>{demoMatter.client}</strong>
            </div>
            <div>
              <span className="label">Last update</span>
              <strong>{demoMatter.lastUpdated}</strong>
            </div>
          </div>
        </aside>
      </header>

      <section className="metrics-grid">
        <StatCard label="Documents" value={String(demoDocuments.length)} hint="Synthetic settlement pack items" />
        <StatCard label="Extracted fields" value={String(demoFields.length)} hint="All values include citations" />
        <StatCard label="Checklist flags" value={String(demoChecklist.length)} hint="Human review required where unclear" />
        <StatCard label="Open queue items" value={String(demoQueueItems.length)} hint="Drafts awaiting approval" />
      </section>

      <section className="detail-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Evidence map</p>
              <h2>Citations that ground the review</h2>
            </div>
            <span className="pill">Scoped to this matter</span>
          </div>
          <div className="evidence-list">
            {demoEvidence.map((item) => (
              <article key={item.label} className="evidence-item">
                <div>
                  <strong>{item.label}</strong>
                  <p>{item.note}</p>
                </div>
                <span className="citation-chip">{item.citation}</span>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Extraction</p>
              <h2>Key facts and checklist findings</h2>
            </div>
          </div>
          <div className="list-stack">
            {demoFields.map((field) => (
              <div key={field.name} className="info-row">
                <div>
                  <span className="label">{field.name}</span>
                  <strong>{field.value}</strong>
                  <p>Confidence {field.confidence}</p>
                </div>
                <span className="citation-chip">{field.citation}</span>
              </div>
            ))}
          </div>
          <div className="divider" />
          <div className="list-stack">
            {demoChecklist.map((item) => (
              <div key={item.name} className="info-row info-row-tight">
                <div>
                  <span className="label">{item.name}</span>
                  <strong>{item.status}</strong>
                  <p>{item.reason}</p>
                </div>
                <span className="citation-chip">{item.citation}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid two-up">
        <MatterWorkflowCard matter={demoMatter} steps={demoWorkflowSteps} />
        <ApprovalQueueCard items={demoQueueItems} />
      </section>

      <section className="panel panel-banner">
        <div>
          <p className="eyebrow">Source documents</p>
          <h2>Demo pack items used to shape the review</h2>
          <div className="doc-grid">
            {demoDocuments.map((doc) => (
              <article key={doc.id} className="doc-card">
                <span className="pill pill-soft">{doc.tag}</span>
                <strong>{doc.name}</strong>
                <p>{doc.pages}</p>
              </article>
            ))}
          </div>
        </div>
        <Link className="button button-secondary" href="/queue">
          Inspect approval queue
        </Link>
      </section>
    </main>
  );
}
