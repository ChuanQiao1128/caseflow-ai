import Link from 'next/link';
import { ApprovalQueueCard } from '../../components/approval-queue-card';
import { demoMatter, demoQueueItems } from '../../data/demo-data';

export default function QueuePage() {
  return (
    <main className="shell">
      <header className="hero hero-compact">
        <div>
          <p className="eyebrow">Matter approval queue</p>
          <h1>{demoMatter.title}</h1>
          <p className="lede">
            Review draft outputs before any external action. Items remain pending until a human approves, rejects,
            or requests changes.
          </p>
        </div>
        <Link className="button button-secondary" href="/">Back to workflow</Link>
      </header>

      <ApprovalQueueCard items={demoQueueItems} compact />
    </main>
  );
}
