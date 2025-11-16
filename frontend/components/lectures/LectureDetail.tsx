'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { getLecture, getAnalysis } from '@/api/lectures';
import { usePolling } from '@/hooks/usePolling';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { MetricCards } from './MetricCards';
import { EmotionChart } from '../analysis/EmotionChart';
import { PeaksDips } from '../analysis/PeaksDips';
import { Suggestions } from '../analysis/Suggestions';
import type { Lecture, Analysis } from '@/types/index';

interface LectureDetailProps {
  lectureId: string;
}

function LectureDetailComponent({ lectureId }: LectureDetailProps) {
  const [lecture, setLecture] = useState<Lecture | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();
  const router = useRouter();

  const { isPolling, stopPolling } = usePolling(async () => {
    if (!token || !lecture) return;

    try {
      const updated = await getLecture(token, lectureId);
      setLecture(updated);

      if (!updated.processing && analysis === null) {
        const analysisData = await getAnalysis(token, lectureId);
        setAnalysis(analysisData);
        stopPolling();
      }
    } catch (err) {
      console.error('Polling error:', err);
    }
  });

  useEffect(() => {
    if (!token) {
      router.push('/auth/login');
      return;
    }

    const fetchLecture = async () => {
      try {
        setLoading(true);
        const data = await getLecture(token, lectureId);
        setLecture(data);

        if (!data.processing) {
          const analysisData = await getAnalysis(token, lectureId);
          setAnalysis(analysisData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch lecture');
      } finally {
        setLoading(false);
      }
    };

    fetchLecture();
  }, [token, lectureId, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <Spinner className="w-8 h-8 text-blue-500" />
      </div>
    );
  }

  if (!lecture) {
    return (
      <div className="min-h-screen bg-slate-900 p-4 md:p-8">
        <Button onClick={() => router.back()} className="mb-6">
          ← Back
        </Button>
        <Alert variant="destructive">{error || 'Lecture not found'}</Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <Button onClick={() => router.back()} className="mb-6 text-slate-400 hover:text-white">
          ← Back
        </Button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">{lecture.title}</h1>
          <p className="text-slate-400">{lecture.subject}</p>
        </div>

        {lecture.processing && (
          <Alert className="mb-6 bg-yellow-900/20 border-yellow-900 text-yellow-400">
            <AlertDescription className="flex items-center gap-2">
              <Spinner className="w-4 h-4" />
              Analysis in progress...
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive" className="mb-6 bg-red-900/20 border-red-900 text-red-400">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {analysis && (
          <div className="space-y-8">
            <MetricCards analysis={analysis} />
            <EmotionChart analysis={analysis} />
            <PeaksDips analysis={analysis} />
            <Suggestions analysis={analysis} />
          </div>
        )}
      </div>
    </div>
  );
}

export { LectureDetailComponent as LectureDetail };
