const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function to handle responses
async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || 'Something went wrong');
  }
  return response.json();
}

// Helper function to get headers
function getHeaders() {
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

// API functions
export const getAthletes = async () => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const getAthlete = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/${id}/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const createAthlete = async (data) => {
  console.log("called with:", data, getHeaders())
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const updateAthlete = async (id, data) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/${id}/`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteAthlete = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/${id}/`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error('Failed to delete Athlete');
  }
  // DELETE typically returns no content
  return;
};

// Authentication
export const login = async (credentials) => {
  const response = await fetch(`${API_BASE_URL}/api/token/`, {
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