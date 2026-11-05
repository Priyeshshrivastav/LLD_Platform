const CLASSIFICATION_LABEL = {
  issue: "Issue",
  improvement: "Possible improvement",
  tradeoff: "Trade-off",
  preference: "Preference",
};

const CLASSIFICATION_COLOR = {
  issue: "#d6483b",
  improvement: "#3b6fd6",
  tradeoff: "#c98a1f",
  preference: "#8a8a8a",
};

export default function CriterionCard({ criterion }) {
  const color = CLASSIFICATION_COLOR[criterion.classification] || "#8a8a8a";
  return (
    <div className="criterion-card">
      <div className="criterion-header">
        <strong>{criterion.name}</strong>
        <span className="criterion-score">{criterion.score}/10</span>
        <span
          className="criterion-classification"
          style={{ backgroundColor: color }}
        >
          {CLASSIFICATION_LABEL[criterion.classification] || criterion.classification}
        </span>
      </div>
      <p className="criterion-evidence">
        <em>Evidence:</em> {criterion.evidence}
      </p>
      <p className="criterion-concern">{criterion.concern}</p>
      <p className="criterion-suggestion">
        <strong>Suggestion:</strong> {criterion.suggestion}
      </p>
      <p className="criterion-confidence">Confidence: {criterion.confidence}/10</p>
    </div>
  );
}
