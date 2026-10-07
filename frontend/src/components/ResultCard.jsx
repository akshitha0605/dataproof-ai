import React, { useState } from 'react';
import { CheckCircle2, HelpCircle, AlertTriangle, Send, ShieldCheck, Sparkles, ArrowRight } from 'lucide-react';
import VerificationBadge from './VerificationBadge';
import EvidenceTable from './EvidenceTable';
import ProofViewer from './ProofViewer';
import ChartView from './ChartView';
import AnalysisTrace from './AnalysisTrace';

export default function ResultCard({ responseData, onSelectAmbiguousColumn, onFollowUp }) {
  const [followUpText, setFollowUpText] = useState('');

  if (!responseData) return null;

  const {
    status,
    answer,
    verification_explanation,
    evidence,
    proof_code,
    execution_result,
    chart,
    trace_steps,
    ambiguity,
    cannot_determine_details,
    execution_time_ms
  } = responseData;

  const handleFollowUpSubmit = (e) => {
    e.preventDefault();
    if (!followUpText.trim()) return;
    onFollowUp(followUpText.trim());
    setFollowUpText('');
  };

  return (
    <div className="space-y-6">
      {/* Ambiguity Clarification Modal/Card */}
      {status === 'AMBIGUOUS' && ambiguity && ambiguity.is_ambiguous && (
        <div className="p-6 rounded-2xl glass-panel border border-cyan-500/40 bg-cyan-950/20 space-y-4 glow-cyan">
          <div className="flex items-center gap-2 text-cyan-300 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-cyan-400" />
            <span>Clarification Needed: Ambiguous Question</span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            {ambiguity.prompt_message || 'I found multiple numerical fields in your dataset. Which one would you like me to analyze?'}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-2">
            {ambiguity.options.map((opt) => (
              <button
                key={opt.field_name}
                onClick={() => onSelectAmbiguousColumn(opt.field_name)}
                className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-700 hover:border-cyan-400 text-left transition-all hover:scale-[1.02] group"
              >
                <div className="text-xs font-mono font-bold text-slate-100 group-hover:text-cyan-400 flex items-center justify-between">
                  <span>{opt.field_name}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400" />
                </div>
                <div className="text-[11px] text-slate-400 mt-1 truncate">
                  {opt.sample_value !== null ? `Sample: ${opt.sample_value}` : opt.description}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* CANNOT DETERMINE Refusal Card */}
      {status === 'CANNOT DETERMINE' && (
        <div className="p-6 rounded-2xl glass-panel border border-amber-500/40 bg-amber-950/20 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-amber-300 font-bold text-base">
              <HelpCircle className="w-5 h-5 text-amber-400" />
              <span>CANNOT DETERMINE</span>
            </div>
            <VerificationBadge status="CANNOT DETERMINE" />
          </div>

          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3 text-xs text-slate-300">
            <div className="font-semibold text-amber-200">{answer}</div>

            {cannot_determine_details && (
              <div className="space-y-2 pt-2 border-t border-slate-800/80 text-[11px]">
                <div>
                  <span className="text-slate-500 font-medium">Reason for Refusal:</span>{' '}
                  <span className="text-slate-300">{cannot_determine_details.reason}</span>
                </div>

                {cannot_determine_details.missing_information?.length > 0 && (
                  <div>
                    <span className="text-amber-400 font-medium">Missing Required Information:</span>{' '}
                    <span className="font-mono text-amber-300">
                      {cannot_determine_details.missing_information.join(', ')}
                    </span>
                  </div>
                )}

                {cannot_determine_details.available_information?.length > 0 && (
                  <div>
                    <span className="text-slate-500 font-medium">Available Dataset Fields:</span>{' '}
                    <span className="font-mono text-slate-400">
                      {cannot_determine_details.available_information.join(', ')}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          <p className="text-[11px] text-slate-400 italic">
            DATAPROOF AI refuses to guess or fabricate answers when required information does not exist in the dataset.
          </p>
        </div>
      )}

      {/* Successful Verified Answer Card */}
      {status === 'VERIFIED ✓' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl glass-panel border border-emerald-500/30 bg-slate-950/60 space-y-4 glow-verified">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-bold text-slate-200">Execution-Backed Verified Answer</h3>
              </div>

              <VerificationBadge status={status} />
            </div>

            {/* Answer Box */}
            <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
              <div className="text-base font-bold text-slate-100 leading-relaxed">{answer}</div>
              <div className="text-xs text-emerald-400/90 font-mono flex items-center gap-1 pt-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>{verification_explanation}</span>
              </div>
            </div>

            {/* Follow-up question bar */}
            <form onSubmit={handleFollowUpSubmit} className="pt-2">
              <div className="relative flex items-center">
                <input
                  type="text"
                  value={followUpText}
                  onChange={(e) => setFollowUpText(e.target.value)}
                  placeholder="Ask a follow-up question (e.g. What about the lowest? Or Compare with previous month)..."
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-xl py-2.5 pl-4 pr-24 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                />
                <button
                  type="submit"
                  disabled={!followUpText.trim()}
                  className="absolute right-1.5 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs flex items-center gap-1 transition-all disabled:opacity-40"
                >
                  <Send className="w-3 h-3" />
                  <span>Follow up</span>
                </button>
              </div>
            </form>
          </div>

          {/* Trace steps */}
          <AnalysisTrace steps={trace_steps} executionTimeMs={execution_time_ms} />

          {/* Dynamic Interactive Chart */}
          {chart && <ChartView chartData={chart} />}

          {/* Source of Truth Evidence Table */}
          {evidence && <EvidenceTable evidence={evidence} />}

          {/* Executable Proof Viewer */}
          {proof_code && <ProofViewer code={proof_code} executionResult={execution_result} />}
        </div>
      )}
    </div>
  );
}
