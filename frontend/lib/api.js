export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

let _refreshPromise = null;

export async function attemptRefresh() {
  if (typeof window === 'undefined') return false;
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;

  try {
    const res = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('access_token', data.access);
    return true;
  } catch {
    return false;
  }
}

function _logout() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/?view=login';
}

export async function apiFetch(url, options = {}) {
  const response = await fetch(url, options);

  if (response.status !== 401) return response;

  // Never refresh for auth endpoints themselves
  if (url.includes('/api/token/') || url.includes('/api/register/')) return response;

  // No refresh token stored — not logged in, return as-is
  if (typeof window === 'undefined' || !localStorage.getItem('refresh_token')) return response;

  // Deduplicate concurrent refresh attempts with a shared promise
  if (!_refreshPromise) {
    _refreshPromise = attemptRefresh().finally(() => { _refreshPromise = null; });
  }
  const refreshed = await _refreshPromise;

  if (!refreshed) {
    _logout();
    throw new Error('Session expired. Please log in again.');
  }

  // Retry original request with fresh token
  return fetch(url, {
    ...options,
    headers: { ...(options.headers ?? {}), ...getHeaders() },
  });
}

export async function handleResponse(response) {
  if (!response.ok) {
    console.log('response not ok:', response);
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.message || 'Something went wrong');
  }
  return response.json();
}

export function getHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}
