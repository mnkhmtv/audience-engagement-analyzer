import client from './client';
import { AuthResponse, UserRole } from '../types';

export interface SignupPayload {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  role?: UserRole;
}

export const authApi = {
  signup: (payload: SignupPayload) =>
    client.post('/auth/register', payload),

  signin: (email: string, password: string) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    return client.post<AuthResponse>('/token/get-token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },

  refresh: (refreshToken: string) =>
    client.post<AuthResponse>('/token/refresh', { refresh_token: refreshToken }),
};
