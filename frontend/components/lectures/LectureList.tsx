'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { getLectures } from '@/api/lectures';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { Lecture } from '@/types/index';

function LectureListComponent() {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.push('/auth/login');
      return;
    }

    const fetchLectures = async () => {
      try {
        setLoading(true);
        const data = await getLectures(token);
        setLectures(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch lectures');
      } finally {
        setLoading(false);
      }
    };

    fetchLectures();
  }, [token, router]);

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <Spinner className="w-8 h-8 text-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">My Lectures</h1>
          <div className="flex gap-4">
            <Link href="/lectures/upload">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white">Upload Lecture</Button>
            </Link>
            <Button variant="outline" onClick={handleLogout} className="text-slate-200 border-slate-600">
              Logout
            </Button>
          </div>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6 bg-red-900/20 border-red-900 text-red-400">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {lectures.length === 0 ? (
          <Card className="bg-slate-800 border-slate-700 p-8 text-center">
            <p className="text-slate-400">No lectures yet. Upload one to get started!</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lectures.map((lecture) => (
              <Link key={lecture.id} href={`/lectures/${lecture.id}`}>
                <Card className="bg-slate-800 border-slate-700 hover:border-blue-500 cursor-pointer transition-colors h-full">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white line-clamp-2">{lecture.title}</h3>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          lecture.processing
                            ? 'bg-yellow-900/30 text-yellow-400'
                            : 'bg-green-900/30 text-green-400'
                        }`}
                      >
                        {lecture.processing ? 'Processing' : 'Ready'}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm mb-4">{lecture.subject}</p>
                    <p className="text-xs text-slate-500">
                      {new Date(lecture.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export { LectureListComponent as LectureList };
