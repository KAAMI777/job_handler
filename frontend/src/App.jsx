import { useEffect, useState } from "react";

function App() {
  const [health, setHealth] = useState({
    status: "Checking...",
    database: "Checking...",
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL}/health`);

        if (!res.ok) throw new Error("Health check failed");

        const data = await res.json();
        setHealth(data);
      } catch (err) {
        console.error(err);
        setHealth({
          status: "Backend unreachable",
          database: "Disconnected",
        });
      }
    };

    checkHealth();
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