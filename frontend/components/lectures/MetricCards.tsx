import { Card } from '@/components/ui/card';
import type { Analysis } from '@/types/index';

interface MetricCardsProps {
  analysis: Analysis;
}

export function MetricCards({ analysis }: MetricCardsProps) {
  const metrics = [
    { label: 'Attention', value: analysis.avg_attention, unit: '%' },
    { label: 'Engagement', value: analysis.avg_engagement, unit: '%' },
    { label: 'Score', value: analysis.score, unit: '/100' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {metrics.map((metric) => (
        <Card key={metric.label} className="bg-slate-800 border-slate-700">
          <div className="p-6">
            <p className="text-slate-400 text-sm mb-2">{metric.label}</p>
            <p className="text-3xl font-bold text-white">
              {metric.value.toFixed(1)}
              <span className="text-lg text-slate-400">{metric.unit}</span>
            </p>
          </div>
        </Card>
      ))}
    </div>
  );
}
