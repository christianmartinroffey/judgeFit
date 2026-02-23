import { API_BASE_URL, getHeaders, handleResponse } from "@/lib/api";

// API functions
export const getVideos = async () => {
  const response = await fetch(`${API_BASE_URL}/api/video/videos`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const getVideo = async (id: number) => {
  const response = await fetch(`${API_BASE_URL}/api/video/videos/${id}/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const submitVideo = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/video/videos/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse(response);
};

export const updateVideo = async (id, data) => {
  const response = await fetch(`${API_BASE_URL}/api/video/videos/${id}/`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteVideo = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/athlete/athletes/${id}/`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error('Failed to delete Athlete');
  }
  return;
};

