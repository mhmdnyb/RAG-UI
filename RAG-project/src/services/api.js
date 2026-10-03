const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8080/ws";

export function getAuthToken() {
  const cookieMatch = document.cookie
    .split("; ")
    .find((row) => row.startsWith("token="));
  if (cookieMatch) {
    const value = cookieMatch.split("=")[1];
    if (value) return decodeURIComponent(value);
  }
  return localStorage.getItem("token") || null;
}

export function setAuthToken(token) {
  if (!token) return;
  const expires = new Date(Date.now() + 7 * 24 * 3600 * 1000).toUTCString();
  document.cookie = `token=${encodeURIComponent(token)};expires=${expires};path=/;SameSite=Lax`;
  localStorage.setItem("token", token);
}

export function removeAuthToken() {
  document.cookie = "token=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;";
  localStorage.removeItem("token");
}

export function parseJwt(token) {
  if (!token) return null;
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export async function apiFetch(path, options = {}) {
  const token = getAuthToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type");
  let body = null;
  if (contentType && contentType.includes("application/json")) {
    body = await response.json();
  }

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      removeAuthToken();
    }
    const message = body?.data?.message || body?.message || "درخواست با خطا مواجه شد";
    const error = new Error(message);
    error.status = response.status;
    error.data = body?.data;
    throw error;
  }

  if (body && body.status === "error") {
    const error = new Error(body.data?.message || "خطای سرور");
    error.code = body.data?.code;
    error.data = body.data;
    throw error;
  }

  return body;
}

export const authApi = {
  login: async (phoneNumber, password) => {
    return apiFetch("/login", {
      method: "POST",
      body: JSON.stringify({ phoneNumber, password }),
    });
  },

  register: async (name, phoneNumber, password) => {
    return apiFetch("/register", {
      method: "POST",
      body: JSON.stringify({ name, phoneNumber, password }),
    });
  },

  checkAuth: async () => {
    try {
      const result = await apiFetch("/auth", { method: "GET" });
      return result;
    } catch (err) {
      if (err?.code === "002" || err?.data?.code === "002") {
        return { status: "OK" };
      }
      throw err;
    }
  },
};

export const chatApi = {
  getConversations: async () => {
    const res = await apiFetch("/chat-list", { method: "GET" });
    return res?.data || [];
  },

  createConversation: async () => {
    const res = await apiFetch("/chat-list", { method: "POST" });
    return res?.data;
  },

  deleteConversation: async (chatId) => {
    return apiFetch(`/chat-list/${chatId}`, { method: "DELETE" });
  },

  getMessages: async (chatId) => {
    const res = await apiFetch(`/chat/${chatId}/messages`, { method: "GET" });
    return res?.data || [];
  },
};

export { API_URL, WS_URL };
