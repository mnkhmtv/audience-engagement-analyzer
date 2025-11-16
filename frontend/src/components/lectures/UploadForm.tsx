'use client';

import { useRouter } from 'next/navigation';
import { FormEvent, useEffect, useState } from 'react';
import { lecturesApi } from '@/api/lectures';

export function UploadForm() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleFileChange = (file: File | null) => {
    setVideoFile(file);
    setError('');
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (file) {
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!videoFile) {
      setError('Please choose a video file');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('title', title);
      if (subject) formData.append('subject', subject);
      formData.append('file', videoFile);
      const { data } = await lecturesApi.upload(formData);
      router.push(`/lectures/${data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed, please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Upload a lecture</h1>
        <p className="text-slate-400 mb-8">We&apos;ll analyze engagement and emotions in a few minutes.</p>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div>
            <label className="block text-slate-300 mb-2 text-sm font-medium">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              placeholder="Keynote presentation"
            />
          </div>

          <div>
            <label className="block text-slate-300 mb-2 text-sm font-medium">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              placeholder="Optional context"
            />
          </div>

          <div>
            <label className="block text-slate-300 mb-2 text-sm font-medium">Video file</label>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              className="w-full text-white text-sm"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold rounded-lg transition"
          >
            {loading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
        </form>
      </div>

      <div className="w-full">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-4">
          <h2 className="text-white font-semibold mb-3">Preview</h2>
          {previewUrl ? (
            <video controls className="w-full rounded-lg border border-slate-700" src={previewUrl} />
          ) : (
            <div className="aspect-video border border-dashed border-slate-600 rounded-lg flex items-center justify-center text-slate-500">
              Select a video to see a preview here
            </div>
          )}
          <p className="text-xs text-slate-500 mt-3">
            We securely store the original video in your Docker volume under <code>artifacts/videos</code>.
            Analysis reports will be attached to the lecture automatically.
          </p>
        </div>
      </div>
    </div>
  );
}

export default UploadForm;
