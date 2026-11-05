import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api } from "../api/client.js";
import StatusBadge from "../components/StatusBadge.jsx";
import CriterionCard from "../components/CriterionCard.jsx";

const POLL_INTERVAL_MS = 2500;

export default function Feedback() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [retrying, setRetrying] = useState(false);
  const [startingRetry, setStartingRetry] = useState(false);
  const pollRef = useRef(null);

  const load = useCallback(() => {
    api
      .getAttempt(attemptId)
      .then(setData)
      .catch((err) => setError(err.message));
  }, [attemptId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const status = data?.attempt?.status;
    const isPending = status === "EVALUATING" || status === "SUBMITTED";
    if (isPending) {
      pollRef.current = setTimeout(load, POLL_INTERVAL_MS);
    }
    return () => clearTimeout(pollRef.current);
  }, [data, load]);

  async function handleRetry() {
    if (!data?.evaluation) return;
    setRetrying(true);
    try {
      await api.retryEvaluation(data.evaluation.id);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setRetrying(false);
    }
  }

  async function handleTryAgain() {
    setStartingRetry(true);
    try {
      const attempt = await api.startAttempt(data.attempt.problem_id);
      navigate(`/attempts/${attempt.id}/edit`);
    } catch (err) {
      setError(err.message);
      setStartingRetry(false);
    }
  }

  if (error && !data) {
    return <div className="state-message error">Something went wrong: {error}</div>;
  }
  if (!data) {
    return <div className="state-message">Loading attempt…</div>;
  }

  const { attempt, submission, evaluation } = data;
  const status = attempt.status;

  return (
    <div>
      <Link to={`/problems/${attempt.problem_id}`} className="back-link">
        ← Back to problem
      </Link>
      <div className="editor-header">
        <h1>Attempt #{attempt.id}</h1>
        <StatusBadge status={status} />
      </div>

      {(status === "SUBMITTED" || status === "EVALUATING") && (
        <div className="state-message evaluating">
          <span className="spinner" /> Evaluating your design… this runs in the
          background, feel free to leave this open.
        </div>
      )}

      {status === "FAILED" && evaluation && (
        <div className="state-message error">
          Evaluation failed: {evaluation.error_message || "Unknown error."}
          <div>
            <button className="primary-button" onClick={handleRetry} disabled={retrying}>
              {retrying ? "Retrying…" : "Retry Evaluation"}
            </button>
          </div>
        </div>
      )}

      {status === "COMPLETED" && evaluation?.result && (
        <div className="feedback">
          <div className="feedback-summary">
            <h3>Summary</h3>
            <p>{evaluation.result.summary}</p>
          </div>

          {evaluation.result.strengths?.length > 0 && (
            <div className="feedback-block">
              <h3>Strengths</h3>
              <ul>
                {evaluation.result.strengths.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}

          {evaluation.result.priority_improvements?.length > 0 && (
            <div className="feedback-block">
              <h3>Priority Improvements</h3>
              <ul>
                {evaluation.result.priority_improvements.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}

          <h3>Criteria</h3>
          <div className="criteria-grid">
            {evaluation.result.criteria?.map((c) => (
              <CriterionCard criterion={c} key={c.name} />
            ))}
          </div>

          <button className="primary-button" onClick={handleTryAgain} disabled={startingRetry}>
            {startingRetry ? "Starting…" : "Try Again"}
          </button>
        </div>
      )}

      {submission && status !== "DRAFT" && (
        <details className="submission-recap">
          <summary>View submitted design</summary>
          {Object.entries(submission.content).map(([key, value]) => (
            <div key={key}>
              <strong>{key.replaceAll("_", " ")}</strong>
              <p>{value}</p>
            </div>
          ))}
        </details>
      )}
    </div>
  );
}
