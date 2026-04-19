import Link from 'next/link';
import { demoMatter } from '../../../data/demo-data';
import { loadMatterWorkspace } from '../../../lib/backend';

function statusLabel(value: string) {
  const normalized = value.toLowerCase();
  if (normalized.includes('needs human review')) return '需人工复核';
  if (normalized.includes('approved')) return '已批准';
  if (normalized.includes('rejected')) return '已拒绝';
  if (normalized.includes('draft')) return '草稿';
  if (normalized.includes('pass')) return '通过';
  if (normalized.includes('unclear')) return '待核对';
  return value;
}

export default async function MatterDetailPage({ params }: { params: { matterId: string } }) {
  const workspace = await loadMatterWorkspace(params.matterId);

  if (!workspace) {
    return (
      <main className="shell shell-detail">
        <header className="hero hero-compact">
          <div className="hero-copy">
            <p className="eyebrow">案件详情</p>
            <h1>没有找到这个案件</h1>
            <p className="lede">请先回到案件列表，选择一个可用的 demo 或 live matter。</p>
          </div>
          <Link className="button button-secondary" href="/matters">
            返回案件列表
          </Link>
        </header>
      </main>
    );
  }

  const { backend, matter, documents, queueItems, auditLogs, analysis, mode } = workspace;
  const isLive = mode === 'live';

  return (
    <main className="shell shell-detail">
      <header className="hero hero-detail">
        <div className="hero-copy">
          <p className="eyebrow">案件详情</p>
          <h1>{matter.title}</h1>
          <p className="lede">
            这是一个给律所内部看的审查工作台：先上传文件，再自动检查缺失、冲突、过期和不匹配，最后交给人工确认。
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" href="/queue">
              查看审批队列
            </Link>
            <Link className="button button-secondary" href="/matters">
              返回案件列表
            </Link>
          </div>
        </div>

        <aside className="hero-card hero-card-accent">
          <span className="pill">{backend.label}</span>
          <h2>{statusLabel(matter.status)}</h2>
          <p>{backend.detail}</p>
          <div className="hero-card-grid">
            <div>
              <span className="label">客户</span>
              <strong>{matter.client}</strong>
            </div>
            <div>
              <span className="label">最近更新</span>
              <strong>{matter.lastUpdated}</strong>
            </div>
          </div>
        </aside>
      </header>

      <section className="metrics-grid">
        <article className="panel stat-panel">
          <span className="label">案件类型</span>
          <strong>{matter.type}</strong>
          <p>用于决定需要检查哪些文件和字段。</p>
        </article>
        <article className="panel stat-panel">
          <span className="label">文件数量</span>
          <strong>{String(documents.length)}</strong>
          <p>上传后会自动分类并进入审查流程。</p>
        </article>
        <article className="panel stat-panel">
          <span className="label">待审项目</span>
          <strong>{String(queueItems.length)}</strong>
          <p>这些内容都需要人工确认后才能继续。</p>
        </article>
        <article className="panel stat-panel">
          <span className="label">模式</span>
          <strong>{isLive ? 'Live backend' : 'Demo synthetic'}</strong>
          <p>{isLive ? '连接真实后端数据' : '使用演示数据，方便展示'}</p>
        </article>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">第一步：上传与收件箱</p>
              <h2>这个案件里有什么文件？</h2>
            </div>
            <span className="pill">{documents.length} 份文件</span>
          </div>
          <p className="lede" style={{ marginTop: 0 }}>
            演示时你可以说：用户先把合同、贷款、合规文件上传进来，系统先知道“有哪些材料”，再开始审查。
          </p>
          <div className="doc-grid">
            {documents.map((doc) => (
              <article key={doc.id} className="doc-card">
                <span className="pill pill-soft">{doc.tag}</span>
                <strong>{doc.name}</strong>
                <p>{doc.pages}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">第二步：自动检查</p>
              <h2>系统先帮你找问题</h2>
            </div>
            <span className="pill">证据留痕</span>
          </div>
          <div className="list-stack">
            {analysis.fields.map((field) => (
              <div key={field.name} className="info-row">
                <div>
                  <span className="label">{field.name}</span>
                  <strong>{field.value}</strong>
                  <p>置信度 {field.confidence}</p>
                </div>
                <span className="citation-chip">{field.citation}</span>
              </div>
            ))}
          </div>
          <div className="divider" />
          <div className="list-stack">
            {analysis.checklist.map((item) => (
              <div key={item.name} className="info-row info-row-tight">
                <div>
                  <span className="label">{item.name}</span>
                  <strong>{statusLabel(item.status)}</strong>
                  <p>{item.reason}</p>
                </div>
                <span className="citation-chip">{item.citation}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">第三步：证据与冲突</p>
              <h2>哪些信息是匹配的？哪些需要人工看？</h2>
            </div>
            <span className="pill">仅作审查辅助</span>
          </div>
          <div className="evidence-list">
            {analysis.evidence.map((item) => (
              <article key={item.label} className="evidence-item">
                <div>
                  <strong>{item.label}</strong>
                  <p>{item.note}</p>
                </div>
                <span className="citation-chip">{item.citation}</span>
              </article>
            ))}
          </div>
          <div className="divider" />
          <div className="list-stack">
            <div className="info-row info-row-tight">
              <div>
                <span className="label">给客户解释的一句话</span>
                <strong>文件已分类，关键信息已抽取，问题已标出。</strong>
                <p>如果证据不足，系统会显示待核对，而不是硬下结论。</p>
              </div>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">第四步：人工审批</p>
              <h2>接下来要做什么？</h2>
            </div>
            <span className="pill">{queueItems.length} 个待办</span>
          </div>
          <div className="queue queue-compact">
            {queueItems.map((item) => (
              <article key={item.id} className="queue-item">
                <div className="queue-item-top">
                  <div>
                    <strong>{item.subject}</strong>
                    <p>{item.context}</p>
                  </div>
                  <span className={`status status-${item.status}`}>{statusLabel(item.status)}</span>
                </div>
                <div className="queue-item-body">
                  <span className="label">为什么放进队列</span>
                  <p>{item.reason}</p>
                  {item.reviewerNotes ? (
                    <p className="queue-note">
                      <span className="label">审阅备注</span>
                      {item.reviewerNotes}
                    </p>
                  ) : null}
                </div>
                <div className="queue-item-foot">
                  <span className="queue-id">{item.matterId}</span>
                  <span>{item.updatedAt}</span>
                </div>
              </article>
            ))}
          </div>
          <div className="divider" />
          <div className="audit-list">
            {auditLogs.slice(0, 2).map((log) => (
              <article key={log.id} className="audit-item">
                <div>
                  <strong>{log.action}</strong>
                  <p>{log.details}</p>
                </div>
                <div className="audit-meta">
                  <span>{log.entityType}</span>
                  <span>{log.createdAt}</span>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="panel panel-banner">
        <div>
          <p className="eyebrow">演示总结</p>
          <h2>一句话讲清这个页面</h2>
          <ul className="bullets bullets-compact">
            <li>先上传案件文件。</li>
            <li>系统自动抽取信息并检查是否缺失、过期、冲突或不匹配。</li>
            <li>所有可疑项进入人工审批队列，最终由人决定下一步。</li>
          </ul>
        </div>
        <Link className="button button-secondary" href="/demo-runbook">
          看演示脚本
        </Link>
      </section>
    </main>
  );
}
