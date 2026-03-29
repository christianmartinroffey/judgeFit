import { API_BASE_URL, handleResponse } from "@/lib/api";

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