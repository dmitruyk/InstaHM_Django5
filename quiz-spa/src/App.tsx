import { Link, Route, Routes, Navigate } from "react-router-dom";
import Play from "./pages/Play";
import Attempts from "./pages/Attempts";
import AttemptDetail from "./pages/AttemptDetail";
import AdminQuestions from "./pages/AdminQuestions";

export default function App() {
  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 16 }}>
      <nav style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Link to="/play">Play</Link>
        <Link to="/attempts">My Attempts</Link>
        <Link to="/admin/questions">Admin: Questions</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Navigate to="/play" replace />} />
        <Route path="/play" element={<Play />} />
        <Route path="/attempts" element={<Attempts />} />
        <Route path="/attempts/:id" element={<AttemptDetail />} />
        <Route path="/admin/questions" element={<AdminQuestions />} />
      </Routes>
    </div>
  );
}
