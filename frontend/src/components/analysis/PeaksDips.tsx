'use client';

import { TimelineHighlight } from '@/types';
import { formatSeconds } from '@/lib/utils';

interface PeaksDipsProps {
  topPeaks: TimelineHighlight[];
  topDips: TimelineHighlight[];
}

const HighlightList = ({
  items,
  accent,
}: {
  items: TimelineHighlight[];
  accent: 'green' | 'red';
}) => (
  <div className="space-y-3">
    {items.map((item, idx) => (
      <div
        key={`${item.ts_sec}-${idx}`}
        className="flex items-center justify-between p-3 bg-slate-700 rounded-lg"
      >
        <div>
          <p className="text-slate-300 text-sm">{item.label}</p>
          <p className="text-slate-500 text-xs">{formatSeconds(item.ts_sec)}</p>
        </div>
        <span
          className={`font-semibold ${
            accent === 'green' ? 'text-green-400' : 'text-red-400'
          }`}
        >
          {(item.engagement_ratio * 100).toFixed(0)}%
        </span>
      </div>
    ))}
  </div>
);

export default function PeaksDips({ topPeaks, topDips }: PeaksDipsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span className="inline-block h-2 w-2 rounded-full bg-green-400" aria-hidden="true" /> Peak moments
        </h3>
        <HighlightList items={topPeaks} accent="green" />
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <span className="inline-block h-2 w-2 rounded-full bg-red-400" aria-hidden="true" /> Engagement dips
        </h3>
        <HighlightList items={topDips} accent="red" />
      </div>
    </div>
  );
}
