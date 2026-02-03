import { useEffect, useState } from "react";

import { apiGet } from "../api/client";

type Run = {
  id: string;
  status: string;
  created_at?: string | null;
};

export default function RunsPage() {
  const [items, setItems] = useState<Run[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Run[]>("/runs")
      .then(setItems)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="card">
      <h2>Runs</h2>
      {error && <p>Failed to load runs: {error}</p>}
      {!error && items.length === 0 && <p>No runs yet.</p>}
      {items.length > 0 && (
        <ul className="list">
          {items.map((run) => (
            <li key={run.id}>
              <strong>{run.status}</strong> · {run.id}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
