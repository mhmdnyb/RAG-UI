import { useEffect, useState } from "react";
import { getAuthToken, setAuthToken, removeAuthToken, parseJwt, authApi } from "../services/api";
import { AuthContext } from "./auth-context-def";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getAuthToken());
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    const currentToken = getAuthToken();
    if (currentToken) {
      const payload = parseJwt(currentToken);
      if (payload?.sub) {
        return { phoneNumber: payload.sub };
      }
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function verify() {
      const currentToken = getAuthToken();
      if (!currentToken) {
        if (active) {
          setToken(null);
          setUser(null);
          setIsLoading(false);
        }
        return;
      }

      const payload = parseJwt(currentToken);
      if (payload?.exp && payload.exp * 1000 < Date.now()) {
        removeAuthToken();
        localStorage.removeItem("user");
        if (active) {
          setToken(null);
          setUser(null);
          setIsLoading(false);
        }
        return;
      }

      try {
        await authApi.checkAuth();
        if (active) {
          setToken(currentToken);
          if (payload?.sub) {
            setUser((prev) => prev || { phoneNumber: payload.sub });
          }
        }
      } catch {
        removeAuthToken();
        localStorage.removeItem("user");
        if (active) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    verify();

    return () => {
      active = false;
    };
  }, []);

  function login(newToken, userInfo = null) {
    setAuthToken(newToken);
    setToken(newToken);
    const payload = parseJwt(newToken);
    const userData = userInfo || (payload?.sub ? { phoneNumber: payload.sub } : null);
    if (userData) {
      localStorage.setItem("user", JSON.stringify(userData));
      setUser(userData);
    }
  }

  function logout() {
    removeAuthToken();
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }

  const value = {
    token,
    user,
    isAuthenticated: Boolean(token),
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
