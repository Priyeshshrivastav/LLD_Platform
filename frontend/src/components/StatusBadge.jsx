const COLORS = {
  DRAFT: "#8a8a8a",
  SUBMITTED: "#3b6fd6",
  EVALUATING: "#c98a1f",
  COMPLETED: "#2e9e5b",
  FAILED: "#d6483b",
  PENDING: "#c98a1f",
};

export default function StatusBadge({ status }) {
  if (!status) return null;
  const color = COLORS[status] || "#8a8a8a";
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 10px",
        borderRadius: "999px",
        fontSize: "0.75rem",
        fontWeight: 600,
        color: "#fff",
        backgroundColor: color,
        letterSpacing: "0.02em",
      }}
    >
      {status}
    </span>
  );
}
