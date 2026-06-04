import { createContext, useContext, useEffect, useState } from "react";

import { api } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [tokens, setTokens] = useState(() => {
    const raw = localStorage.getItem("tokens");
    return raw ? JSON.parse(raw) : null;
  });
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const persist = (t) => {
    if (t) localStorage.setItem("tokens", JSON.stringify(t));
    else localStorage.removeItem("tokens");
    setTokens(t);
  };

  useEffect(() => {
    let active = true;
    async function load() {
      if (!tokens?.access) {
        setLoading(false);
        return;
      }
      try {
        const me = await api.me(tokens.access);
        if (active) setUser(me);
      } catch {
        try {
          const r = await api.refresh(tokens.refresh);
          const next = { ...tokens, access: r.access };
          persist(next);
          const me = await api.me(next.access);
          if (active) setUser(me);
        } catch {
          persist(null);
          if (active) setUser(null);
        }
      } finally {
        if (active) setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email, password) => {
    const t = await api.login({ email, password });
    persist(t);
    const me = await api.me(t.access);
    setUser(me);
  };

  const register = async (data) => {
    await api.register(data);
    await login(data.email, data.password);
  };

  const logout = () => {
    persist(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, token: tokens?.access, loading, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
