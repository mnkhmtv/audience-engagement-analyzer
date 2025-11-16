'use client';

import { ReactNode, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

interface GuardProps {
  children: ReactNode;
}

function FullScreenMessage({ message }: { message: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-300">
      {message}
    </div>
  );
}

export function ProtectedRoute({ children }: GuardProps) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return <FullScreenMessage message="Checking your session..." />;
  }

  if (!isAuthenticated) {
    return <FullScreenMessage message="Redirecting to sign in..." />;
  }

  return <>{children}</>;
}

export function PublicOnlyRoute({ children }: GuardProps) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.replace('/lectures');
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return <FullScreenMessage message="Loading..." />;
  }

  if (isAuthenticated) {
    return <FullScreenMessage message="Redirecting to your workspace..." />;
  }

  return <>{children}</>;
}
