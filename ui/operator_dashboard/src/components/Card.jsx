export default function Card({ children, style, ...props }) {
  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 12,
      boxShadow: 'var(--shadow)', padding: 20, color: 'var(--text-body)', ...style,
    }} {...props}>
      {children}
    </div>
  );
}
