'use client';

import { useParams } from 'next/navigation';
import { Layout } from '@/components/Layout';
import { LectureDetail } from '@/components/lectures/LectureDetail';
import { ProtectedRoute } from '@/components/auth/RouteGuards';

export default function LectureDetailPage() {
  const params = useParams();
  const lectureId = params.id as string;

  return (
    <ProtectedRoute>
      <Layout>
        <LectureDetail lectureId={lectureId} />
      </Layout>
    </ProtectedRoute>
  );
}
