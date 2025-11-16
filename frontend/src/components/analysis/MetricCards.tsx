'use client';

interface MetricCardsProps {
  avgAttention: number;
  avgEngagement: number;
  score: number;
}

export function MetricCards({
  avgAttention,
  avgEngagement,
  score,
}: MetricCardsProps) {
  const metrics = [
    {
      label: 'Average Attention',
      value: (avgAttention * 100).toFixed(1),
      unit: '%',
      color: 'blue',
    },
    {
      label: 'Average Engagement',
      value: (avgEngagement * 100).toFixed(1),
      unit: '%',
      color: 'green',
    },
    {
      label: 'Overall Score',
      value: (score * 100).toFixed(1),
      unit: '%',
      color: 'purple',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-900 border-blue-700 text-blue-300',
    green: 'bg-green-900 border-green-700 text-green-300',
    purple: 'bg-purple-900 border-purple-700 text-purple-300',
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className={`${colorClasses[metric.color as keyof typeof colorClasses]} border rounded-xl p-6`}
        >
          <p className="text-sm font-medium opacity-75 mb-2">{metric.label}</p>
          <div className="flex items-baseline gap-1">
            <span className="text-4xl font-bold">{metric.value}</span>
            <span className="text-xl opacity-75">{metric.unit}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default MetricCards;
