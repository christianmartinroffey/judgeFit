import { API_BASE_URL, getHeaders, handleResponse } from "@/lib/api";

// API functions
export const getVideos = async () => {
  const response = await fetch(`${API_BASE_URL}/api/workout/videos`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const getVideo = async (id: number) => {
  const response = await fetch(`${API_BASE_URL}/api/workout/videos/${id}/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const submitVideo = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/workout/videos/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse(response);
};

export const updateVideo = async (id, data) => {
  const response = await fetch(`${API_BASE_URL}/api/workout/videos/${id}/`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteVideo = async (id) => {
  const response = await fetch(`${API_BASE_URL}/api/workout/videos/${id}/`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error('Failed to delete video submission');
  }
  return;
};

