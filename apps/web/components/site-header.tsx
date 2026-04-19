import Link from 'next/link';

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="site-brand">
        <div className="brand-mark">CF</div>
        <div>
          <p className="eyebrow">CaseFlow AI</p>
          <strong>NZ 交割材料审查 Copilot</strong>
          <p className="site-subtitle">仅做审查辅助，不替代律师判断</p>
        </div>
      </div>

      <nav className="site-nav" aria-label="Primary">
        <Link href="/">总览</Link>
        <Link href="/matters">案件列表</Link>
        <Link href="/matters/matter-001">案件工作台</Link>
        <Link href="/queue">人工审批队列</Link>
        <Link href="/demo-runbook">演示脚本</Link>
      </nav>
    </header>
  );
}
