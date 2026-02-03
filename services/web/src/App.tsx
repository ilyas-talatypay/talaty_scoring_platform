import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";

import DatasetsPage from "./pages/Datasets";
import FeatureSetsPage from "./pages/FeatureSets";
import LoginPage from "./pages/Login";
import ModelsPage from "./pages/Models";
import RunsPage from "./pages/Runs";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <aside className="sidebar">
          <h1>Talaty Scoring</h1>
          <nav className="nav">
            <NavLink to="/" className={({ isActive }) => (isActive ? "active" : "")}>
              Datasets
            </NavLink>
            <NavLink
              to="/feature-sets"
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              Feature Sets
            </NavLink>
            <NavLink to="/runs" className={({ isActive }) => (isActive ? "active" : "")}>
              Runs
            </NavLink>
            <NavLink to="/models" className={({ isActive }) => (isActive ? "active" : "")}>
              Models
            </NavLink>
            <NavLink to="/login" className={({ isActive }) => (isActive ? "active" : "")}>
              Login
            </NavLink>
          </nav>
        </aside>
        <main className="content">
          <Routes>
            <Route path="/" element={<DatasetsPage />} />
            <Route path="/feature-sets" element={<FeatureSetsPage />} />
            <Route path="/runs" element={<RunsPage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/login" element={<LoginPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
