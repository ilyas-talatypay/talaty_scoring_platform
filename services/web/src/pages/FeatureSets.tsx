import { useEffect, useState } from "react";

import { apiGet } from "../api/client";

type FeatureSet = {
  id: string;
  name: string;
};

export default function FeatureSetsPage() {
  const [items, setItems] = useState<FeatureSet[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<FeatureSet[]>("/feature-sets")
      .then(setItems)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="card">
      <h2>Feature Sets</h2>
      {error && <p>Failed to load feature sets: {error}</p>}
      {!error && items.length === 0 && <p>No feature sets yet.</p>}
      {items.length > 0 && (
        <ul className="list">
          {items.map((featureSet) => (
            <li key={featureSet.id}>{featureSet.name}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
