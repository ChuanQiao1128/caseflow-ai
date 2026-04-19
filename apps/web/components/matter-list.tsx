import Link from 'next/link';
import type { BackendMatter } from '../lib/backend';

export function MatterList({ matters }: { matters: BackendMatter[] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Matters</p>
          <h2>Available matters</h2>
        </div>
        <span className="pill">{matters.length} items</span>
      </div>

      <div className="matter-list">
        {matters.map((matter) => (
          <Link key={matter.id} href={`/matters/${matter.id}`} className="matter-list-item">
            <div>
              <span className="label">{matter.reference ?? 'No reference'}</span>
              <strong>{matter.title}</strong>
              <p>{matter.status}</p>
            </div>
            <span className="matter-chevron">→</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
