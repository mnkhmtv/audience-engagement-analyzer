'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { uploadLecture } from '@/api/lectures';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

function UploadFormComponent() {
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const { token } = useAuth();
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type.startsWith('video/')) {
        setFile(selectedFile);
        setError('');
      } else {
        setError('Please select a valid video file');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title || !subject || !file) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      const lectureId = await uploadLecture(token!, { title, subject, video: file }, (prog) =>
        setProgress(prog),
      );
      router.push(`/lectures/${lectureId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="mb-6 text-slate-400 hover:text-white"
        >
          ← Back
        </Button>

        <Card className="bg-slate-800 border-slate-700">
          <div className="p-6 space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-white">Upload Lecture</h1>
              <p className="text-slate-400 mt-2">Add a new lecture video for analysis</p>
            </div>

            {error && (
              <Alert variant="destructive" className="bg-red-900/20 border-red-900 text-red-400">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-2">Title</label>
                <Input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Introduction to Machine Learning"
                  className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-200 mb-2">Subject</label>
                <Input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g., Computer Science"
                  className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-200 mb-2">Video File</label>
                <Input
                  type="file"
                  accept="video/*"
                  onChange={handleFileChange}
                  className="bg-slate-700 border-slate-600 text-slate-400 file:bg-blue-600 file:text-white file:border-0 file:px-4 file:py-2"
                  required
                />
                {file && <p className="text-sm text-slate-400 mt-2">Selected: {file.name}</p>}
              </div>

              {progress > 0 && progress < 100 && (
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2"
              >
                {loading ? `Uploading... ${progress}%` : 'Upload Lecture'}
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </div>
  );
}

export { UploadFormComponent as UploadForm };
