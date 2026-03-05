const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, { method = "GET", token, body } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data?.detail || data?.message || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  register: (payload) => request("/auth/register", { method: "POST", body: payload }),
  login: (payload) => request("/auth/login", { method: "POST", body: payload }),
  verifyEmail: (token) => request(`/auth/verify-email?token=${token}`),
  saveScan: (token, payload) => request("/scans/", { method: "POST", token, body: payload }),
  getMyScans: (token) => request("/scans/my", { token }),
  deleteScan: (token, scanId) => request(`/scans/${scanId}`, { method: "DELETE", token }),
  deleteAllScans: (token) => request("/scans/my/all", { method: "DELETE", token }),
  forgotPassword: (email) => request("/auth/forgot-password", { method: "POST", body: { email } }),
  resetPassword: (token, password) => request("/auth/reset-password", { method: "POST", body: { token, password } }),
};

export const adminApi = {
  getStats: (token) => request("/admin/stats", { token }),
  getUsers: (token) => request("/admin/users", { token }),
  deleteUser: (token, userId) => request(`/admin/users/${userId}`, { method: "DELETE", token }),
  changeRole: (token, userId, role) => request(`/admin/users/${userId}/role`, { method: "PATCH", token, body: { role } }),
  getScans: (token) => request("/scans/all", { token }),
};

export const chatApi = {
  getSession: (token) => request("/chat/session", { token }),
  createSession: (token) => request("/chat/session", { method: "POST", token }),
  closeSession: (token, sessionId) => request(`/chat/close/${sessionId}`, { method: "POST", token }),
  getMessages: (token, sessionId) => request(`/chat/messages/${sessionId}`, { token }),
  getAllSessions: (token) => request("/chat/sessions", { token }),
  getHistory: (token) => request("/chat/history", { token }),
  getAllHistory: (token) => request("/chat/history/all", { token }),
  getUnread: (token) => request("/chat/unread", { token }),
};

export const profileApi = {
  getMe: (token) => request("/auth/me", { token }),
  changePassword: (token, current_password, new_password) =>
    request("/auth/me/password", { method: "PATCH", token, body: { current_password, new_password } }),
  deleteMe: (token) => request("/auth/me", { method: "DELETE", token }),
};

