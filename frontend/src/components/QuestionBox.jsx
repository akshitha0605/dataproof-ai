import React, { useState } from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';

export default function QuestionBox({ onAnalyze, loading }) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;
    onAnalyze(question.trim());
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-3">
      <div className="space-y-1">
        <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
          Ask anything about your data
        </label>
        
        <div className="relative flex items-center">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Which category has the highest value?"
            rows={2}
            className="w-full bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 rounded-2xl py-3.5 pl-4 pr-32 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-cyan-500 dark:focus:border-cyan-500 transition-all resize-none shadow-sm"
          />

          <button
            type="submit"
            disabled={!question.trim() || loading}
            className="absolute right-3 bottom-3 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 transition-all disabled:opacity-40 disabled:hover:bg-cyan-600 shadow-md shadow-cyan-500/10"
          >
            <span>Analyze</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </form>
  );
}
