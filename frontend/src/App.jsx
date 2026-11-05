import { Routes, Route, Link } from "react-router-dom";
import ProblemList from "./pages/ProblemList.jsx";
import ProblemDetail from "./pages/ProblemDetail.jsx";
import SubmissionEditor from "./pages/SubmissionEditor.jsx";
import Feedback from "./pages/Feedback.jsx";
import History from "./pages/History.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <nav className="top-nav">
        <Link to="/" className="nav-brand">
          LLD Practice
        </Link>
        <Link to="/attempts">History</Link>
      </nav>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<ProblemList />} />
          <Route path="/problems/:problemId" element={<ProblemDetail />} />
          <Route path="/attempts" element={<History />} />
          <Route path="/attempts/:attemptId/edit" element={<SubmissionEditor />} />
          <Route path="/attempts/:attemptId" element={<Feedback />} />
        </Routes>
      </main>
    </div>
  );
}
