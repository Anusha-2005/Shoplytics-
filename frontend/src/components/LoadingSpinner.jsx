import React from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';

export function LoadingSpinner({ message = 'Loading analytics data...', minHeight = 'h-64' }) {
  return (
    <div className={`flex flex-col items-center justify-center ${minHeight} w-full text-slate-500`}>
      <div className="relative flex items-center justify-center">
        <div className="w-12 h-12 rounded-full border-2 border-slate-200 border-t-sky-600 animate-spin"></div>
        <div className="absolute w-6 h-6 rounded-full border-2 border-slate-100 border-b-teal-500 animate-spin"></div>
      </div>
      <p className="mt-4 text-xs font-medium tracking-wide text-slate-500 uppercase">{message}</p>
    </div>
  );
}

export function ErrorMessage({ message, onRetry, minHeight = 'h-64' }) {
  return (
    <div className={`flex flex-col items-center justify-center ${minHeight} w-full p-6 text-center rounded-xl border border-rose-200 bg-rose-50/50 text-rose-800`}>
      <div className="w-12 h-12 rounded-full bg-rose-100 flex items-center justify-center mb-3 text-rose-600">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-rose-900">Failed to load data</h3>
      <p className="text-xs text-rose-700 mt-1 max-w-md">{message || 'An error occurred while communicating with the analytics backend.'}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg shadow-sm transition-colors cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry Request
        </button>
      )}
    </div>
  );
}
