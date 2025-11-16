'use client';

import { UploadForm } from '@/components/lectures/UploadForm';
import { Layout } from '@/components/Layout';
import { ProtectedRoute } from '@/components/auth/RouteGuards';

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <Layout>
        <UploadForm />
      </Layout>
    </ProtectedRoute>
  );
}
