import { useEffect, useState } from "react";

import { apiGet } from "../api/client";

type Dataset = {
  id: string;
  name: string;
  status: string;
  row_count?: number | null;
};

export default function DatasetsPage() {
  const [items, setItems] = useState<Dataset[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Dataset[]>("/datasets")
      .then(setItems)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="card">
      <h2>Datasets</h2>
      {error && <p>Failed to load datasets: {error}</p>}
      {!error && items.length === 0 && <p>No datasets yet.</p>}
      {items.length > 0 && (
        <ul className="list">
          {items.map((dataset) => (
            <li key={dataset.id}>
              <strong>{dataset.name}</strong> · {dataset.status}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
