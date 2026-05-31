import { API_BASE_URL, apiFetch, getHeaders, handleResponse } from "@/lib/api";

export const getWorkouts = async () => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/workouts/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};
