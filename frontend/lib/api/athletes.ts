import { API_BASE_URL, getHeaders, handleResponse } from "@/lib/api";

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

