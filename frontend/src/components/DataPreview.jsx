import React, { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight, Loader2, Table } from 'lucide-react';
import { fetchDatasetPreview } from '../services/api';

export default function DataPreview({ datasetId, activeSheet, onClose }) {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPreview(page, search);
  }, [datasetId, page, activeSheet]);

  const loadPreview = async (p, q) => {
    setLoading(true);
    try {
      const res = await fetchDatasetPreview(datasetId, p, 15, q, activeSheet);
      setData(res);
      setError(null);
    } catch (err) {
      setError(err.message);
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
    <div className="space-y-4 glass-panel p-6 rounded-2xl border border-slate-800">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <Table className="w-5 h-5 text-cyan-400" />
          <h3 className="text-base font-bold text-slate-100">Live Dataset Records Preview</h3>
          {data && <span className="text-xs text-slate-400">({data.total_rows.toLocaleString()} total rows)</span>}
        </div>

        <form onSubmit={handleSearchSubmit} className="relative min-w-[240px]">
          <input
            type="text"
            placeholder="Search records..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg py-1.5 pl-8 pr-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
        </form>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12 text-slate-400 text-xs gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
          <span>Fetching dataset rows...</span>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-red-950/50 border border-red-500/40 text-red-300 text-xs">
          {error}
        </div>
      ) : data && data.rows.length > 0 ? (
        <div className="space-y-4">
          <div className="overflow-x-auto max-h-96 rounded-xl border border-slate-800">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/90 text-slate-400 uppercase font-semibold text-[10px] sticky top-0 border-b border-slate-800">
                <tr>
                  <th className="px-3 py-2 w-12 text-slate-600">#</th>
                  {data.columns.map((col) => (
                    <th key={col} className="px-3 py-2 whitespace-nowrap">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                {data.rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-900/40">
                    <td className="px-3 py-2 text-slate-600 font-sans">{(page - 1) * 15 + idx + 1}</td>
                    {data.columns.map((col) => (
                      <td key={col} className="px-3 py-2 whitespace-nowrap max-w-xs truncate" title={String(row[col] ?? '')}>
                        {row[col] === null || row[col] === undefined ? (
                          <span className="text-slate-600 italic">null</span>
                        ) : (
                          String(row[col])
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination bar */}
          <div className="flex items-center justify-between text-xs text-slate-400">
            <div>
              Page <span className="font-bold text-slate-200">{data.page}</span> of <span className="font-bold text-slate-200">{data.total_pages}</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                disabled={page >= data.total_pages}
                onClick={() => setPage(page + 1)}
                className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-slate-500 text-xs">No records found matching search query.</div>
      )}
    </div>
  );
}
