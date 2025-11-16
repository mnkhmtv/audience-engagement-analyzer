'use client';

import { useEffect, useRef, useState } from 'react';

export function usePolling(callback: () => Promise<void>, interval: number = 3000) {
  const [isPolling, setIsPolling] = useState(true);
  const intervalRef = useRef<NodeJS.Timeout>();

  const stopPolling = () => setIsPolling(false);

  useEffect(() => {
    if (!isPolling) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    intervalRef.current = setInterval(callback, interval);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPolling, callback, interval]);

  return { isPolling, stopPolling };
}
