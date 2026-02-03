import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function LoginPage() {
  const navigate = useNavigate();
  const [value, setValue] = useState(
    localStorage.getItem("talaty.user") ?? ""
  );

  return (
    <div className="card">
      <h2>Login (Dev)</h2>
      <p>Set a local user identity for API requests.</p>
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="e.g. analyst@example.com"
        style={{ padding: "8px 12px", width: "100%", maxWidth: 360 }}
      />
      <div style={{ marginTop: 12 }}>
        <button
          onClick={() => {
            localStorage.setItem("talaty.user", value || "dev-user");
            navigate("/");
          }}
        >
          Save
        </button>
      </div>
    </div>
  );
}
