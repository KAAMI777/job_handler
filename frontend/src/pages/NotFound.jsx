import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div style={{ minHeight: "100dvh", display: "grid", placeItems: "center", padding: "2rem" }}>
      <pre style={{ color: "var(--text-secondary)", textAlign: "center", lineHeight: 1.7 }}>
        <span style={{ color: "var(--danger)" }}>404</span> — no such route
        {"\n\n"}
        <Link to="/">› return home</Link>
      </pre>
    </div>
  );
}
