import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, X, Eye, Loader2, Table } from 'lucide-react';
import { uploadDatasetFile } from '../services/api';

export default function FileUpload({ dataset, onDatasetUploaded, onResetDataset, onTogglePreview }) {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;
    const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    const allowed = ['.csv', '.xlsx', '.xls', '.json', '.tsv'];
    
    if (!allowed.includes(ext)) {
      setError("This file type isn't supported. Please upload CSV, Excel, JSON or TSV.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const profile = await uploadDatasetFile(file);
      onDatasetUploaded(profile);
    } catch (err) {
      setError(err.message || "We couldn't read this file. Please check the file and try again.");
    } finally {
      setLoading(false);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  // If a dataset is already uploaded
  if (dataset) {
    return (
      <div className="w-full bg-slate-900/60 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-5 transition-all">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-500 dark:text-emerald-400">
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <div className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                ✓ {dataset.file_name}
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-mono mt-0.5">
                {dataset.file_type || 'DATA'} • {dataset.row_count?.toLocaleString()} rows
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onTogglePreview}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-all"
            >
              <Eye className="w-3.5 h-3.5 text-cyan-500" />
              <span>Preview data</span>
            </button>

            <button
              onClick={onResetDataset}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-rose-500/10 hover:text-rose-600 dark:hover:text-rose-400 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700 transition-all"
              title="Change file"
            >
              <X className="w-3.5 h-3.5" />
              <span>Change file</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // File Upload Drop Area
  return (
    <div className="w-full space-y-3">
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer border-2 border-dashed rounded-2xl p-8 sm:p-10 text-center transition-all duration-200 ${
          isDragging
            ? 'border-cyan-500 bg-cyan-500/10 scale-[1.01]'
            : 'border-slate-300 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-600 bg-white/50 dark:bg-slate-900/40 hover:bg-slate-50 dark:hover:bg-slate-900/80'
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".csv,.xlsx,.xls,.json,.tsv"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="p-4 rounded-2xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
            {loading ? (
              <Loader2 className="w-8 h-8 animate-spin" />
            ) : (
              <Upload className="w-8 h-8" />
            )}
          </div>

          <div className="space-y-1">
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
              {loading ? 'Reading dataset...' : 'Drop your file here'}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              or <span className="text-cyan-600 dark:text-cyan-400 font-semibold underline underline-offset-2">browse files</span>
            </p>
          </div>

          <div className="pt-2 text-[11px] font-medium text-slate-400 dark:text-slate-500 font-mono tracking-wider uppercase">
            CSV • Excel • JSON • TSV
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 text-xs font-medium text-center">
          {error}
        </div>
      )}
    </div>
  );
}
