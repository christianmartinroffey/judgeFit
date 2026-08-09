import { API_BASE_URL, apiFetch, getHeaders, handleResponse } from "@/lib/api";

// API functions
export const getVideos = async () => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/videos`, {
    headers: getHeaders(),
  });
  console.log(response)
  return handleResponse(response);
};

export const getVideo = async (id: string) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/videos/${id}/`, {
    headers: getHeaders(),
  });
  console.log(response, "DA RESPONSE")
  return handleResponse(response);
};

export const submitVideo = async (data) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/videos/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });

  return handleResponse(response);
};


export const deleteVideo = async (id) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/videos/${id}/`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error('Failed to delete video submission');
  }
  return;
};

export const getReviewQueue = async (params: { status?: string; competition?: number } = {}) => {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.competition) query.set('competition', String(params.competition));
  query.set('limit', '100');
  const qs = query.toString();
  const response = await apiFetch(`${API_BASE_URL}/api/workout/videos/review_queue/${qs ? `?${qs}` : ''}`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const approveVideo = async (id: string) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/videos/${id}/approve/`, {
    method: 'POST',
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const rejectVideo = async (id: string) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/videos/${id}/reject/`, {
    method: 'POST',
    headers: getHeaders(),
  });
  return handleResponse(response);
};

