import type { MatterDemo, WorkflowStep } from '../data/demo-data';

export function MatterWorkflowCard({ matter, steps }: { matter: MatterDemo; steps: WorkflowStep[] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Workflow</p>
          <h2>Matter overview</h2>
        </div>
        <span className="pill">{matter.status}</span>
      </div>

      <div className="matter-meta">
        <div>
          <span className="label">Matter</span>
          <strong>{matter.title}</strong>
        </div>
        <div>
          <span className="label">Organisation</span>
          <strong>{matter.organisation}</strong>
        </div>
        <div>
          <span className="label">Type</span>
          <strong>{matter.type}</strong>
        </div>
        <div>
          <span className="label">Settlement</span>
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
