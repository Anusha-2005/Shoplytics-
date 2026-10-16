import axios from 'axios';

// Get base URL from environment variable, with fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Response interceptor for consistent error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let message = 'Network error or backend service unavailable.';
    if (error.response) {
      // Backend returned an error response
      message = error.response.data?.detail || error.response.data?.message || `Error ${error.response.status}: ${error.response.statusText}`;
    } else if (error.request) {
      // Request made but no response received
      message = 'Cannot connect to Shoplytics backend at ' + API_BASE_URL + '. Ensure FastAPI server is running on port 8000.';
    } else {
      message = error.message;
    }
    console.error('API Error:', message, error);
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
