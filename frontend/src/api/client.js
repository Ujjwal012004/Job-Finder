import axios from 'axios';

// Base API Client
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // FastAPI Backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor to add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // If we receive a 401 Unauthorized, we might want to log the user out
    if (error.response && error.response.status === 401) {
      // Don't auto-logout on the login route itself
      if (!error.config.url.includes('/auth/login')) {
        localStorage.removeItem('token');
        window.dispatchEvent(new Event('auth-expired'));
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
