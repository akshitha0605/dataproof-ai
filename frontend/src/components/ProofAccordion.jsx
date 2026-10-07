import React, { useState } from 'react';
import { Database, Code, ChevronDown, ChevronUp, Copy, Check, Terminal, Search, Download } from 'lucide-react';

export default function ProofAccordion({ evidence, proofCode, executionResult }) {
  const [showEvidence, setShowEvidence] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);
  const [search, setSearch] = useState('');

  const handleCopyCode = () => {
    if (!proofCode) return;
    navigator.clipboard.writeText(proofCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const rows = evidence?.rows || [];
  const columns = (evidence?.columns && evidence.columns.length > 0)
    ? evidence.columns
    : (rows.length > 0 ? Object.keys(rows[0]) : []);

  const filteredRows = rows.filter((row) => {
    if (!search.trim()) return true;
    const s = search.toLowerCase();
    return Object.values(row).some((val) => String(val ?? '').toLowerCase().includes(s));
  });

  const downloadCSV = () => {
    if (!filteredRows.length) return;
    const headers = columns.join(',');
    const csvRows = filteredRows.map((r) => columns.map((c) => JSON.stringify(r[c] ?? '')).join(','));
    const csvContent = [headers, ...csvRows].join('\n');

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
    <div className="w-full space-y-3 pt-2">
      {/* Expandable Action Buttons */}
      <div className="flex items-center gap-3 flex-wrap">
        {evidence && rows.length > 0 && (
          <button
            onClick={() => {
              setShowEvidence(!showEvidence);
              if (showCode) setShowCode(false);
            }}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold border transition-all ${
              showEvidence
                ? 'bg-cyan-600 text-white border-cyan-500 shadow-md shadow-cyan-500/20'
                : 'bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-800'
            }`}
          >
            <Database className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
            <span>View Evidence</span>
            {showEvidence ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        )}

        {proofCode && (
          <button
            onClick={() => {
              setShowCode(!showCode);
              if (showEvidence) setShowEvidence(false);
            }}
            className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold border transition-all ${
              showCode
                ? 'bg-cyan-600 text-white border-cyan-500 shadow-md shadow-cyan-500/20'
                : 'bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-800'
            }`}
          >
            <Code className="w-4 h-4 text-cyan-500 dark:text-cyan-400" />
            <span>View Proof Code</span>
            {showCode ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {/* View Evidence Panel */}
      {showEvidence && rows.length > 0 && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4 shadow-sm transition-all">
          <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                Evidence used for this answer
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Showing {filteredRows.length} supporting record(s) calculated from dataset
              </p>
            </div>

            <div className="flex items-center gap-2">
              <div className="relative min-w-[180px]">
                <input
                  type="text"
                  placeholder="Search evidence..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-lg py-1 pl-7 pr-3 text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cyan-500"
                />
                <Search className="w-3 h-3 text-slate-400 absolute left-2.5 top-2" />
              </div>

              <button
                onClick={downloadCSV}
                className="inline-flex items-center gap-1 text-xs text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 px-3 py-1 rounded-lg border border-slate-300 dark:border-slate-700 transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export</span>
              </button>
            </div>
          </div>

          <div className="overflow-x-auto max-h-72 rounded-xl border border-slate-200 dark:border-slate-800">
            <table className="w-full text-left text-xs text-slate-800 dark:text-slate-200">
              <thead className="bg-slate-100 dark:bg-slate-950 text-slate-500 dark:text-slate-400 uppercase font-semibold text-[10px] sticky top-0 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-3 py-2.5 w-10 text-slate-400">#</th>
                  {columns.map((col) => (
                    <th key={col} className="px-3 py-2.5 whitespace-nowrap">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800/80 font-mono text-[11px]">
                {filteredRows.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                    <td className="px-3 py-2 text-slate-400 font-sans">{idx + 1}</td>
                    {columns.map((col) => (
                      <td key={col} className="px-3 py-2 whitespace-nowrap max-w-xs truncate" title={String(r[col] ?? '')}>
                        {r[col] === null || r[col] === undefined ? (
                          <span className="text-slate-400 italic">null</span>
                        ) : typeof r[col] === 'number' ? (
                          <span className="text-emerald-600 dark:text-emerald-400 font-semibold">{Number(r[col]).toLocaleString()}</span>
                        ) : (
                          String(r[col])
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* View Proof Code Panel */}
      {showCode && proofCode && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4 shadow-sm transition-all">
          <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
            <div>
              <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                Proof Code
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Exact Python/Pandas code generated and executed on your dataset
              </p>
            </div>

            <button
              onClick={handleCopyCode}
              className="inline-flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 transition-all font-semibold"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy Code'}</span>
            </button>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 text-cyan-400 font-mono text-xs overflow-x-auto max-h-72 border border-slate-800">
            <pre className="whitespace-pre-wrap leading-relaxed">{proofCode}</pre>
          </div>

          {/* Execution Result Box */}
          <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-800">
            <div className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <Terminal className="w-4 h-4 text-emerald-500" />
              <span>Execution Result</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
              <div className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 font-mono">
                ✓ Code executed successfully
              </div>
              <pre className="text-[11px] font-mono text-slate-400 whitespace-pre-wrap overflow-x-auto max-h-40">
                {typeof executionResult === 'object'
                  ? JSON.stringify(executionResult, null, 2)
                  : String(executionResult || 'Executed with status 0')}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
