"use client";

import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import type { AuthUser } from "@/lib/auth/api";
import { clearToken, fetchCurrentUser, getToken } from "@/lib/auth/api";

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  /** Re-checks localStorage and re-fetches the current user. Call this right
   * after setToken() (e.g. on login/signup success), since writing to
   * localStorage doesn't itself notify this shared state. */
  refresh: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(() => getToken() !== null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const token = getToken();
    // No token: initial state already reflects "logged out" correctly
    // (see the lazy useState initializers above), and refresh() is only
    // ever called right after a successful setToken(), so this branch is
    // only reached on a first mount with no session - nothing to fetch.
    if (!token) return;

    fetchCurrentUser(token)
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setIsLoading(false));
  }, [refreshKey]);

  const logout = () => {
    clearToken();
    setUser(null);
  };

  const refresh = () => setRefreshKey((key) => key + 1);

  return (
    <AuthContext.Provider value={{ user, isLoading, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
