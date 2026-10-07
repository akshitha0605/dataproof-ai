import React, { useEffect, useState } from 'react';
import { X, Sparkles, FileSpreadsheet, Loader2 } from 'lucide-react';
import { fetchDatasets } from '../services/api';

export default function SampleDatasetsModal({ onSelectSample, onClose }) {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDatasets()
      .then((data) => setDatasets(data || []))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl p-6 space-y-4 relative">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white bg-slate-100 dark:bg-slate-800 transition-all"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="space-y-1">
          <div className="flex items-center gap-2 text-base font-bold text-slate-900 dark:text-slate-100">
            <Sparkles className="w-5 h-5 text-cyan-500" />
            <span>Try Sample Datasets</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Select any raw data file to test the dynamic analysis pipeline.
          </p>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-400 flex flex-col items-center justify-center space-y-2">
            <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
            <span className="text-xs font-mono">Loading datasets...</span>
          </div>
        ) : datasets.length === 0 ? (
          <div className="p-6 text-center text-slate-400 text-xs">No sample datasets found.</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            {datasets.map((d) => (
              <div
                key={d.id}
                onClick={() => {
                  onSelectSample(d);
                  onClose();
                }}
                className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 hover:bg-slate-100 dark:hover:bg-slate-800/80 border border-slate-200 dark:border-slate-800 hover:border-cyan-500/50 cursor-pointer transition-all space-y-2 group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-cyan-600 dark:text-cyan-400 uppercase">
                    {d.file_type || 'CSV'}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {d.row_count?.toLocaleString()} rows
                  </span>
                </div>
                <div className="text-xs font-bold text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 truncate">
                  {d.file_name}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
