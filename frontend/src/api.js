const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

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
      if (typeof body.detail === "string") detail = body.detail;
      else if (body.detail) detail = JSON.stringify(body.detail);
    } catch {
      /* ignore */
    }
    throw new ApiError(detail, res.status);
  }
  if (res.status === 204) return null;
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
  logout(token) {
    return request("/auth/logout", { method: "POST", headers: authHeaders(token) });
  },
  me(token) {
    return request("/users/me", { headers: authHeaders(token) });
  },
  updateMe(token, data) {
    return request("/users/me", {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  changePassword(token, data) {
    return request("/users/me/password", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  deleteMe(token) {
    return request("/users/me", { method: "DELETE", headers: authHeaders(token) });
  },
  listContent(token) {
    return request("/content", { headers: authHeaders(token) });
  },
  getContent(token, id) {
    return request(`/content/${id}`, { headers: authHeaders(token) });
  },
  createContent(token, data) {
    return request("/content", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  deleteContent(token, id) {
    return request(`/content/${id}`, { method: "DELETE", headers: authHeaders(token) });
  },
  createSession(token, contentId) {
    return request("/sessions", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ content_id: contentId }),
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
  getSession(token, id) {
    return request(`/sessions/${id}`, { headers: authHeaders(token) });
  },
};
