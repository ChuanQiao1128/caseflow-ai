import type { BackendHealth } from '../lib/backend';

export function BackendStatusCard({ health }: { health: BackendHealth }) {
  return (
    <article className="panel backend-card">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Backend status</p>
          <h2>FastAPI connection</h2>
        </div>
        <span className={`status status-${health.status}`}>{health.label}</span>
      </div>
      <p>{health.detail}</p>
      <div className="connection-bar">
        <span className={`connection-dot connection-${health.status}`} />
        <span>
          {health.status === 'ok'
            ? 'Live API mode is available for real data inspection.'
            : 'The UI is running in demo mode with synthetic data.'}
        </span>
      </div>
    </article>
  );
}
