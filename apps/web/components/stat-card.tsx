type StatCardProps = {
  label: string;
  value: string;
  hint: string;
};

export function StatCard({ label, value, hint }: StatCardProps) {
  return (
    <article className="stat-card">
      <span className="label">{label}</span>
      <strong>{value}</strong>
      <p>{hint}</p>
    </article>
  );
}
