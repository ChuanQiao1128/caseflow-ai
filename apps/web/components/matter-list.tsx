import Link from 'next/link';
import type { BackendMatter } from '../lib/backend';

function statusLabel(status: string) {
  const normalized = status.toLowerCase();
  if (normalized.includes('needs human review') || normalized.includes('needs_human_review')) return '需人工复核';
  if (normalized.includes('unclear')) return '待核对';
  if (normalized.includes('approved')) return '已批准';
  if (normalized.includes('draft')) return '草稿';
  return status;
}

export function MatterList({ matters }: { matters: BackendMatter[] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">案件清单</p>
          <h2>可进入的案件</h2>
        </div>
        <span className="pill">{matters.length} 个案件</span>
      </div>

      <div className="matter-list">
        {matters.map((matter) => (
          <Link key={matter.id} href={`/matters/${matter.id}`} className="matter-list-item">
            <div>
              <span className="label">{matter.reference ?? '无参考号'}</span>
              <strong>{matter.title}</strong>
              <p>{statusLabel(matter.status)}</p>
            </div>
            <span className="matter-chevron">→</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
