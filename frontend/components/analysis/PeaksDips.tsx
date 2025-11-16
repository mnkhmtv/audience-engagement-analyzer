import { Card } from '@/components/ui/card';
import type { Analysis } from '@/types/index';

interface PeaksDipsProps {
  analysis: Analysis;
}

export function PeaksDips({ analysis }: PeaksDipsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card className="bg-slate-800 border-slate-700">
        <div className="p-6">
          <h3 className="text-lg font-bold text-white mb-4">Peak Moments</h3>
          <div className="space-y-3">
            {analysis.top_peaks.map((peak, idx) => (
              <div key={idx} className="bg-slate-700 rounded p-3">
                <p className="text-sm text-slate-300">
                  {peak.timestamp} - <span className="text-green-400">{peak.metric}</span>
                </p>
                <p className="text-xs text-slate-400 mt-1">{peak.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <Card className="bg-slate-800 border-slate-700">
        <div className="p-6">
          <h3 className="text-lg font-bold text-white mb-4">Low Moments</h3>
          <div className="space-y-3">
            {analysis.top_dips.map((dip, idx) => (
              <div key={idx} className="bg-slate-700 rounded p-3">
                <p className="text-sm text-slate-300">
                  {dip.timestamp} - <span className="text-red-400">{dip.metric}</span>
                </p>
                <p className="text-xs text-slate-400 mt-1">{dip.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
