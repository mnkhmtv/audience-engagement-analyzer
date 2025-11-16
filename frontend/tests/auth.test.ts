import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getTokens, setTokens, clearTokens, isTokenExpired } from '../src/utils/jwt';

describe('JWT Utils', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should set and get tokens', () => {
    setTokens('access123', 'refresh456');
    const tokens = getTokens();
    expect(tokens.access).toBe('access123');
    expect(tokens.refresh).toBe('refresh456');
  });

  it('should clear tokens', () => {
    setTokens('access123', 'refresh456');
    clearTokens();
    const tokens = getTokens();
    expect(tokens.access).toBeNull();
    expect(tokens.refresh).toBeNull();
  });

  it('should detect expired tokens', () => {
    // Token with past expiration
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.test';
    expect(isTokenExpired(expiredToken)).toBe(true);
  });

  it('should detect valid tokens', () => {
    // Token with future expiration (year 2099)
    const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQwNzA5MDg4MDB9.test';
    expect(isTokenExpired(validToken)).toBe(false);
  });
});
