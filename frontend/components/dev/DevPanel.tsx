'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { analyzeVideo } from '@/api/analysis';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Spinner } from '@/components/ui/spinner';
import type { AnalysisResponse } from '@/types/index';

export function DevPanel() {
  const [lectureId, setLectureId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState('');
  const { token } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResponse(null);

    if (!lectureId || !file) {
      setError('Please provide lecture ID and video file');
      return;
    }

    setLoading(true);

    try {
      const result = await analyzeVideo(token!, lectureId, file);
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 w-96 max-h-96 bg-slate-800 border border-slate-700 rounded-lg shadow-lg overflow-hidden flex flex-col">
      <div className="bg-slate-700 px-4 py-3">
        <h3 className="text-white font-bold">Dev Panel</h3>
      </div>

      <div className="overflow-y-auto flex-1 p-4 space-y-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <Input
            type="text"
            value={lectureId}
            onChange={(e) => setLectureId(e.target.value)}
            placeholder="Lecture ID"
            className="bg-slate-700 border-slate-600 text-white text-sm"
          />
          <Input
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="bg-slate-700 border-slate-600 text-slate-400 text-sm"
          />
          <Button type="submit" disabled={loading} className="w-full bg-purple-600 hover:bg-purple-700 text-sm">
            {loading ? <Spinner className="w-4 h-4" /> : 'Analyze'}
          </Button>
        </form>

        {error && <div className="text-red-400 text-sm bg-red-900/20 p-2 rounded">{error}</div>}

        {response && (
          <Card className="bg-slate-700 border-slate-600 p-3">
            <pre className="text-xs text-slate-300 overflow-x-auto max-h-40">
              {JSON.stringify(response, null, 2)}
            </pre>
          </Card>
        )}
      </div>
    </div>
  );
}
