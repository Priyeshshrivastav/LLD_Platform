import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";

export default function ProblemList() {
  const [problems, setProblems] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listProblems()
      .then(setProblems)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <div className="state-message error">
        Couldn't load problems: {error}.{" "}
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (problems === null) {
    return <div className="state-message">Loading problems…</div>;
  }

  if (problems.length === 0) {
    return <div className="state-message">No problems available yet.</div>;
  }

  return (
    <div>
      <h1>LLD Practice Platform</h1>
      <p className="subtitle">
        Choose a problem, design a solution, and get structured, evidence-based
        feedback on your design.
      </p>
      <div className="problem-grid">
        {problems.map((p) => (
          <Link to={`/problems/${p.id}`} key={p.id} className="problem-card">
            <div className="problem-card-header">
              <h3>{p.title}</h3>
              <span className="difficulty-badge">{p.difficulty}</span>
            </div>
            <p>{p.summary}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
