import { apiBaseUrl, parseErrorMessage, postJson } from "@/lib/api";

export interface AuthUser {
  id: number;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

const TOKEN_STORAGE_KEY = "prelegal_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function signup(email: string, password: string): Promise<AuthResponse> {
  return postJson("/api/auth/signup", { email, password });
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return postJson("/api/auth/login", { email, password });
}

export async function fetchCurrentUser(token: string): Promise<AuthUser> {
  const response = await fetch(`${apiBaseUrl()}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error(await parseErrorMessage(response));
  return response.json();
}
