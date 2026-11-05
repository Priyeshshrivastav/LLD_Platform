import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api, ApiError } from "../api/client.js";

const SECTIONS = [
  {
    key: "requirements_understanding",
    label: "Requirements Understanding",
    placeholder:
      "What did you understand the problem to require? Note any assumptions or edge cases you're accounting for.",
  },
  {
    key: "classes_responsibilities",
    label: "Classes & Responsibilities",
    placeholder:
      "List the key classes/interfaces and, for each, what single responsibility it owns.",
  },
  {
    key: "key_relationships",
    label: "Key Relationships",
    placeholder:
      "How do the classes relate to and depend on each other? Note any interfaces used to abstract a varying concern.",
  },
  {
    key: "tradeoffs_assumptions",
    label: "Trade-offs & Assumptions",
    placeholder:
      "What trade-offs did you make, and why? What would change if a stated requirement changed?",
  },
];

const AUTOSAVE_DELAY_MS = 900;

export default function SubmissionEditor() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const [attempt, setAttempt] = useState(null);
  const [content, setContent] = useState({});
  const [error, setError] = useState(null);
  const [saveState, setSaveState] = useState("idle"); // idle | saving | saved
  const [missingSections, setMissingSections] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const timerRef = useRef(null);

  useEffect(() => {
    api
      .getAttempt(attemptId)
      .then((data) => {
        if (data.attempt.status !== "DRAFT") {
          navigate(`/attempts/${attemptId}`, { replace: true });
          return;
        }
        setAttempt(data.attempt);
        setContent(data.submission?.content || {});
      })
      .catch((err) => setError(err.message));

    return () => clearTimeout(timerRef.current);
  }, [attemptId, navigate]);

  function handleChange(key, value) {
    const next = { ...content, [key]: value };
    setContent(next);
    setSaveState("saving");
    setMissingSections((prev) => prev.filter((s) => s !== key));

    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(async () => {
      try {
        await api.saveSubmission(attemptId, { [key]: value });
        setSaveState("saved");
      } catch (err) {
        setError(err.message);
        setSaveState("idle");
      }
    }, AUTOSAVE_DELAY_MS);
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    setMissingSections([]);
    // Flush any pending autosave first so the last edit isn't lost.
    clearTimeout(timerRef.current);
    try {
      await api.saveSubmission(attemptId, content);
      await api.submitAttempt(attemptId);
      navigate(`/attempts/${attemptId}`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 400 && err.body?.missing_sections) {
        setMissingSections(err.body.missing_sections);
      } else {
        setError(err.message);
      }
      setSubmitting(false);
    }
  }

  if (error && !attempt) {
    return <div className="state-message error">Something went wrong: {error}</div>;
  }
  if (!attempt) {
    return <div className="state-message">Loading attempt…</div>;
  }

  return (
    <div>
      <Link to={`/problems/${attempt.problem_id}`} className="back-link">
        ← Back to problem
      </Link>
      <div className="editor-header">
        <h1>Design Your Solution</h1>
        <span className="save-indicator">
          {saveState === "saving" ? "Saving…" : saveState === "saved" ? "Saved" : ""}
        </span>
      </div>

      {missingSections.length > 0 && (
        <div className="state-message error">
          Please fill in: {missingSections.map((s) => s.replaceAll("_", " ")).join(", ")}
        </div>
      )}
      {error && <div className="state-message error">{error}</div>}

      {SECTIONS.map((section) => (
        <div className="editor-section" key={section.key}>
          <label htmlFor={section.key}>
            {section.label}
            {missingSections.includes(section.key) && (
              <span className="required-marker"> — required</span>
            )}
          </label>
          <textarea
            id={section.key}
            rows={5}
            placeholder={section.placeholder}
            value={content[section.key] || ""}
            onChange={(e) => handleChange(section.key, e.target.value)}
          />
        </div>
      ))}

      <button className="primary-button" onClick={handleSubmit} disabled={submitting}>
        {submitting ? "Submitting…" : "Submit for Evaluation"}
      </button>
    </div>
  );
}
