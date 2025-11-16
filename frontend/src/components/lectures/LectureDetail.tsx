'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import client from '@/api/client';
import { lecturesApi } from '@/api/lectures';
import { Lecture, AnalysisData, AnalysisSummary } from '@/types';
import { usePolling } from '@/hooks/usePolling';
import MetricCards from '@/components/analysis/MetricCards';
import EmotionChart from '@/components/analysis/EmotionChart';
import Suggestions from '@/components/analysis/Suggestions';
import TimelineWithHighlights from '@/components/analysis/TimelineWithHighlights';
import PeaksDips from '@/components/analysis/PeaksDips';
import NarrativeSummary from '@/components/analysis/NarrativeSummary';
import { formatSeconds } from '@/lib/utils';

interface LectureDetailProps {
  lectureId: string;
}

export function LectureDetail({ lectureId }: LectureDetailProps) {
  const [lecture, setLecture] = useState<Lecture | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [videoDuration, setVideoDuration] = useState<number | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const fetchLectureData = useCallback(async () => {
    try {
      const [lectureRes, analysisRes] = await Promise.all([
        lecturesApi.getById(lectureId),
        lecturesApi.getAnalysis(lectureId).catch(() => ({ data: null })),
      ]);

      const lectureData = lectureRes.data;
      const analysisPayload = analysisRes.data || lectureData.analysis || null;

      setLecture(lectureData);
      if (analysisPayload) {
        setAnalysis(analysisPayload);
      }
      setError('');
      const waitingStatuses = new Set(['pending', 'processing']);
      const stillWaiting = waitingStatuses.has(lectureData.status) || !analysisPayload;
      return stillWaiting;
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Lecture not found or already removed.');
      } else {
        setError(err.response?.data?.detail || 'Failed to load lecture.');
      }
      return false;
    } finally {
      setLoading(false);
    }
  }, [lectureId]);

  useEffect(() => {
    fetchLectureData();
  }, [fetchLectureData]);

  const shouldPoll = !analysis && lecture?.status !== 'error';
  usePolling(fetchLectureData, 3000, shouldPoll);

  useEffect(() => {
    let revokeUrl: string | null = null;
    const loadVideo = async () => {
      if (!lecture?.video_url) {
        setVideoSrc(null);
        return;
      }
      try {
        const response = await client.get<Blob>(lecture.video_url, { responseType: 'blob' });
        revokeUrl = URL.createObjectURL(response.data);
        setVideoSrc(revokeUrl);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Unable to load lecture video.');
      }
    };
    loadVideo();
    return () => {
      if (revokeUrl) {
        URL.revokeObjectURL(revokeUrl);
      }
    };
  }, [lecture?.video_url]);

  const summary: AnalysisSummary | null = useMemo(() => {
    if (!analysis?.summary_json) return null;
    if (typeof analysis.summary_json === 'object') return analysis.summary_json;
    try {
      return JSON.parse(analysis.summary_json);
    } catch {
      return null;
    }
  }, [analysis]);
  const metrics = summary ?? analysis;

  const handleSeek = (time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      videoRef.current.focus();
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12 text-slate-400">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mb-4" />
        Loading lecture...
      </div>
    );
  }

  if (error || !lecture) {
    return (
      <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg">
        {error || 'Lecture not found'}
      </div>
    );
  }

  const isProcessing = lecture.status === 'processing' || lecture.status === 'pending';

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">{lecture.title}</h1>
        <p className="text-slate-400">{lecture.subject || 'No subject provided'}</p>
        <div className="text-slate-500 text-sm mt-1">
          Uploaded on {new Date(lecture.created_at).toLocaleString()}
        </div>
        {isProcessing && (
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-yellow-900 text-yellow-200 rounded-lg">
            <span className="inline-block h-2 w-2 rounded-full bg-yellow-200 animate-pulse" aria-hidden="true" />
            Analysis running... we refresh results every 3 seconds.
          </div>
        )}

      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[2fr,3fr] gap-8">
        <div className="space-y-4">
          <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
            {videoSrc ? (
              <video
                ref={videoRef}
                className="w-full aspect-video bg-black"
                src={videoSrc}
                controls
                onLoadedMetadata={(event) => setVideoDuration(event.currentTarget.duration)}
              />
            ) : (
              <div className="aspect-video flex items-center justify-center text-slate-400">
                Video is not ready yet.
              </div>
            )}
          </div>

          {summary && (
            <TimelineHighlightsSection
              summary={summary}
              videoDuration={videoDuration}
              onSeek={handleSeek}
            />
          )}
        </div>

        <div className="space-y-6">
          {metrics ? (
            <>
              <MetricCards
                avgAttention={metrics.avg_attention}
                avgEngagement={metrics.avg_engagement}
                score={metrics.score}
              />
              {summary ? (
                <>
                  <NarrativeSummary summary={summary} />
                  <EmotionChart emotions={summary.emotion_hist} />
                  <PeaksDips topPeaks={summary.top_peaks} topDips={summary.top_dips} />
                  <Suggestions suggestions={summary.suggestions} />
                </>
              ) : (
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 text-center text-slate-400">
                  We&apos;ve crunched the base metrics and are generating highlight narratives now. This will refresh
                  automatically.
                </div>
              )}
            </>
          ) : (
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 text-center text-slate-400">
              We&apos;re still analyzing this lecture. Hang tight!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default LectureDetail;

function TimelineHighlightsSection({
  summary,
  videoDuration,
  onSeek,
}: {
  summary: AnalysisSummary;
  videoDuration: number | null;
  onSeek: (time: number) => void;
}) {
  const highlightTimes = [...summary.top_peaks, ...summary.top_dips].map((item) => item.ts_sec);
  const derivedDuration = videoDuration ?? Math.max(...highlightTimes, 1);

  return (
    <TimelineWithHighlights
      duration={derivedDuration}
      peaks={summary.top_peaks}
      dips={summary.top_dips}
      onSelect={onSeek}
    />
  );
}
