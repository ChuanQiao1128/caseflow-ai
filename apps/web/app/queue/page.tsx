import Link from 'next/link';
import { ApprovalQueueCard } from '../../components/approval-queue-card';
import { BackendStatusCard } from '../../components/backend-status-card';
import { MatterWorkflowCard } from '../../components/matter-workflow-card';
import { demoWorkflowSteps } from '../../data/demo-data';
import { loadQueuePageState } from '../../lib/backend';

const queueRules = [
  '仅处理“可执行动作”，例如外联邮件草稿。',
  '每个条目都要说明进入队列的原因与证据。',
  '审批通过前，不触发任何外部系统动作。'
];

export default async function QueuePage() {
  const { backend, matter, queueItems, mode } = await loadQueuePageState();

  return (
    <main className="shell shell-narrow">
      <header className="hero hero-compact">
        <div>
          <p className="eyebrow">人工审批队列</p>
          <h1>{matter.title}</h1>
          <p className="lede">
            队列页是“最后一道安全阀”：AI 只给出建议草稿，是否执行由人工审批决定。
          </p>
        </div>
        <div className="hero-side-stack">
          <BackendStatusCard health={backend} />
          <Link className="button button-secondary" href="/matters">
            返回案件列表
          </Link>
        </div>
      </header>

      <section className="grid two-up">
        <MatterWorkflowCard matter={matter} steps={demoWorkflowSteps} />
        <ApprovalQueueCard items={queueItems} />
      </section>

      <section className="panel panel-banner">
        <div>
          <p className="eyebrow">审批规则</p>
          <h2>{mode === 'live' ? '当前为 Live Backend 队列' : '当前为 Synthetic Demo 队列'}</h2>
          <ul className="bullets bullets-compact">
            {queueRules.map((rule) => (
              <li key={rule}>{rule}</li>
            ))}
          </ul>
        </div>
        <Link className="button button-secondary" href={`/matters/${matter.id}`}>
          回到案件工作台
        </Link>
      </section>
    </main>
  );
}
