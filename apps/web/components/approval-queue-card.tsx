import type { ApprovalQueueItemDemo } from '../data/demo-data';

export function ApprovalQueueCard({ items, compact = false }: { items: ApprovalQueueItemDemo[]; compact?: boolean }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Approval queue</p>
          <h2>Human review items</h2>
        </div>
        <span className="pill">{items.length} items</span>
      </div>

      <div className={`queue ${compact ? 'queue-compact' : ''}`}>
        {items.map((item) => (
          <article key={item.id} className="queue-item">
            <div className="queue-item-top">
              <div>
                <strong>{item.subject}</strong>
                <p>{item.context}</p>
              </div>
              <span className={`status status-${item.status}`}>{item.status.replace('_', ' ')}</span>
            </div>
            <div className="queue-item-body">
              <span className="label">Reason</span>
              <p>{item.reason}</p>
            </div>
            <div className="queue-item-foot">
              <span className="queue-id">{item.matterId}</span>
              <span>{item.updatedAt}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
