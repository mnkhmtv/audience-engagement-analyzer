'use client';

import { LectureList } from '@/components/lectures/LectureList';
import { Layout } from '@/components/Layout';
import { ProtectedRoute } from '@/components/auth/RouteGuards';

export default function LecturesPage() {
  return (
    <ProtectedRoute>
      <Layout>
        <LectureList />
      </Layout>
    </ProtectedRoute>
  );
}
