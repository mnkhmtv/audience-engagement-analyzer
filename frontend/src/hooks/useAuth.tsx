'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, SignupPayload } from '@/api/auth';
import { clearTokens, getTokens, setTokens } from '@/utils/jwt';

interface AuthContextType {
  isAuthenticated: boolean;
  loading: boolean;
  signup: (payload: SignupPayload) => Promise<void>;
  signin: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const { access } = getTokens();
    setIsAuthenticated(Boolean(access));
    setLoading(false);
  }, []);

  const signup = async (payload: SignupPayload) => {
    const { data } = await authApi.signup(payload);
    setTokens(data.access_token, data.refresh_token);
    setIsAuthenticated(true);
  };

  const signin = async (email: string, password: string) => {
    const { data } = await authApi.signin(email, password);
    setTokens(data.access_token, data.refresh_token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    clearTokens();
    setIsAuthenticated(false);
    router.push('/auth/login');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, loading, signup, signin, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
