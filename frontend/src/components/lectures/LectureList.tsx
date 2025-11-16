import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { lecturesApi } from '@/api/lectures';
import { Lecture } from '@/types';
import LectureCard from './LectureCard';

export function LectureList() {
  const router = useRouter();
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchLectures = async () => {
      setLoading(true);
      try {
        const { data } = await lecturesApi.list();
        setLectures(data);
        setError('');
      } catch (err: any) {
        if (err.response?.status === 401) {
          router.push('/auth/login');
          return;
        }
        setError(err.response?.data?.detail || err.message || 'Failed to load lectures');
      } finally {
        setLoading(false);
      }
    };

    fetchLectures();
  }, [router]);

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Lectures</h1>
          <p className="text-slate-400">Manage and analyze your lecture videos</p>
        </div>
        <Link
          href="/lectures/upload"
          className="inline-flex justify-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
        >
          Upload Lecture
        </Link>
      </div>

      {error && (
        <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-10 text-slate-400">Loading lectures...</div>
      ) : lectures.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-slate-400 mb-4">No lectures yet. Start by uploading one!</p>
          <Link
            href="/lectures/upload"
            className="inline-flex px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
          >
            Upload Your First Lecture
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {lectures.map((lecture) => (
            <LectureCard key={lecture.id} lecture={lecture} />
          ))}
        </div>
      )}
    </div>
  );
}

export default LectureList;
