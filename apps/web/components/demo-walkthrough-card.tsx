import Link from 'next/link';

export function DemoWalkthroughCard() {
  return (
    <section className="panel panel-banner">
      <div>
        <p className="eyebrow">演示准备</p>
        <h2>可按“收件-审查-审批”完成端到端讲解</h2>
        <p>
          现在包含首页、案件列表、案件工作台、审批队列和 runbook。你可以完整演示产品价值，同时保持“AI 辅助、人工决策”的边界。
        </p>
      </div>
      <div className="hero-actions">
        <Link className="button button-primary" href="/demo-runbook">
          查看演示脚本
        </Link>
        <Link className="button button-secondary" href="/matters">
          打开案件列表
        </Link>
      </div>
    </section>
  );
}
