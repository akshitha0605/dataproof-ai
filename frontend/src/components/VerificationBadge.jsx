import React from 'react';
import { CheckCircle2, AlertTriangle, ShieldAlert, XCircle, HelpCircle } from 'lucide-react';

export default function VerificationBadge({ status, className = '' }) {
  if (status === 'VERIFIED ✓' || status === 'VERIFIED') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 ${className}`}>
        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
        VERIFIED
      </span>
    );
  }

  if (status === 'CANNOT DETERMINE') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 ${className}`}>
        <HelpCircle className="w-4 h-4 text-amber-500" />
        CANNOT DETERMINE
      </span>
    );
  }

  if (status === 'AMBIGUOUS') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30 ${className}`}>
        <AlertTriangle className="w-4 h-4 text-cyan-500" />
        CLARIFICATION REQUIRED
      </span>
    );
  }

  if (status === 'UNVERIFIED') {
    return (
      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30 ${className}`}>
        <ShieldAlert className="w-4 h-4 text-rose-500" />
        UNVERIFIED
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/30 ${className}`}>
      <XCircle className="w-4 h-4 text-red-500" />
      {status || 'UNVERIFIED'}
    </span>
  );
}
