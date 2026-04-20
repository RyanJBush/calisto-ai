import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
});

export function getToken() {
  return localStorage.getItem("calisto_token");
}

export function setToken(token) {
  localStorage.setItem("calisto_token", token);
}

export function clearToken() {
  localStorage.removeItem("calisto_token");
}

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(email, password) {
  const { data } = await api.post("/api/auth/login", { email, password });
  setToken(data.access_token);
  return data;
}

export async function me() {
  const { data } = await api.get("/api/auth/me");
  return data;
}

export async function listDocuments() {
  const { data } = await api.get("/api/documents");
  return data;
}

export async function uploadDocument(payload) {
  const { data } = await api.post("/api/documents/upload", payload);
  return data;
}

export async function queryChat(payload) {
  const { data } = await api.post("/api/chat/query", payload);
  return data;
}

export async function fetchHistory() {
  const { data } = await api.get("/api/chat/history");
  return data;
}

export async function fetchAdminAnalyticsSummary() {
  const { data } = await api.get("/api/admin/analytics/summary");
  return data;
}
