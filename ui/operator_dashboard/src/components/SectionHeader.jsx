export default function SectionHeader({ title, action }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
      <h3 style={{ fontSize: 14, fontWeight: 700, color: '#1E293B', margin: 0 }}>{title}</h3>
      {action && <span style={{ fontSize: 12, color: '#8A4931', cursor: 'pointer' }}>{action}</span>}
    </div>
  );
}
