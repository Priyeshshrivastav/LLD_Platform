const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(status, detail, body) {
    super(detail || `Request failed with status ${status}`);
    this.status = status;
    this.body = body;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let body = null;
  try {
    body = await res.json();
  } catch {
    // no JSON body (e.g. some error responses) — fine
  }
  if (!res.ok) {
    throw new ApiError(res.status, body?.detail, body);
  }
  return body;
}

export const api = {
  listProblems: () => request("/problems"),
  getProblem: (id) => request(`/problems/${id}`),
  listProblemAttempts: (id) => request(`/problems/${id}/attempts`),
  startAttempt: (problemId) =>
    request(`/problems/${problemId}/attempts`, { method: "POST" }),

  getAttempt: (id) => request(`/attempts/${id}`),
  listAttempts: (problemId) =>
    request(problemId ? `/attempts?problem_id=${problemId}` : "/attempts"),
  saveSubmission: (attemptId, content) =>
    request(`/attempts/${attemptId}/submission`, {
      method: "PUT",
      body: JSON.stringify(content),
    }),
  submitAttempt: (attemptId) =>
    request(`/attempts/${attemptId}/submit`, { method: "POST" }),

  getEvaluation: (id) => request(`/evaluations/${id}`),
  retryEvaluation: (id) =>
    request(`/evaluations/${id}/retry`, { method: "POST" }),
};

export { ApiError };
