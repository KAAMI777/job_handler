// Single source of truth for the backend base URL.
// Set VITE_API_URL in .env for local dev and in the Vercel project settings for deploys.
export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

/**
 * Fetch JSON from the backend API.
 * @param {string} path - Path beginning with "/", e.g. "/health".
 * @param {RequestInit} [options]
 * @returns {Promise<any>}
 */
export async function apiFetch(path, options) {
  const res = await fetch(`${API_BASE_URL}${path}`, options);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed with ${res.status}`);
  }
  return res.json();
}
