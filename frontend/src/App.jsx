import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(
          `${import.meta.env.VITE_RENDER_API_URL}/health`
        ); const data = await res.json();
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
    </div>
  );
}

export default App;