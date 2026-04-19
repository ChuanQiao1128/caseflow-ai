import type { BackendHealth } from '../lib/backend';

export function BackendStatusCard({ health }: { health: BackendHealth }) {
  return (
    <article className="panel backend-card">
      <div className="panel-header">
        <div>
          <p className="eyebrow">后端状态</p>
          <h2>FastAPI 连接</h2>
        </div>
        <span className={`status status-${health.status}`}>{health.label}</span>
      </div>
      <p>{health.detail}</p>
      <div className="connection-bar">
        <span className={`connection-dot connection-${health.status}`} />
        <span>{health.status === 'ok' ? '当前可读取 Live API 数据。' : '当前为 Demo 模式（合成数据）。'}</span>
      </div>
    </article>
  );
}
