import type { ApprovalQueueItemDemo } from '../data/demo-data';

function statusLabel(status: ApprovalQueueItemDemo['status']) {
  if (status === 'pending') return '待审批';
  if (status === 'needs_changes') return '需修改';
  return '已批准';
}

export function ApprovalQueueCard({ items, compact = false }: { items: ApprovalQueueItemDemo[]; compact?: boolean }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">人工审批队列</p>
          <h2>待人工确认事项</h2>
        </div>
        <span className="pill">{items.length} 项</span>
      </div>

      <div className={`queue ${compact ? 'queue-compact' : ''}`}>
        {items.map((item) => (
          <article key={item.id} className="queue-item">
            <div className="queue-item-top">
              <div>
                <strong>{item.subject}</strong>
                <p>{item.context}</p>
              </div>
              <span className={`status status-${item.status}`}>{statusLabel(item.status)}</span>
            </div>
            <div className="queue-item-body">
              <span className="label">进入队列原因</span>
              <p>{item.reason}</p>
              {item.reviewerNotes ? (
                <p className="queue-note">
                  <span className="label">审阅备注</span>
                  {item.reviewerNotes}
                </p>
              ) : null}
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
