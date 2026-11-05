import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";
import StatusBadge from "../components/StatusBadge.jsx";

export default function History() {
  const [attempts, setAttempts] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listAttempts()
      .then(setAttempts)
      .catch((err) => setError(err.message));
  }, []);

  if (error) {
    return <div className="state-message error">Couldn't load history: {error}</div>;
  }
  if (attempts === null) {
    return <div className="state-message">Loading history…</div>;
  }
  if (attempts.length === 0) {
    return (
      <div className="state-message">
        No attempts yet — <Link to="/">pick a problem</Link> to start.
      </div>
    );
  }

  return (
    <div>
      <h1>Attempt History</h1>
      <table className="history-table">
        <thead>
          <tr>
            <th>Problem</th>
            <th>Attempt</th>
            <th>Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {attempts.map(({ attempt, problem_title }) => (
            <tr key={attempt.id}>
              <td>{problem_title}</td>
              <td>
                <Link to={`/attempts/${attempt.id}`}>#{attempt.id}</Link>
              </td>
              <td>{new Date(attempt.created_at).toLocaleString()}</td>
              <td>
                <StatusBadge status={attempt.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
