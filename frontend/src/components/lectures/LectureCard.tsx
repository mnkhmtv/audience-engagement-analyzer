'use client';

import Link from 'next/link';
import { Lecture, LectureStatus, AnalysisSummary } from '@/types';
import { formatSeconds } from '@/lib/utils';

interface LectureCardProps {
  lecture: Lecture;
}

const statusLabels: Record<LectureStatus, string> = {
  pending: 'Queued',
  processing: 'Analyzing',
  done: 'Ready',
  error: 'Failed',
};

const statusColors: Record<LectureStatus, string> = {
  pending: 'bg-slate-600 text-white',
  processing: 'bg-yellow-900 text-yellow-200',
  done: 'bg-green-900 text-green-200',
  error: 'bg-red-900 text-red-200',
};

function percentage(value?: number | null) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—';
  }
  return `${Math.round(value * 100)}%`;
}

function parseSummary(summary: Lecture['analysis']): AnalysisSummary | null {
  const payload = summary?.summary_json;
  if (!payload) return null;
  if (typeof payload === 'object') {
    return payload as AnalysisSummary;
  }
  try {
    return JSON.parse(payload) as AnalysisSummary;
  } catch {
    return null;
  }
}

function AnalysisSnapshot({ lecture }: { lecture: Lecture }) {
  if (!lecture.analysis) {
    return (
      <p className="mt-4 text-sm text-slate-500">
        We&apos;re still crunching the numbers for this upload. The detail page will refresh automatically
        once analysis completes.
      </p>
    );
  }

  const summary = parseSummary(lecture.analysis);
  const peak = summary?.top_peaks?.[0];
  const dip = summary?.top_dips?.[0];

  return (
    <div className="mt-6 space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <Stat label="Engagement" value={percentage(lecture.analysis.avg_engagement)} accent="text-green-300" />
        <Stat label="Attention" value={percentage(lecture.analysis.avg_attention)} accent="text-amber-300" />
        <Stat label="Score" value={percentage(lecture.analysis.score)} accent="text-blue-300" />
      </div>

      {summary ? (
        <div className="bg-slate-700/60 rounded-lg p-3 text-sm text-slate-300 leading-relaxed">
          <p>
            Your audience stayed engaged at <span className="text-white font-semibold">{percentage(summary.avg_engagement)}</span>{' '}
            on average, while attention hovered near{' '}
            <span className="text-white font-semibold">{percentage(summary.avg_attention)}</span>. Overall score:{' '}
            <span className="text-white font-semibold">{percentage(summary.score)}</span>.
          </p>
          {peak && (
            <p className="mt-2 text-green-300">
              Peak around {formatSeconds(peak.ts_sec)} — {peak.label}
            </p>
          )}
          {dip && (
            <p className="text-red-300">
              Watch for a drop close to {formatSeconds(dip.ts_sec)} — {dip.label}
            </p>
          )}
        </div>
      ) : (
        <p className="text-xs text-slate-500">Detailed highlights will appear as soon as we finish processing.</p>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <div className="rounded-lg bg-slate-800/80 border border-slate-700/80 px-3 py-2">
      <div className="text-xs uppercase tracking-wide text-slate-400">{label}</div>
      <div className={`text-lg font-semibold ${accent}`}>{value}</div>
    </div>
  );
}

export function LectureCard({ lecture }: LectureCardProps) {
  const createdAt = new Date(lecture.created_at).toLocaleString();

  return (
    <Link href={`/lectures/${lecture.id}`} className="block group">
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-lg transition hover:border-blue-500 hover:-translate-y-1">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition">
              {lecture.title}
            </h3>
            <p className="text-slate-400 text-sm">{lecture.subject || 'Untitled topic'}</p>
          </div>
          <span className={`px-3 py-1 text-xs font-semibold rounded-full ${statusColors[lecture.status]}`}>
            {statusLabels[lecture.status]}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
          <div>
            Created&nbsp;
            <span className="text-white">{createdAt}</span>
          </div>
          <div>
            Progress&nbsp;
            <span className="text-white">{lecture.progress}%</span>
          </div>
          {lecture.error_message && lecture.status === 'error' && (
            <div className="text-red-400 truncate max-w-full">Error: {lecture.error_message}</div>
          )}
        </div>

        <AnalysisSnapshot lecture={lecture} />
      </div>
    </Link>
  );
}

export default LectureCard;
