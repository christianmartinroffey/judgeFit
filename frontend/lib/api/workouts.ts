import { API_BASE_URL, getHeaders, handleResponse } from "@/lib/api";

export const getWorkouts = async () => {
  const response = await fetch(`${API_BASE_URL}/api/workout/workouts/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};
