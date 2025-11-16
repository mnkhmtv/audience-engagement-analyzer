import { Card } from '@/components/ui/card';
import type { Analysis } from '@/types/index';

interface SuggestionsProps {
  analysis: Analysis;
}

export function Suggestions({ analysis }: SuggestionsProps) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <div className="p-6">
        <h2 className="text-xl font-bold text-white mb-4">Improvement Suggestions</h2>
        <ul className="space-y-3">
          {analysis.suggestions.map((suggestion, idx) => (
            <li key={idx} className="flex gap-3">
              <span className="text-blue-400 font-bold">•</span>
              <span className="text-slate-300">{suggestion}</span>
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
