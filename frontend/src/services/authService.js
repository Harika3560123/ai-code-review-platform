import api from "./api";

export const authService = {
  async register(name, email, password) {
    const response = await api.post("/api/auth/register", { name, email, password });
    return response.data;
  },

  async login(email, password) {
    const response = await api.post("/api/auth/login", { email, password });
    if (response.data.access_token) {
      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify({
        userId: response.data.user_id,
        name: response.data.name,
        email: response.data.email,
      }));
    }
    return response.data;
  },

  logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  },

  getCurrentUser() {
    const userStr = localStorage.getItem("user");
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  },

  getToken() {
    return localStorage.getItem("token");
  },

  isAuthenticated() {
    return Boolean(localStorage.getItem("token"));
  },

  async fetchProfile() {
    const response = await api.get("/api/auth/profile");
    return response.data;
  }
};
