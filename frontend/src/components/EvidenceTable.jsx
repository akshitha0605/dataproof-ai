import React, { useState } from 'react';
import { Database, Search, Download } from 'lucide-react';

export default function EvidenceTable({ evidence }) {
  const [search, setSearch] = useState('');

  if (!evidence || !evidence.rows || evidence.rows.length === 0) {
    return null;
  }

  const columns = evidence.columns && evidence.columns.length > 0
    ? evidence.columns
    : Object.keys(evidence.rows[0]);

  const filteredRows = evidence.rows.filter((row) => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    return Object.values(row).some((val) => String(val ?? '').toLowerCase().includes(s));
  });

  const downloadCSV = () => {
    if (!filteredRows.length) return;
    const headers = columns.join(',');
    const rows = filteredRows.map((r) => columns.map((c) => JSON.stringify(r[c] ?? '')).join(','));
    const csvContent = [headers, ...rows].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'dataproof_evidence.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden space-y-3 p-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-emerald-400" />
          <h4 className="text-sm font-bold text-slate-100">Dataset Evidence (Source of Truth)</h4>
          <span className="text-xs text-slate-400 font-mono">({filteredRows.length} supporting rows)</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative min-w-[200px]">
            <input
              type="text"
              placeholder="Search evidence..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg py-1 pl-7 pr-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
            <Search className="w-3 h-3 text-slate-500 absolute left-2.5 top-2" />
          </div>

          <button
            onClick={downloadCSV}
            className="inline-flex items-center gap-1 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1 rounded-lg border border-slate-700 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      <div className="overflow-x-auto max-h-80 rounded-xl border border-slate-800">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/90 text-slate-400 uppercase font-semibold text-[10px] sticky top-0 border-b border-slate-800">
            <tr>
              <th className="px-3 py-2 w-10 text-slate-600">#</th>
              {columns.map((col) => (
                <th key={col} className="px-3 py-2 whitespace-nowrap">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
            {filteredRows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-900/40">
                <td className="px-3 py-2 text-slate-600 font-sans">{idx + 1}</td>
                {columns.map((col) => (
                  <td key={col} className="px-3 py-2 whitespace-nowrap max-w-xs truncate" title={String(row[col] ?? '')}>
                    {row[col] === null || row[col] === undefined ? (
                      <span className="text-slate-600 italic">null</span>
                    ) : typeof row[col] === 'number' ? (
                      <span className="text-emerald-400 font-bold">{Number(row[col]).toLocaleString()}</span>
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
    </div>
  );
}
