import { jwtDecode } from 'jwt-decode';

interface JWTPayload {
  exp: number;
  is_competition_admin: boolean;
}

export function isTokenValid(token: string): boolean {
  try {
    const { exp } = jwtDecode<JWTPayload>(token);
    return exp * 1000 > Date.now();
  } catch {
    return false;
  }
}

export function isAdminToken(token: string): boolean {
  try {
    const decoded = jwtDecode<JWTPayload>(token);
    return decoded.exp * 1000 > Date.now() && decoded.is_competition_admin === true;
  } catch {
    return false;
  }
}

export function checkIsAdmin(): boolean {
  if (typeof window === 'undefined') return false;
  const token = localStorage.getItem('access_token');
  return token ? isAdminToken(token) : false;
}
