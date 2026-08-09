import { API_BASE_URL, apiFetch, getHeaders, handleResponse } from "@/lib/api";

// Authentication
export const login = async (credentials) => {
  const response = await fetch(`${API_BASE_URL}/api/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
  return handleResponse(response);
};

export const register = async (credentials: { username: string; email: string; password: string }) => {
  const response = await fetch(`${API_BASE_URL}/api/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });
  return handleResponse(response);
};

export const refreshToken = async (refresh) => {
  const response = await fetch(`${API_BASE_URL}/api/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  return handleResponse(response);
};

export const requestPasswordReset = async (email: string) => {
  const response = await fetch(`${API_BASE_URL}/api/password-reset/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  return handleResponse(response);
};

export const confirmPasswordReset = async (data: { uid: string; token: string; password: string }) => {
  const response = await fetch(`${API_BASE_URL}/api/password-reset/confirm/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const changePassword = async (data: { old_password: string; new_password: string }) => {
  const response = await apiFetch(`${API_BASE_URL}/api/users/change-password/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteAccount = async (password: string) => {
  const response = await apiFetch(`${API_BASE_URL}/api/users/me/`, {
    method: 'DELETE',
    headers: getHeaders(),
    body: JSON.stringify({ password }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Failed to delete account.');
  }
};