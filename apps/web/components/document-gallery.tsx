import type { WorkspaceDocument } from '../lib/backend';

export function DocumentGallery({ documents }: { documents: WorkspaceDocument[] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Source documents</p>
          <h2>Docs in the matter pack</h2>
        </div>
        <span className="pill">{documents.length} docs</span>
      </div>

      <div className="doc-grid">
        {documents.map((doc) => (
          <article key={doc.id} className="doc-card">
            <span className="pill pill-soft">{doc.tag}</span>
            <strong>{doc.name}</strong>
            <p>{doc.pages}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
