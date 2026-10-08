import api from "./api";

export const reviewService = {
  async analyzeCode(code, language, filename) {
    const response = await api.post("/api/review/analyze", {
      code,
      language,
      filename
    });
    return response.data;
  },

  async uploadCodeFile(file, language) {
    const formData = new FormData();
    formData.append("file", file);
    if (language) {
      formData.append("language", language);
    }
    const response = await api.post("/api/review/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
    return response.data;
  },

  async getReviewById(reviewId) {
    const response = await api.get(`/api/review/${reviewId}`);
    return response.data;
  },

  async getReviewHistory() {
    const response = await api.get("/api/review/history");
    return response.data;
  },

  async getDashboardStatistics() {
    const response = await api.get("/api/dashboard/statistics");
    return response.data;
  },

  async generateFix(originalCode, finding, language) {
    const response = await api.post("/api/fix/generate", {
      original_code: originalCode,
      finding,
      language
    });
    return response.data;
  }
};
