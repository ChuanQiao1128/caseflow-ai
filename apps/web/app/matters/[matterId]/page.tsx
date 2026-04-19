import Link from 'next/link';
import { ApprovalQueueCard } from '../../../components/approval-queue-card';
import { AuditTrailList } from '../../../components/audit-trail-list';
import { DocumentGallery } from '../../../components/document-gallery';
import { MatterWorkflowCard } from '../../../components/matter-workflow-card';
import { StatCard } from '../../../components/stat-card';
import { demoMatter, demoWorkflowSteps } from '../../../data/demo-data';
import { loadMatterWorkspace } from '../../../lib/backend';

export default async function MatterDetailPage({ params }: { params: { matterId: string } }) {
  const workspace = await loadMatterWorkspace(params.matterId);

  if (!workspace) {
    return (
      <main className="shell shell-detail">
        <header className="hero hero-compact">
          <div className="hero-copy">
            <p className="eyebrow">Matter detail</p>
            <h1>Matter not found</h1>
            <p className="lede">
              The demo only recognises one synthetic matter by default. Use the matter index to choose an available
              live or demo matter.
            </p>
          </div>
          <Link className="button button-secondary" href="/matters">
            Back to matters
          </Link>
        </header>
      </main>
    );
  }

  const { backend, matter, documents, queueItems, auditLogs, analysis, mode } = workspace;

  return (
    <main className="shell shell-detail">
      <header className="hero hero-detail">
        <div className="hero-copy">
          <p className="eyebrow">Matter detail</p>
          <h1>{matter.title}</h1>
          <p className="lede">
            {mode === 'live'
              ? 'Live backend data is connected for matter metadata, documents, queue items, and audit history. The analysis cards remain synthetic until read endpoints are added.'
              : 'A richer view of the review flow: extracted facts, cited evidence, checklist findings, and queued human actions.'}
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/queue">
              View queue
            </Link>
            <Link className="button button-secondary" href="/matters">
              Back to matters
            </Link>
          </div>
        </div>

        <aside className="hero-card hero-card-accent">
          <span className="pill">{backend.label}</span>
          <h2>{matter.status}</h2>
          <p>{backend.detail}</p>
          <div className="hero-card-grid">
            <div>
              <span className="label">Client</span>
              <strong>{matter.client}</strong>
            </div>
            <div>
              <span className="label">Last update</span>
              <strong>{matter.lastUpdated}</strong>
            </div>
          </div>
        </aside>
      </header>

      <section className="metrics-grid">
        <StatCard label="Documents" value={String(documents.length)} hint="Matter pack content on screen" />
        <StatCard label="Queue items" value={String(queueItems.length)} hint="Human approval actions waiting" />
        <StatCard label="Audit entries" value={String(auditLogs.length)} hint="Every state change stays traceable" />
        <StatCard label="Mode" value={mode === 'live' ? 'Live backend' : 'Demo synthetic'} hint="Backend-aware rendering" />
      </section>

      <section className="detail-grid">
        <DocumentGallery documents={documents} />
        <AuditTrailList logs={auditLogs} />
      </section>

      <section className="panel panel-banner">
        <div>
          <p className="eyebrow">Synthetic analysis snapshot</p>
          <h2>Citations that ground the review</h2>
          <ul className="bullets bullets-compact">
            <li>
              {mode === 'live'
                ? 'This analysis preview is synthetic and acts as a placeholder for the future read-only extraction APIs.'
                : 'The matter review is bounded, citation-aware, and intended for human review only.'}
            </li>
            <li>Evidence map, checklist findings, and follow-up draft flows remain visible in the demo.</li>
          </ul>
        </div>
        <Link className="button button-secondary" href="/queue">
          Inspect approval queue
        </Link>
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
            {analysis.evidence.map((item) => (
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
            {analysis.fields.map((field) => (
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
            {analysis.checklist.map((item) => (
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
        <MatterWorkflowCard matter={matter} steps={demoWorkflowSteps} />
        <ApprovalQueueCard items={queueItems} />
      </section>
    </main>
  );
}
