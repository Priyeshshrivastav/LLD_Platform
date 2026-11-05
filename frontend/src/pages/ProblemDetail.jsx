import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../api/client.js";
import StatusBadge from "../components/StatusBadge.jsx";

export default function ProblemDetail() {
  const { problemId } = useParams();
  const navigate = useNavigate();
  const [problem, setProblem] = useState(null);
  const [attempts, setAttempts] = useState(null);
  const [error, setError] = useState(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    setProblem(null);
    setAttempts(null);
    setError(null);
    Promise.all([api.getProblem(problemId), api.listProblemAttempts(problemId)])
      .then(([p, a]) => {
        setProblem(p);
        setAttempts(a);
      })
      .catch((err) => setError(err.message));
  }, [problemId]);

  async function handleStart() {
    setStarting(true);
    try {
      const attempt = await api.startAttempt(problemId);
      navigate(`/attempts/${attempt.id}/edit`);
    } catch (err) {
      setError(err.message);
      setStarting(false);
    }
  }

  if (error) {
    return <div className="state-message error">Something went wrong: {error}</div>;
  }
  if (problem === null) {
    return <div className="state-message">Loading problem…</div>;
  }

  return (
    <div>
      <Link to="/" className="back-link">
        ← All problems
      </Link>
      <div className="problem-detail-header">
        <h1>{problem.title}</h1>
        <span className="difficulty-badge">{problem.difficulty}</span>
      </div>
      <p className="subtitle">{problem.summary}</p>

      <section>
        <h3>Requirements</h3>
        <pre className="requirements-block">{problem.requirements}</pre>
      </section>
      <section>
        <h3>Constraints</h3>
        <pre className="requirements-block">{problem.constraints}</pre>
      </section>

      <button className="primary-button" onClick={handleStart} disabled={starting}>
        {starting ? "Starting…" : "Start New Attempt"}
      </button>

      <section className="past-attempts">
        <h3>Your Past Attempts</h3>
        {attempts.length === 0 ? (
          <p className="state-message">No attempts yet — start your first above.</p>
        ) : (
          <ul className="attempt-list">
            {attempts.map((a) => (
              <li key={a.id}>
                <Link to={`/attempts/${a.id}`}>
                  Attempt #{a.id} — {new Date(a.created_at).toLocaleString()}
                </Link>
                <StatusBadge status={a.status} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
