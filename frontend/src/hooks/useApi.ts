'use client';

import { useState, useCallback, useEffect, useRef } from 'react';

export const useApi = <T,>(apiCall: () => Promise<{ data: T }>, immediate = true) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<Error | null>(null);
  const hasExecuted = useRef(false);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCall();
      setData(response.data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  useEffect(() => {
    if (immediate && !hasExecuted.current) {
      hasExecuted.current = true;
      execute();
    }
  }, [execute, immediate]);

  return { data, loading, error, execute, refetch: execute };
};
