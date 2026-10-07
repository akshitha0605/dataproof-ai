import React, { useState } from 'react';
import { HelpCircle, AlertTriangle, ShieldCheck, ArrowRight, CornerDownRight, RotateCcw } from 'lucide-react';
import VerificationBadge from './VerificationBadge';
import ProofAccordion from './ProofAccordion';

export default function AnswerCard({ response, onSelectAmbiguousColumn, onAskAnother }) {
  const [followUpQuestion, setFollowUpQuestion] = useState('');

  if (!response) return null;

  const {
    status,
    question,
    answer,
    verification_explanation,
    evidence,
    proof_code,
    execution_result,
    ambiguity,
    cannot_determine_details,
  } = response;

  const handleFollowUpSubmit = (e) => {
    e.preventDefault();
    if (!followUpQuestion.trim()) return;
    onAskAnother(followUpQuestion.trim());
    setFollowUpQuestion('');
  };

  // 1. Ambiguous Clarification State
  if (status === 'AMBIGUOUS' && ambiguity && ambiguity.is_ambiguous) {
    return (
      <div className="w-full bg-white dark:bg-slate-900 border border-cyan-500/40 rounded-2xl p-6 space-y-4 shadow-sm transition-all">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-cyan-600 dark:text-cyan-400 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-cyan-500" />
            <span>Clarification Needed</span>
          </div>
          <VerificationBadge status="AMBIGUOUS" />
        </div>

        <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
          {ambiguity.prompt_message || 'I found more than one possible field for this question. Please clarify which one you mean:'}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-1">
          {ambiguity.options?.map((opt) => (
            <button
              key={opt.field_name}
              onClick={() => onSelectAmbiguousColumn(opt.field_name)}
              className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 hover:border-cyan-500 text-left transition-all hover:scale-[1.01] group"
            >
              <div className="text-xs font-mono font-bold text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 flex items-center justify-between">
                <span>{opt.field_name}</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-500" />
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 truncate">
                {opt.sample_value !== null ? `Sample: ${opt.sample_value}` : opt.description}
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // 2. Refusal State (CANNOT DETERMINE)
  if (status === 'CANNOT DETERMINE') {
    return (
      <div className="w-full bg-white dark:bg-slate-900 border border-amber-500/30 rounded-2xl p-6 space-y-4 shadow-sm transition-all">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm">
            <HelpCircle className="w-5 h-5 text-amber-500" />
            <span>CANNOT DETERMINE</span>
          </div>
          <VerificationBadge status="CANNOT DETERMINE" />
        </div>

        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 font-mono">
            Question: "{question}"
          </div>
          <div className="text-sm font-bold text-slate-900 dark:text-slate-100 leading-relaxed">
            The uploaded file does not contain enough information to answer this question.
          </div>
          {cannot_determine_details?.reason && (
            <div className="text-xs text-amber-700 dark:text-amber-300 pt-1 font-medium">
              Reason: {cannot_determine_details.reason}
            </div>
          )}
        </div>

        <div className="pt-2">
          <button
            onClick={() => onAskAnother('')}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Ask a different question</span>
          </button>
        </div>
      </div>
    );
  }

  // 3. Error / Execution Failure State
  if (status === 'ERROR' || status === 'FAILED') {
    return (
      <div className="w-full bg-white dark:bg-slate-900 border border-rose-500/30 rounded-2xl p-6 space-y-4 shadow-sm transition-all">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-sm">
            <AlertTriangle className="w-5 h-5 text-rose-500" />
            <span>Execution Failure</span>
          </div>
          <VerificationBadge status="UNVERIFIED" />
        </div>

        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-rose-600 dark:text-rose-400 font-medium">
          We couldn't safely verify this analysis. No verified answer was returned.
        </div>
      </div>
    );
  }

  // 4. Successful Answer Screen (VERIFIED or UNVERIFIED)
  return (
    <div className="w-full space-y-5">
      {/* Answer Card Container */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 sm:p-7 space-y-5 shadow-sm transition-all">
        {/* Question Header */}
        <div className="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5 border-b border-slate-100 dark:border-slate-800/80 pb-3">
          <span className="font-semibold text-slate-400 dark:text-slate-500">Your question:</span>
          <span className="font-bold text-slate-800 dark:text-slate-200">"{question}"</span>
        </div>

        {/* Answer Label & Large Answer Text */}
        <div className="space-y-2">
          <div className="text-[11px] font-mono font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider">
            ANSWER
          </div>
          <div className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 leading-snug">
            {answer}
          </div>
        </div>

        {/* Verification Badge & Subtext */}
        <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 flex items-start sm:items-center justify-between flex-col sm:flex-row gap-3">
          <div className="space-y-1">
            <VerificationBadge status={status} />
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {status === 'VERIFIED ✓' || status === 'VERIFIED'
                ? 'This answer was calculated from your uploaded data and verified against the execution result.'
                : 'Based on your uploaded data.'}
            </p>
          </div>
        </div>

        {/* Proof Accordion: View Evidence & View Proof Code */}
        <ProofAccordion
          evidence={evidence}
          proofCode={proof_code}
          executionResult={execution_result}
        />
      </div>

      {/* Ask Follow-Up / Another Question Bar */}
      <div className="bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 sm:p-5">
        <form onSubmit={handleFollowUpSubmit} className="flex items-center gap-2">
          <input
            type="text"
            value={followUpQuestion}
            onChange={(e) => setFollowUpQuestion(e.target.value)}
            placeholder="Ask a follow-up question about this data..."
            className="flex-1 bg-white dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl py-2.5 px-4 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500"
          />
          <button
            type="submit"
            disabled={!followUpQuestion.trim()}
            className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs flex items-center gap-1.5 transition-all disabled:opacity-40"
          >
            <span>Ask</span>
            <CornerDownRight className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
