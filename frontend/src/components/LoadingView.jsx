import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';

const STATUS_STEPS = [
  'Understanding data...',
  'Generating analysis...',
  'Verifying result...'
];

export default function LoadingView() {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setStepIndex(1), 1200);
    const timer2 = setTimeout(() => setStepIndex(2), 2600);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, []);

  return (
    <div className="w-full bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 text-center space-y-4 shadow-sm transition-all">
      <div className="flex justify-center">
        <div className="p-3.5 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
          <Loader2 className="w-7 h-7 animate-spin" />
        </div>
      </div>

      <div className="space-y-1.5">
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
          Analyzing your data...
        </h3>
        <p className="text-xs font-mono text-cyan-600 dark:text-cyan-400 font-medium transition-all duration-300">
          {STATUS_STEPS[stepIndex]}
        </p>
      </div>

      {/* Subtle Progress Bar */}
      <div className="max-w-xs mx-auto h-1 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-cyan-500 transition-all duration-700 ease-out rounded-full"
          style={{ width: `${((stepIndex + 1) / STATUS_STEPS.length) * 100}%` }}
        />
      </div>
    </div>
  );
}
