import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import QuestionBox from './components/QuestionBox';
import LoadingView from './components/LoadingView';
import AnswerCard from './components/AnswerCard';
import DataPreviewModal from './components/DataPreviewModal';
import SampleDatasetsModal from './components/SampleDatasetsModal';
import { analyzeQuestion, fetchDatasetProfile } from './services/api';
import { Sparkles, RefreshCw } from 'lucide-react';

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [dataset, setDataset] = useState(null); // Uploaded dataset profile
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [showSampleModal, setShowSampleModal] = useState(false);

  // Sync theme class on HTML element
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleDatasetUploaded = (profile) => {
    setDataset(profile);
    setResponse(null);
    setError(null);
  };

  const handleResetDataset = () => {
    setDataset(null);
    setResponse(null);
    setError(null);
    setShowPreview(false);
  };

  const handleAnalyze = async (questionStr, selectedAmbiguousColumn = null) => {
    if (!dataset || !questionStr) return;

    setLoading(true);
    setError(null);

    try {
      const res = await analyzeQuestion({
        datasetIds: [dataset.id],
        sheetName: dataset.active_sheet || null,
        question: questionStr,
        selectedAmbiguousColumn,
      });

      setResponse(res);
    } catch (err) {
      setError(err.message || "We couldn't safely verify this analysis. No verified answer was returned.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAmbiguousColumn = (colName) => {
    if (response && response.question) {
      handleAnalyze(response.question, colName);
    }
  };

  const handleAskAnother = (newQ) => {
    if (newQ) {
      handleAnalyze(newQ);
    } else {
      setResponse(null);
    }
  };

  const handleSelectSample = (sampleProfile) => {
    setDataset(sampleProfile);
    setResponse(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-200">
      {/* Clean Single Header */}
      <Header theme={theme} onToggleTheme={toggleTheme} />

      {/* Main Workspace Container - Centered */}
      <main className="flex-1 max-w-3xl w-full mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-8 flex flex-col justify-center">
        
        {/* Landing State Hero Title (Before Answer or Loading) */}
        {!response && !loading && (
          <div className="text-center space-y-2 pt-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
              DATAPROOF AI
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto">
              Upload any data file and ask a question.
            </p>
          </div>
        )}

        {/* 1. UPLOAD AREA (Primary Step) */}
        {!response && !loading && (
          <FileUpload
            dataset={dataset}
            onDatasetUploaded={handleDatasetUploaded}
            onResetDataset={handleResetDataset}
            onTogglePreview={() => setShowPreview(true)}
          />
        )}

        {/* 2. QUESTION AREA (Appears clearly after file upload) */}
        {dataset && !loading && !response && (
          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            <QuestionBox onAnalyze={handleAnalyze} loading={loading} />
          </div>
        )}

        {/* 3. LOADING STATE */}
        {loading && <LoadingView />}

        {/* Error message if any */}
        {error && !loading && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 text-xs text-center font-medium">
            {error}
          </div>
        )}

        {/* 4. ANSWER & PROOF SCREEN */}
        {response && !loading && (
          <div className="space-y-6 animate-in fade-in duration-300">
            {/* Answer Card (Answer + Verification Badge + Proof Accordion) */}
            <AnswerCard
              response={response}
              onSelectAmbiguousColumn={handleSelectAmbiguousColumn}
              onAskAnother={handleAskAnother}
            />

            {/* Change Dataset / Start New Analysis Button */}
            <div className="flex justify-center pt-2">
              <button
                onClick={handleResetDataset}
                className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-all"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Upload a different data file</span>
              </button>
            </div>
          </div>
        )}

        {/* Discrete Secondary Sample Datasets Picker */}
        {!dataset && !loading && !response && (
          <div className="text-center pt-4">
            <button
              onClick={() => setShowSampleModal(true)}
              className="inline-flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-all font-medium"
            >
              <Sparkles className="w-3.5 h-3.5 text-cyan-500" />
              <span>Don't have a file ready? Try a sample dataset</span>
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800/80 py-6 text-center text-xs text-slate-400 dark:text-slate-500">
        <div className="max-w-3xl mx-auto px-4 flex items-center justify-between flex-wrap gap-2">
          <div>DATAPROOF AI — Ask your data. Get a proven answer.</div>
          <div className="font-mono text-[11px]">Dynamic Code Verification • Zero Hardcoding</div>
        </div>
      </footer>

      {/* Data Preview Modal */}
      {showPreview && dataset && (
        <DataPreviewModal
          datasetId={dataset.id}
          fileName={dataset.file_name}
          onClose={() => setShowPreview(false)}
        />
      )}

      {/* Sample Datasets Modal */}
      {showSampleModal && (
        <SampleDatasetsModal
          onSelectSample={handleSelectSample}
          onClose={() => setShowSampleModal(false)}
        />
      )}
    </div>
  );
}
