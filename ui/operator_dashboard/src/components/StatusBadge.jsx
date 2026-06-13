const statusConfig = {
  critical:      { color: '#DC2626', bg: '#FEF2F2', border: '#FECACA', label: 'Critical' },
  warning:       { color: '#B45309', bg: '#FFFBEB', border: '#FDE68A', label: 'Warning' },
  'in-progress': { color: '#7C3AED', bg: '#F5F3FF', border: '#DDD6FE', label: 'In Progress' },
  completed:     { color: '#16A34A', bg: '#F0FDF4', border: '#BBF7D0', label: 'Completed' },
  available:     { color: '#16A34A', bg: '#F0FDF4', border: '#BBF7D0', label: 'Available' },
  normal:        { color: '#16A34A', bg: '#F0FDF4', border: '#BBF7D0', label: 'Normal' },
  running:       { color: '#16A34A', bg: '#F0FDF4', border: '#BBF7D0', label: 'Running' },
  watch:         { color: '#D97706', bg: '#FFFBEB', border: '#FDE68A', label: 'Watch' },
  standby:       { color: '#6B7280', bg: '#F9FAFB', border: '#E5E7EB', label: 'Standby' },
  info:          { color: '#2563EB', bg: '#EFF6FF', border: '#BFDBFE', label: 'Info' },
  planned:       { color: '#64748B', bg: '#F9FAFB', border: '#E5E7EB', label: 'Planned' },
  active:        { color: '#8A4931', bg: '#F3E7E2', border: '#E7D0C6', label: 'Active' },
};

export default function StatusBadge({ status, label, size = 'sm' }) {
  const cfg = statusConfig[status] || statusConfig.standby;
  const pad = size === 'md' ? '3px 10px' : '2px 8px';
  const fontSize = size === 'md' ? '11px' : '10px';

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      padding: pad, borderRadius: 6,
      background: cfg.bg, border: `1px solid ${cfg.border}`,
      fontSize, fontWeight: 600, color: cfg.color, whiteSpace: 'nowrap',
    }}>
      <span style={{ width: 5, height: 5, borderRadius: '50%', background: cfg.color, flexShrink: 0 }} />
      {label || cfg.label}
    </span>
  );
}
