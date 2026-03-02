import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null); // {id,name,email,role}

  useEffect(() => {
    const t = localStorage.getItem("token");
    const u = localStorage.getItem("user");
    if (t && u) {
      setToken(t);
      try {
        setUser(JSON.parse(u));
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }
  }, []);

  const isAuthed = Boolean(token && user);

  function setSession(tokenValue, userValue) {
    setToken(tokenValue);
    setUser(userValue);
    localStorage.setItem("token", tokenValue);
    localStorage.setItem("user", JSON.stringify(userValue));
  }

  function logout() {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  }

  const value = useMemo(
    () => ({ token, user, isAuthed, setSession, logout }),
    [token, user, isAuthed]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}