'use client';

import { useState } from 'react';
import { analysisApi } from '@/api/analysis';

export function DevPanel() {
  const isDev = process.env.NODE_ENV !== 'production';
  const [lectureId, setLectureId] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState('');

  if (!isDev) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResponse(null);

    if (!lectureId || !videoFile) {
      setError('Lecture ID and video file required');
      return;
    }

    setLoading(true);
    try {
      const result = await analysisApi.analyzeVideo(lectureId, videoFile);
      setResponse(result.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 w-96 max-h-96 bg-slate-900 border border-slate-700 rounded-lg shadow-xl overflow-hidden flex flex-col">
      <div className="bg-slate-800 px-4 py-2 border-b border-slate-700">
        <h3 className="text-white font-semibold text-sm">Dev Panel</h3>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-3">
        <form onSubmit={handleSubmit} className="space-y-2">
          <input
            type="text"
            placeholder="Lecture ID"
            value={lectureId}
            onChange={(e) => setLectureId(e.target.value)}
            className="w-full px-2 py-1 bg-slate-800 border border-slate-600 rounded text-white text-xs"
          />
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
            className="w-full text-white text-xs"
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full px-2 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white text-xs rounded"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>

        {error && <div className="bg-red-900 text-red-200 p-2 rounded text-xs">{error}</div>}

        {response && (
          <pre className="bg-slate-800 p-2 rounded text-xs text-slate-300 overflow-auto max-h-48">
            {JSON.stringify(response, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}

export default DevPanel;
