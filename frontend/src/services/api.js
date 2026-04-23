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

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      clearToken();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

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

export async function uploadDocumentFile(payload) {
  const form = new FormData();
  form.append("title", payload.title);
  form.append("file", payload.file);
  if (payload.source_name) form.append("source_name", payload.source_name);
  if (payload.redact_pii) form.append("redact_pii", "true");
  if (payload.collection_id) form.append("collection_id", String(payload.collection_id));
  const { data } = await api.post("/api/documents/upload-file", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
}

export async function createCollection(payload) {
  const { data } = await api.post("/api/documents/collections", payload);
  return data;
}

export async function listCollections() {
  const { data } = await api.get("/api/documents/collections");
  return data;
}

export async function queryChat(payload) {
  const { data } = await api.post("/api/chat/query", payload);
  return data;
}

export async function submitChatFeedback(payload) {
  const { data } = await api.post("/api/chat/feedback", payload);
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

export async function fetchAdminTopDocuments() {
  const { data } = await api.get("/api/admin/analytics/top-documents");
  return data;
}

export async function fetchAdminIngestionBreakdown() {
  const { data } = await api.get("/api/admin/analytics/ingestion-breakdown");
  return data;
}

export async function fetchAdminAuditLogs(params = {}) {
  const { data } = await api.get("/api/admin/audit-logs", { params });
  return data;
}

export async function fetchAdminFeedbackSummary() {
  const { data } = await api.get("/api/admin/analytics/feedback-summary");
  return data;
}

export async function fetchAdminBenchmark() {
  const { data } = await api.get("/api/admin/analytics/benchmark");
  return data;
}

export async function fetchAdminCollectionSummary() {
  const { data } = await api.get("/api/admin/analytics/collections");
  return data;
}

export async function fetchAdminUsers() {
  const { data } = await api.get("/api/admin/users");
  return data;
}

export async function fetchWorkspaceSettings() {
  const { data } = await api.get("/api/admin/workspace");
  return data;
}

export async function updateWorkspaceSettings(payload) {
  const { data } = await api.put("/api/admin/workspace", payload);
  return data;
}

export async function fetchDocumentIngestionRuns(documentId) {
  const { data } = await api.get(`/api/documents/${documentId}/ingestion-runs`);
  return data;
}

export async function retryDocumentIngestion(documentId) {
  const { data } = await api.post(`/api/documents/${documentId}/retry-ingestion`);
  return data;
}

export async function grantDocumentAccess(documentId, payload) {
  const { data } = await api.post(`/api/documents/${documentId}/access`, payload);
  return data;
}

export async function revokeDocumentAccess(documentId, userId) {
  await api.delete(`/api/documents/${documentId}/access/${userId}`);
}
