import React from 'react';
import { HelpCircle, Download } from 'lucide-react';
import { exportToCSV } from '../utils/formatters';

export function ChartCard({
  title,
  subtitle,
  tooltip,
  children,
  dataToExport,
  exportFilename = 'chart_data',
  actions,
  className = '',
  loading = false,
  empty = false,
  emptyMessage = 'No data available for the selected filters.',
  minHeight = 'min-h-[340px]',
}) {
  const handleExport = () => {
    if (dataToExport && dataToExport.length > 0) {
      exportToCSV(exportFilename, dataToExport);
    }
  };

  return (
    <div className={`bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs flex flex-col ${className}`}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
        <div>
          <div className="flex items-center gap-1.5">
            <h3 className="text-sm font-semibold text-slate-900 tracking-tight">{title}</h3>
            {tooltip && (
              <div className="relative group/tooltip cursor-help">
                <HelpCircle className="w-3.5 h-3.5 text-slate-400 hover:text-slate-600" />
                <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover/tooltip:flex flex-col z-30 w-56 p-2 bg-slate-900 text-white text-[11px] leading-relaxed rounded-md shadow-lg pointer-events-none">
                  {tooltip}
                  <div className="absolute left-1/2 -translate-x-1/2 top-full border-4 border-transparent border-t-slate-900"></div>
                </div>
              </div>
            )}
          </div>
          {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {actions}
          {dataToExport && dataToExport.length > 0 && (
            <button
              onClick={handleExport}
              title="Export filtered data to CSV"
              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 bg-slate-50 hover:bg-slate-100 hover:text-slate-900 border border-slate-200 rounded-lg transition-colors cursor-pointer"
            >
              <Download className="w-3 h-3 text-slate-500" />
              <span>CSV</span>
            </button>
          )}
        </div>
      </div>

      {/* Chart Body */}
      <div className={`mt-4 flex-1 flex flex-col justify-center ${minHeight} relative`}>
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2">
            <div className="w-8 h-8 rounded-full border-2 border-slate-200 border-t-sky-600 animate-spin"></div>
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">Loading chart...</span>
          </div>
        ) : empty ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-slate-400 py-8">
            <p className="text-xs font-medium text-slate-500">{emptyMessage}</p>
            <p className="text-[11px] text-slate-400 mt-1">Try widening your date range or clearing category/state filters.</p>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
