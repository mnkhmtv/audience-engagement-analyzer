'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card } from '@/components/ui/card';
import type { Analysis } from '@/types/index';

interface EmotionChartProps {
  analysis: Analysis;
}

export function EmotionChart({ analysis }: EmotionChartProps) {
  const data = [
    { name: 'Happy', value: analysis.emotion_histogram.happy || 0 },
    { name: 'Sad', value: analysis.emotion_histogram.sad || 0 },
    { name: 'Neutral', value: analysis.emotion_histogram.neutral || 0 },
    { name: 'Angry', value: analysis.emotion_histogram.angry || 0 },
    { name: 'Surprise', value: analysis.emotion_histogram.surprise || 0 },
  ];

  return (
    <Card className="bg-slate-800 border-slate-700">
      <div className="p-6">
        <h2 className="text-xl font-bold text-white mb-6">Emotion Distribution</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '8px',
                color: '#e2e8f0',
              }}
            />
            <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
