'use client';

import { TimelineHighlight } from '@/types';
import { formatSeconds } from '@/lib/utils';

type MarkerType = 'peak' | 'dip';

interface TimelineWithHighlightsProps {
  duration: number;
  peaks: TimelineHighlight[];
  dips: TimelineHighlight[];
  onSelect: (time: number) => void;
}

const typeStyles: Record<MarkerType, string> = {
  peak: 'bg-green-400 hover:bg-green-300',
  dip: 'bg-red-400 hover:bg-red-300',
};

export function TimelineWithHighlights({
  duration,
  peaks,
  dips,
  onSelect,
}: TimelineWithHighlightsProps) {
  const safeDuration = duration > 0 ? duration : 1;

  const markers = [
    ...peaks.map((peak) => ({ ...peak, type: 'peak' as MarkerType })),
    ...dips.map((dip) => ({ ...dip, type: 'dip' as MarkerType })),
  ].sort((a, b) => a.ts_sec - b.ts_sec);

  return (
    <div className="space-y-3">
      <div className="text-sm font-semibold text-white">Timeline highlights</div>
      <div className="relative h-2 w-full rounded-full bg-slate-700">
        {markers.map((marker, idx) => {
          const left = Math.min(100, (marker.ts_sec / safeDuration) * 100);
          return (
            <button
              key={`${marker.type}-${idx}-${marker.ts_sec}`}
              type="button"
              className={`absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/70 ${typeStyles[marker.type]}`}
              style={{ left: `${left}%` }}
              title={`${marker.label} - ${formatSeconds(marker.ts_sec)}`}
              onClick={() => onSelect(marker.ts_sec)}
            />
          );
        })}
      </div>
      <div className="flex justify-between text-xs text-slate-400">
        <span>0:00</span>
        <span>{formatSeconds(safeDuration)}</span>
      </div>
      <div className="flex gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-green-400" />
          High engagement
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-red-400" />
          Needs attention
        </div>
      </div>
    </div>
  );
}

export default TimelineWithHighlights;
