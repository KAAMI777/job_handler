import { useEffect, useState } from "react";
import { Analytics } from "@vercel/analytics/react";

function App() {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(
          `${import.meta.env.RENDER_API_URL}/health`
        );

        const data = await res.json();
        setStatus(data.status);
      } catch (err) {
        setStatus("Backend unreachable");
      }
    };

    checkHealth();
  }, []);

  return (
    <div>
      <h1>Job Agent</h1>
      <p>Backend status: {status}</p>
      <Analytics />
    </div>
  );
}

export default App;