const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function authHeaders(token) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    let detail = "Request failed";
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return undefined;
  return res.json();
}

export const api = {
  register(data) {
    return request("/auth/register", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
  },
  login(data) {
    return request("/auth/login", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
  },
  me(token) {
    return request("/users/me", { headers: authHeaders(token) });
  },
  logout(token) {
    return request("/auth/logout", {
      method: "POST",
      headers: authHeaders(token),
    });
  },
  listContent(token) {
    return request("/content", { headers: authHeaders(token) });
  },
  createContent(token, data) {
    return request("/content", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  deleteContent(token, contentId) {
    return request(`/content/${contentId}`, {
      method: "DELETE",
      headers: authHeaders(token),
    });
  },
  startSession(token, content_id) {
    return request("/sessions", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ content_id }),
    });
  },
  postReading(token, sessionId, data) {
    return request(`/sessions/${sessionId}/readings`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  endSession(token, sessionId) {
    return request(`/sessions/${sessionId}/end`, {
      method: "POST",
      headers: authHeaders(token),
    });
  },
  listSessions(token) {
    return request("/sessions", { headers: authHeaders(token) });
  },
  getSession(token, sessionId) {
    return request(`/sessions/${sessionId}`, { headers: authHeaders(token) });
  },
};
