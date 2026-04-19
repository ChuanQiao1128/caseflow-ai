import Link from 'next/link';
import { BackendStatusCard } from '../../components/backend-status-card';
import { MatterList } from '../../components/matter-list';
import { BackendHealth, loadBackendHealth, loadMatterList } from '../../lib/backend';

const triageNotes = [
  '先看状态为 needs_human_review / unclear 的案件。',
  '先处理 settlement date 临近的案件，降低延期风险。',
  '优先打开存在审批队列待办的案件。'
];

export default async function MattersIndexPage() {
  const [health, matters] = await Promise.all([loadBackendHealth(), loadMatterList()]);

  return (
    <main className="shell shell-detail">
      <header className="hero hero-compact">
        <div className="hero-copy">
          <p className="eyebrow">案件入口</p>
          <h1>先做分诊，再进入单案审查</h1>
          <p className="lede">
            列表页的核心价值是“快速决定先看哪一个”，而不是一次看完所有细节。建议在这里先完成风险排序，再进入案件工作台。
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/">
              返回总览
            </Link>
            <Link className="button button-secondary" href="/queue">
              查看审批队列
            </Link>
          </div>
        </div>
        <div className="hero-side-stack">
          <BackendStatusCard health={health as BackendHealth} />
        </div>
      </header>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">分诊建议</p>
            <h2>推荐操作顺序</h2>
          </div>
          <span className="pill">高风险优先</span>
        </div>
        <ul className="bullets bullets-compact">
          {triageNotes.map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </section>

      <MatterList matters={matters} />
    </main>
  );
}
