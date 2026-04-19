'use client';

import { useMemo, useState } from 'react';
import type { ApprovalQueueItemDemo } from '../data/demo-data';

function statusLabel(status: ApprovalQueueItemDemo['status']) {
  if (status === 'pending') return '待审批';
  if (status === 'needs_changes') return '需修改';
  return '已批准';
}

function parseMinutesFromUpdatedAt(value: string) {
  const minuteMatch = value.match(/(\d+)\s*minute/i);
  if (minuteMatch) return Number.parseInt(minuteMatch[1], 10);

  const hourMatch = value.match(/(\d+)\s*hour/i);
  if (hourMatch) return Number.parseInt(hourMatch[1], 10) * 60;

  return 0;
}

function slaLevel(updatedAt: string): 'ok' | 'warning' | 'urgent' {
  const minutes = parseMinutesFromUpdatedAt(updatedAt);
  if (minutes >= 30) return 'urgent';
  if (minutes >= 10) return 'warning';
  return 'ok';
}

function slaLabel(level: 'ok' | 'warning' | 'urgent') {
  if (level === 'urgent') return 'SLA 紧急';
  if (level === 'warning') return 'SLA 关注';
  return 'SLA 正常';
}

export function ApprovalQueueCard({ items, compact = false }: { items: ApprovalQueueItemDemo[]; compact?: boolean }) {
  const [queueItems, setQueueItems] = useState<ApprovalQueueItemDemo[]>(items);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const selectedCount = selectedIds.length;
  const allSelected = queueItems.length > 0 && selectedCount === queueItems.length;

  const summary = useMemo(() => {
    return queueItems.reduce(
      (acc, item) => {
        if (item.status === 'approved') acc.approved += 1;
        else if (item.status === 'needs_changes') acc.needsChanges += 1;
        else acc.pending += 1;
        return acc;
      },
      { pending: 0, approved: 0, needsChanges: 0 }
    );
  }, [queueItems]);

  function toggleSelected(id: string) {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((itemId) => itemId !== id) : [...prev, id]));
  }

  function toggleAll() {
    setSelectedIds((prev) => (prev.length === queueItems.length ? [] : queueItems.map((item) => item.id)));
  }

  function applyBatchStatus(status: ApprovalQueueItemDemo['status']) {
    if (selectedIds.length === 0) {
      return;
    }

    setQueueItems((prev) =>
      prev.map((item) =>
        selectedIds.includes(item.id)
          ? {
              ...item,
              status,
              reviewerNotes:
                status === 'approved' ? '批量审批通过（前端演示）' : '批量退回修改（前端演示）'
            }
          : item
      )
    );
    setSelectedIds([]);
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">人工审批队列</p>
          <h2>待人工确认事项</h2>
        </div>
        <span className="pill">{queueItems.length} 项</span>
      </div>

      <div className="queue-summary">
        <span className="pill">待审批 {summary.pending}</span>
        <span className="pill">需修改 {summary.needsChanges}</span>
        <span className="pill">已批准 {summary.approved}</span>
      </div>

      <div className="batch-toolbar">
        <label className="batch-select-all">
          <input type="checkbox" checked={allSelected} onChange={toggleAll} />
          <span>全选</span>
        </label>
        <span className="queue-selected">已选 {selectedCount} 项</span>
        <button
          type="button"
          className="button button-secondary"
          onClick={() => applyBatchStatus('approved')}
          disabled={selectedCount === 0}
        >
          批量标记已批准
        </button>
        <button
          type="button"
          className="button button-secondary"
          onClick={() => applyBatchStatus('needs_changes')}
          disabled={selectedCount === 0}
        >
          批量退回修改
        </button>
      </div>

      <p className="queue-disclaimer">说明：以上批量操作为前端演示交互，当前不会写回后端。</p>

      <div className={`queue ${compact ? 'queue-compact' : ''}`}>
        {queueItems.map((item) => {
          const level = slaLevel(item.updatedAt);
          return (
            <article key={item.id} className="queue-item">
              <div className="queue-item-top">
                <label className="queue-select">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(item.id)}
                    onChange={() => toggleSelected(item.id)}
                  />
                  <span className="sr-only">选择 {item.subject}</span>
                </label>
                <div>
                  <strong>{item.subject}</strong>
                  <p>{item.context}</p>
                </div>
                <div className="queue-top-badges">
                  <span className={`status status-${item.status}`}>{statusLabel(item.status)}</span>
                  <span className={`status status-sla-${level}`}>{slaLabel(level)}</span>
                </div>
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
          );
        })}
      </div>
    </section>
  );
}
