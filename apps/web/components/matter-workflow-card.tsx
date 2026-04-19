import type { WorkflowStep } from '../data/demo-data';

export type MatterCardData = {
  title: string;
  organisation: string;
  type: string;
  status: string;
  settlementDate: string;
};

export function MatterWorkflowCard({ matter, steps }: { matter: MatterCardData; steps: WorkflowStep[] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">案件流程</p>
          <h2>当前进度总览</h2>
        </div>
        <span className="pill">{matter.status}</span>
      </div>

      <div className="matter-meta">
        <div>
          <span className="label">案件名称</span>
          <strong>{matter.title}</strong>
        </div>
        <div>
          <span className="label">机构</span>
          <strong>{matter.organisation}</strong>
        </div>
        <div>
          <span className="label">案件类型</span>
          <strong>{matter.type}</strong>
        </div>
        <div>
          <span className="label">交割日期</span>
          <strong>{matter.settlementDate}</strong>
        </div>
      </div>

      <div className="workflow">
        {steps.map((step, index) => (
          <div key={step.name} className={`workflow-step ${step.state}`}>
            <div className="workflow-index">{index + 1}</div>
            <div>
              <strong>{step.name}</strong>
              <p>{step.summary}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
