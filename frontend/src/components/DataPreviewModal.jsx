import React, { useState, useEffect } from 'react';
import { X, Table, Search, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { fetchDatasetPreview } from '../services/api';

export default function DataPreviewModal({ datasetId, fileName, onClose }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPreview(page, search);
  }, [datasetId, page]);

  const loadPreview = async (pageNum, searchStr) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchDatasetPreview(datasetId, pageNum, 15, searchStr);
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to fetch preview.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadPreview(1, search);
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl p-5 sm:p-6 space-y-4 max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Table className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
              Data Preview — <span className="font-mono text-cyan-600 dark:text-cyan-400">{fileName}</span>
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white bg-slate-100 dark:bg-slate-800 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search bar */}
        <div className="flex items-center justify-between gap-3">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-sm">
            <input
              type="text"
              placeholder="Search table values..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl py-1.5 pl-8 pr-3 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500"
            />
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
          </form>

          {data && (
            <div className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              Total: {data.total_rows?.toLocaleString()} rows
            </div>
          )}
        </div>

        {/* Table Body */}
        <div className="flex-1 overflow-auto border border-slate-200 dark:border-slate-800 rounded-xl">
          {loading ? (
            <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center space-y-2">
              <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
              <span className="text-xs font-mono">Loading data preview...</span>
            </div>
          ) : error ? (
            <div className="p-6 text-center text-rose-500 text-xs font-medium">{error}</div>
          ) : data && data.rows && data.rows.length > 0 ? (
            <table className="w-full text-left text-xs text-slate-800 dark:text-slate-200">
              <thead className="bg-slate-100 dark:bg-slate-950 text-slate-500 dark:text-slate-400 uppercase font-semibold text-[10px] sticky top-0 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-3 py-2.5 w-10 text-slate-400">#</th>
                  {data.columns.map((col) => (
                    <th key={col} className="px-3 py-2.5 whitespace-nowrap">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/80 font-mono text-[11px]">
                {data.rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                    <td className="px-3 py-2 text-slate-400 font-sans font-medium">
                      {(page - 1) * 15 + idx + 1}
                    </td>
                    {data.columns.map((col) => (
                      <td key={col} className="px-3 py-2 whitespace-nowrap max-w-xs truncate" title={String(row[col] ?? '')}>
                        {row[col] === null || row[col] === undefined ? (
                          <span className="text-slate-400 italic">null</span>
                        ) : typeof row[col] === 'number' ? (
                          <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{Number(row[col]).toLocaleString()}</span>
                        ) : (
                          String(row[col])
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-400 text-xs">No records found.</div>
          )}
        </div>

        {/* Pagination Footer */}
        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between pt-2">
            <div className="text-xs text-slate-500 dark:text-slate-400 font-mono">
              Page {data.page} of {data.total_pages}
            </div>

            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1 || loading}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-lg border border-slate-300 dark:border-slate-800 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-40 transition-all"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= data.total_pages || loading}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded-lg border border-slate-300 dark:border-slate-800 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-40 transition-all"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
