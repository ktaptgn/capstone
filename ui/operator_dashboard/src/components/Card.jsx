export default function Card({ children, style, ...props }) {
  return (
    <div style={{
      background: '#fff', border: '1px solid #E2E8F0', borderRadius: 12,
      boxShadow: '0 1px 3px rgba(0,0,0,0.04)', padding: 20, ...style,
    }} {...props}>
      {children}
    </div>
  );
}
