'use client';

import { LoginForm } from '@/components/auth/LoginForm';
import { Layout } from '@/components/Layout';
import { PublicOnlyRoute } from '@/components/auth/RouteGuards';

export default function LoginPage() {
  return (
    <PublicOnlyRoute>
      <Layout>
        <LoginForm />
      </Layout>
    </PublicOnlyRoute>
  );
}
