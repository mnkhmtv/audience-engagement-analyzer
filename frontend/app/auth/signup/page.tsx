'use client';

import { SignupForm } from '@/components/auth/SignupForm';
import { Layout } from '@/components/Layout';
import { PublicOnlyRoute } from '@/components/auth/RouteGuards';

export default function SignupPage() {
  return (
    <PublicOnlyRoute>
      <Layout>
        <SignupForm />
      </Layout>
    </PublicOnlyRoute>
  );
}
