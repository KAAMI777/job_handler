// One function per backend endpoint. Base URL from VITE_API_URL (Vercel / .env).

import { authClient, authConfigured } from "./auth-client";

export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

/** Bearer header for the current Supabase session, or {} when auth is off / signed out. */
async function authHeader() {
  if (!authConfigured) return {};
  const { data } = await authClient.getSession();
  return data.session ? { authorization: `Bearer ${data.session.access_token}` } : {};
}

export class ApiError extends Error {
  constructor(status, body, path) {
    super(`${path} → ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function request(path, { method = "GET", body, params } = {}) {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, v);
    }
  }
  const res = await fetch(url, {
    method,
    headers: {
      ...(body ? { "content-type": "application/json" } : {}),
      ...(await authHeader()),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = null;
    try {
      detail = await res.json();
    } catch {
      /* no body */
    }
    throw new ApiError(res.status, detail, path);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => request("/health"),

  // auth
  register: (payload) => request("/api/v1/auth/register", { method: "POST", body: payload }),
  login: (payload) => request("/api/v1/auth/login", { method: "POST", body: payload }),

  // companies
  listCompanies: () => request("/api/v1/companies"),
  resolveAts: (url) => request("/api/v1/companies/resolve", { method: "POST", body: { url } }),
  createCompany: (payload) => request("/api/v1/companies", { method: "POST", body: payload }),
  updateCompany: (id, payload) =>
    request(`/api/v1/companies/${id}`, { method: "PATCH", body: payload }),
  setCompanyActive: (id, active) =>
    request(`/api/v1/companies/${id}/${active ? "enable" : "disable"}`, { method: "POST" }),
  deleteCompany: (id) => request(`/api/v1/companies/${id}`, { method: "DELETE" }),

  // jobs
  listJobs: (params) => request("/api/v1/jobs", { params }),

  // stats
  stats: () => request("/api/v1/stats"),

  // scrape
  startScrape: () =>
    request("/api/v1/scrape/run", { method: "POST", body: { run_type: "manual" } }),
  getScrapeRun: (id) => request(`/api/v1/scrape/run/${id}`),
  listScrapeRuns: (limit = 10) => request("/api/v1/scrape/runs", { params: { limit } }),

  // keyword rules
  listKeywordRules: () => request("/api/v1/keyword-rules"),
  createKeywordRule: (payload) =>
    request("/api/v1/keyword-rules", { method: "POST", body: payload }),
  updateKeywordRule: (id, payload) =>
    request(`/api/v1/keyword-rules/${id}`, { method: "PATCH", body: payload }),
  deleteKeywordRule: (id) => request(`/api/v1/keyword-rules/${id}`, { method: "DELETE" }),

  // saved jobs
  listSavedJobs: (status) => request("/api/v1/saved-jobs", { params: { status } }),
  saveJob: (jobId, status = "saved") =>
    request(`/api/v1/saved-jobs/${jobId}`, { method: "PUT", body: { status } }),
  unsaveJob: (jobId) => request(`/api/v1/saved-jobs/${jobId}`, { method: "DELETE" }),

  // settings
  getSettings: () => request("/api/v1/settings"),
  updateSettings: (payload) => request("/api/v1/settings", { method: "PATCH", body: payload }),
};
