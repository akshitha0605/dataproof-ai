import React, { useState } from 'react';
import { Code, Copy, Check, Terminal, Eye } from 'lucide-react';

export default function ProofViewer({ code, executionResult }) {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('code'); // 'code' or 'output'

  const handleCopy = () => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
      {/* Header bar */}
      <div className="p-4 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 font-semibold text-xs text-slate-200">
            <Code className="w-4 h-4 text-cyan-400" />
            <span>Executable Proof Code</span>
          </div>

          <div className="flex bg-slate-950 p-0.5 rounded-lg border border-slate-800 text-[11px]">
            <button
              onClick={() => setActiveTab('code')}
              className={`px-3 py-1 rounded-md transition-all ${
                activeTab === 'code' ? 'bg-cyan-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Python Pandas Code
            </button>
            <button
              onClick={() => setActiveTab('output')}
              className={`px-3 py-1 rounded-md transition-all ${
                activeTab === 'output' ? 'bg-cyan-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Raw Execution Output
            </button>
          </div>
        </div>

        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition-all"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied!' : 'Copy Code'}</span>
        </button>
      </div>

      {/* Code tab */}
      {activeTab === 'code' ? (
        <div className="p-4 bg-slate-950 font-mono text-xs text-cyan-300 overflow-x-auto max-h-96">
          <pre className="whitespace-pre-wrap leading-relaxed">{code || '# No execution code generated'}</pre>
        </div>
      ) : (
        /* Output tab */
        <div className="p-4 bg-slate-950 font-mono text-xs text-slate-300 overflow-x-auto max-h-96 space-y-3">
          <div className="flex items-center gap-2 text-slate-400 text-[11px]">
            <Terminal className="w-4 h-4 text-amber-400" />
            <span>Sandbox Execution Result Payload</span>
          </div>
          <pre className="whitespace-pre-wrap text-emerald-400 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            {JSON.stringify(executionResult, null, 2) || 'No execution result'}
          </pre>
        </div>
      )}
    </div>
  );
}
