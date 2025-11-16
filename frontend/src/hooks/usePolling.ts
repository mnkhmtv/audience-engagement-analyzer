'use client';

import { useEffect, useRef } from 'react';

export const usePolling = (
  callback: () => Promise<boolean>,
  interval: number = 3000,
  shouldPoll: boolean = true
) => {
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!shouldPoll) return;

    const poll = async () => {
      const shouldContinue = await callback();
      if (shouldContinue) {
        pollRef.current = setTimeout(poll, interval);
      }
    };

    poll();

    return () => {
      if (pollRef.current) clearTimeout(pollRef.current);
    };
  }, [callback, interval, shouldPoll]);
};
