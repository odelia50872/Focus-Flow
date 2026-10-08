import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { ApiError, api } from "./api";

const AuthContext = createContext(null);
const TOKEN_KEY = "focusflow_token";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function hydrate() {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      try {
        const me = await api.me(token);
        if (!cancelled) setUser(me);
      } catch (err) {
        if (!cancelled && err instanceof ApiError && err.status === 401) clearAuth();
        else if (!cancelled) clearAuth();
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    hydrate();
    return () => {
      cancelled = true;
    };
  }, [token, clearAuth]);

  const login = useCallback(async (email, password) => {
    const res = await api.login({ email, password });
    localStorage.setItem(TOKEN_KEY, res.access_token);
    setToken(res.access_token);
    const me = await api.me(res.access_token);
    setUser(me);
  }, []);

  const register = useCallback(async (data) => {
    await api.register(data);
  }, []);

  const logout = useCallback(async () => {
    try {
      if (token) await api.logout(token);
    } catch {
      /* still sign out locally */
    }
    clearAuth();
  }, [token, clearAuth]);

  const value = useMemo(
    () => ({ token, user, loading, login, register, logout, setUser, clearAuth }),
    [token, user, loading, login, register, logout, clearAuth],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
