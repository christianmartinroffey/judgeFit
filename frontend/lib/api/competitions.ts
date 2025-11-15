import { API_BASE_URL, getHeaders, handleResponse } from "@/lib/api";


// API functions
export const getCompetitions = async () => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/competitions`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const getCompetition = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/competitions/${id}/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const createCompetition = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/competitions/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse(response);
};

export const updateCompetition = async (id, data) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/competitions/${id}/`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteCompetition = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/competitions/${id}/`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error('Failed to delete Competition');
  }
  // DELETE typically returns no content
  return;
};

