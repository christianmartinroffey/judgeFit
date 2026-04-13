export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to handle responses
export async function handleResponse(response) {
  if (response.status === 401) {
    const isAuthEndpoint = response.url?.includes('/api/token/');
    if (!isAuthEndpoint && typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/?view=login';
    }
    throw new Error('Session expired. Please log in again.');
  }
  if (!response.ok) {
    console.log("response not ok:", response)
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || 'Something went wrong');
  }
  return response.json();
}

// Helper function to get headers
export function getHeaders() {
  const headers = {
    'Content-Type': 'application/json',
  };

  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}
