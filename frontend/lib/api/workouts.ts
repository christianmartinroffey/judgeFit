import { API_BASE_URL, apiFetch, getHeaders, handleResponse } from "@/lib/api";

export const getWorkouts = async (competitionId?: number) => {
  const url = competitionId
    ? `${API_BASE_URL}/api/workout/workouts/?competition=${competitionId}`
    : `${API_BASE_URL}/api/workout/workouts/`;
  const response = await apiFetch(url, { headers: getHeaders() });
  return handleResponse(response);
};

export const createWorkout = async (data: object) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/workouts/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const activateWorkout = async (id: number) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/workouts/${id}/activate/`, {
    method: 'POST',
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const deleteWorkout = async (id: number) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/workouts/${id}/`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to delete workout');
};

export const getMovements = async () => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/movements/`, {
    headers: getHeaders(),
  });
  return handleResponse(response);
};

export const createWorkoutComponent = async (data: object) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/workout-components/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(response);
};

export const deleteWorkoutComponent = async (id: number) => {
  const response = await apiFetch(`${API_BASE_URL}/api/workout/workout-components/${id}/`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to delete workout component');
};
