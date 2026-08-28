import { useEffect, useState } from "react";

import { apiFetch } from "./lib/api";

function App() {
  const [health, setHealth] = useState({
    status: "Checking...",
    database: "Checking...",
  });

  useEffect(() => {
    apiFetch("/health")
      .then(setHealth)
      .catch((err) => {
        console.error(err);
        setHealth({ status: "Backend unreachable", database: "Disconnected" });
      });
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Job Agent</h1>

      <p><strong>API:</strong> {health.status}</p>
      <p><strong>Database:</strong> {health.database}</p>
    </div>
  );
}

export default App;
