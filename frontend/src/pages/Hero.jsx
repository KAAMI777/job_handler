import { Link } from "react-router-dom";

export default function Hero() {
  return (
    <div style={{ minHeight: "100dvh", display: "grid", placeItems: "center" }}>
      <p>
        <Link to="/graph">› enter_graph</Link>
      </p>
    </div>
  );
}
