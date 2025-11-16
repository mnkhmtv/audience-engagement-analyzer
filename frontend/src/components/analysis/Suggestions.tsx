'use client';

interface SuggestionsProps {
  suggestions: string[];
}

export default function Suggestions({ suggestions }: SuggestionsProps) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Suggestions for Improvement</h3>
      <ul className="space-y-3">
        {suggestions.map((suggestion, idx) => (
          <li key={idx} className="flex gap-3">
            <span className="text-blue-400 font-bold flex-shrink-0">•</span>
            <span className="text-slate-300">{suggestion}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
