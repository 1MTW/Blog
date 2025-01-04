import axios from "axios";
import { getCookie } from "@/utils/useCookie";

const apiClient = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});


apiClient.interceptors.request.use(
  (config) => {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) {
      config.headers["X-CSRFToken"] = csrfToken;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error("API Request Error:", {
        message: error.message,
        config: error.config,
        response: error.response,
      });
      return Promise.reject(error);
    }
);
  

export default apiClient;
