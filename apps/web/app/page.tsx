import Link from 'next/link';
import { ApprovalQueueCard } from '../components/approval-queue-card';
import { DemoWalkthroughCard } from '../components/demo-walkthrough-card';
import { MatterWorkflowCard } from '../components/matter-workflow-card';
import { StatCard } from '../components/stat-card';
import { demoMatter, demoQueueItems, demoWorkflowSteps, demoMetrics } from '../data/demo-data';

const journeySteps = [
  {
    title: '1) 收件与归档',
    description: '先把合同、贷款、CDD 等材料按案件收齐，系统只在 matter 范围内处理。'
  },
  {
    title: '2) AI 预审与证据映射',
    description: '抽取关键字段、标注来源页码；证据不足时直接标记“待核对”。'
  },
  {
    title: '3) 人工审批与外部动作',
    description: '所有对外邮件、推进动作都进入审批队列，由律师最终确认。'
  }
];

const productBoundaries = [
  '不提供最终法律意见，不判断“可交割”。',
  '不自动通过 AML/CDD，不直接提交 Landonline。',
  '不自动发送外部邮件，不释放任何资金。',
  '所有关键结论都必须可追溯到文档与页码。'
];

export default function HomePage() {
  return (
    <main className="shell shell-home">
      <header className="hero hero-home">
        <div className="hero-copy">
          <p className="eyebrow">产品总览</p>
          <h1>把复杂交割材料，变成“可审查、可追溯、可交接”的工作流</h1>
          <p className="lede">
            这个前端不追求“像聊天机器人一样什么都做”，而是把用户最核心的路径做清楚：案件进入、证据抽取、风险标注、人工审批。
            这样更符合律所真实工作方式，也更容易建立信任。
          </p>

          <div className="hero-actions">
            <Link className="button button-primary" href={`/matters/${demoMatter.id}`}>
              进入案件工作台
            </Link>
            <Link className="button button-secondary" href="/queue">
              查看人工审批队列
            </Link>
          </div>
          <p className="disclaimer">仅使用合成数据演示，不包含真实客户资料。</p>
        </div>

        <aside className="hero-card hero-card-accent">
          <span className="pill">当前建议主路径</span>
          <h2>收件 → AI 预审 → 人审决策</h2>
          <p>避免在首页堆太多功能入口，优先让用户知道“下一步应该做什么”。</p>
          <div className="list-stack">
            {journeySteps.map((step) => (
              <div key={step.title} className="journey-item">
                <strong>{step.title}</strong>
                <p>{step.description}</p>
              </div>
            ))}
          </div>
        </aside>
      </header>

      <section className="metrics-grid">
        {demoMetrics.map((metric) => (
          <StatCard key={metric.label} label={metric.label} value={metric.value} hint={metric.hint} />
        ))}
      </section>

      <section className="grid two-up">
        <MatterWorkflowCard matter={demoMatter} steps={demoWorkflowSteps} />
        <ApprovalQueueCard items={demoQueueItems} />
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <p className="eyebrow">产品边界</p>
            <h2>为什么这样设计更合理</h2>
          </div>
          <span className="pill">降低误用风险</span>
        </div>
        <div className="principles-grid">
          {productBoundaries.map((boundary) => (
            <article key={boundary} className="principle-card">
              <strong>{boundary}</strong>
            </article>
          ))}
        </div>
      </section>

      <DemoWalkthroughCard />
    </main>
  );
}
