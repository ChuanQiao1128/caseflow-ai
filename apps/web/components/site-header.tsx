import Link from 'next/link';

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="site-brand">
        <div className="brand-mark">CF</div>
        <div>
          <p className="eyebrow">CaseFlow AI</p>
          <strong>NZ Property Settlement Review Copilot</strong>
        </div>
      </div>

      <nav className="site-nav" aria-label="Primary">
        <Link href="/">Overview</Link>
        <Link href="/matters">Matters</Link>
        <Link href="/matters/matter-001">Matter detail</Link>
        <Link href="/queue">Approval queue</Link>
        <Link href="/demo-runbook">Runbook</Link>
      </nav>
    </header>
  );
}
