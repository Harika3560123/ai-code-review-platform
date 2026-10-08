import { useState, useEffect } from "react";
import { authService } from "../services/authService";

export function useAuth() {
  const [user, setUser] = useState(authService.getCurrentUser());
  const [token, setToken] = useState(authService.getToken());

  useEffect(() => {
    const handleStorageChange = () => {
      setUser(authService.getCurrentUser());
      setToken(authService.getToken());
    };
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const login = async (email, password) => {
    const res = await authService.login(email, password);
    setUser({ userId: res.user_id, name: res.name, email: res.email });
    setToken(res.access_token);
    return res;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
  };

  return {
    user,
    token,
    isAuthenticated: Boolean(token),
    login,
    logout
  };
}
