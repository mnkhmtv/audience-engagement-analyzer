'use client';

import { AnalysisSummary } from '@/types';
import { formatSeconds } from '@/lib/utils';

interface NarrativeSummaryProps {
  summary: AnalysisSummary;
}

export default function NarrativeSummary({ summary }: NarrativeSummaryProps) {
  const peak = summary.top_peaks?.[0];
  const dip = summary.top_dips?.[0];

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white">Engagement story</h3>
        <p className="text-slate-400 text-sm">
          A plain-language recap of how students reacted throughout the session.
        </p>
      </div>

      <p className="text-slate-200 leading-relaxed">
        Average engagement held at{' '}
        <span className="font-semibold text-white">{toPercent(summary.avg_engagement)}</span>, with attention close
        to{' '}
        <span className="font-semibold text-white">{toPercent(summary.avg_attention)}</span>. The combined quality score
        for this lecture is{' '}
        <span className="font-semibold text-white">{toPercent(summary.score)}</span>.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {peak && (
          <NarrativeCallout
            title="What resonated"
            tone="positive"
            timestamp={formatSeconds(peak.ts_sec)}
            description={peak.label}
          />
        )}
        {dip && (
          <NarrativeCallout
            title="Needs attention"
            tone="negative"
            timestamp={formatSeconds(dip.ts_sec)}
            description={dip.label}
          />
        )}
      </div>
    </div>
  );
}

function NarrativeCallout({
  title,
  tone,
  timestamp,
  description,
}: {
  title: string;
  tone: 'positive' | 'negative';
  timestamp: string;
  description: string;
}) {
  const toneClasses =
    tone === 'positive'
      ? 'border-green-500/40 bg-green-500/5 text-green-200'
      : 'border-red-500/40 bg-red-500/5 text-red-200';

  return (
    <div className={`rounded-lg border px-4 py-3 ${toneClasses}`}>
      <p className="text-xs uppercase tracking-wide opacity-80">{title}</p>
      <p className="text-sm font-semibold">{timestamp}</p>
      <p className="text-sm opacity-80">{description}</p>
    </div>
  );
}

function toPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}
