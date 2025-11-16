import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { getTokens, setTokens, clearTokens, isTokenExpired } from '../utils/jwt';

const RAW_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const API_BASE = `${RAW_BASE_URL.replace(/\/$/, '')}/api`;

const client: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
client.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    if (typeof window === 'undefined') {
      return config;
    }

    const { access, refresh } = getTokens();

    if (access && !isTokenExpired(access)) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${access}`,
      };
      return config;
    }

    if (refresh) {
      try {
        const response = await axios.post(`${API_BASE}/token/refresh`, {
          refresh_token: refresh,
        });
        const { access_token, refresh_token } = response.data;
        setTokens(access_token, refresh_token);
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${access_token}`,
        };
      } catch {
        clearTokens();
        if (typeof window !== 'undefined') {
          window.location.href = '/auth/login';
        }
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

export default client;
