import type { WorkspaceAuditLog } from '../lib/backend';

export function AuditTrailList({ logs }: { logs: WorkspaceAuditLog[] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Audit trail</p>
          <h2>State changes and activity</h2>
        </div>
        <span className="pill">{logs.length} entries</span>
      </div>

      <div className="audit-list">
        {logs.map((log) => (
          <article key={log.id} className="audit-item">
            <div>
              <strong>{log.action}</strong>
              <p>{log.details}</p>
            </div>
            <div className="audit-meta">
              <span>{log.entityType}</span>
              <span>{log.createdAt}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
