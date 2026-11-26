export function EvidenceStatusPill({ status }: { status: 'green' | 'yellow' | 'red' }) {
  const color = status === 'green' ? 'bg-green-100 text-green-800' : status === 'red' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-900';
  return <span className={`evidence-status-pill ${color}`}>{status}</span>;
}
