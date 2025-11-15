export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to handle responses
export async function handleResponse(response) {
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
  console.log("token  :", token)
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}
