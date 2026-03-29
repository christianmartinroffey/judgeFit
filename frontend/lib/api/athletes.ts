import { API_BASE_URL, getHeaders, handleResponse } from "@/lib/api";

// Returns the athlete data if a profile exists, or { _noProfile: true, userEmail } if not.
export const getMyProfile = async () => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/me/`, {
    headers: getHeaders(),
  });
  if (response.status === 404) {
    const body = await response.json().catch(() => ({}));
    return { _noProfile: true as const, userEmail: (body.user_email as string) ?? '' };
  }
  return handleResponse(response);
};

export const createMyProfile = async (data: Record<string, unknown>) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/me/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const updateMyProfile = async (data: Record<string, unknown>) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/me/`, {
    method: 'PATCH',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

// API functions
export const getAthletes = async () => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const getAthlete = async (id: number) => {
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

export const updateAthlete = async (id: number, data) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/${id}/`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteAthlete = async (id: number) => {
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

