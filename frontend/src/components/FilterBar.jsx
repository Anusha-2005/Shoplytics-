import React from 'react';
import { Filter, X, RotateCcw, Calendar, MapPin, Tag, CheckCircle2 } from 'lucide-react';
import { useFilters } from '../context/FilterContext';

export function FilterBar() {
  const { filters, setFilter, resetFilters, options, activeFilterCount } = useFilters();

  const handlePreset = (preset) => {
    if (preset === '2017') {
      setFilter('startDate', '2017-01-01');
      setFilter('endDate', '2017-12-31');
    } else if (preset === '2018') {
      setFilter('startDate', '2018-01-01');
      setFilter('endDate', '2018-08-31');
    } else if (preset === 'all') {
      setFilter('startDate', '');
      setFilter('endDate', '');
    }
  };

  return (
    <div className="bg-white border-b border-slate-200/80 px-4 sm:px-6 py-3 shadow-2xs">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Filter Inputs Grid */}
        <div className="flex flex-wrap items-center gap-2.5 flex-1">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider mr-1">
            <Filter className="w-3.5 h-3.5 text-sky-600" />
            <span className="hidden sm:inline">Filters:</span>
          </div>

          {/* Start Date */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-[10px] text-slate-400 font-medium">From:</span>
            <input
              type="date"
              value={filters.startDate}
              min={options.dateRange?.minDate}
              max={filters.endDate || options.dateRange?.maxDate}
              onChange={(e) => setFilter('startDate', e.target.value)}
              className="bg-transparent text-slate-800 text-xs focus:outline-none cursor-pointer"
            />
          </div>

          {/* End Date */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs">
            <Calendar className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-[10px] text-slate-400 font-medium">To:</span>
            <input
              type="date"
              value={filters.endDate}
              min={filters.startDate || options.dateRange?.minDate}
              max={options.dateRange?.maxDate}
              onChange={(e) => setFilter('endDate', e.target.value)}
              className="bg-transparent text-slate-800 text-xs focus:outline-none cursor-pointer"
            />
          </div>

          {/* Quick presets */}
          <div className="hidden lg:flex items-center gap-1 text-[11px]">
            <button
              onClick={() => handlePreset('2017')}
              className={`px-2 py-0.5 rounded border text-[11px] font-medium transition-colors cursor-pointer ${
                filters.startDate === '2017-01-01' && filters.endDate === '2017-12-31'
                  ? 'bg-sky-50 text-sky-700 border-sky-300 font-semibold'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              2017
            </button>
            <button
              onClick={() => handlePreset('2018')}
              className={`px-2 py-0.5 rounded border text-[11px] font-medium transition-colors cursor-pointer ${
                filters.startDate === '2018-01-01' && filters.endDate === '2018-08-31'
                  ? 'bg-sky-50 text-sky-700 border-sky-300 font-semibold'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              2018 H1
            </button>
          </div>

          {/* State selector */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-xs">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filters.state}
              onChange={(e) => setFilter('state', e.target.value)}
              className="bg-transparent text-slate-800 text-xs focus:outline-none cursor-pointer pr-1"
            >
              <option value="">All States ({options.states?.length || 27})</option>
              {options.states?.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
          </div>

          {/* Category selector */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-xs max-w-[190px]">
            <Tag className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <select
              value={filters.category}
              onChange={(e) => setFilter('category', e.target.value)}
              className="bg-transparent text-slate-800 text-xs focus:outline-none cursor-pointer truncate"
            >
              <option value="">All Categories ({options.categories?.length || 71})</option>
              {options.categories?.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Order Status selector */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-xs">
            <CheckCircle2 className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filters.orderStatus}
              onChange={(e) => setFilter('orderStatus', e.target.value)}
              className="bg-transparent text-slate-800 text-xs focus:outline-none cursor-pointer pr-1"
            >
              <option value="">All Statuses</option>
              {options.orderStatuses?.map((st) => (
                <option key={st} value={st}>
                  {st.charAt(0).toUpperCase() + st.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Clear Filters Button */}
        {activeFilterCount > 0 && (
          <button
            onClick={resetFilters}
            className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Filters ({activeFilterCount})</span>
          </button>
        )}
      </div>

      {/* Active filter pills */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap items-center gap-1.5 mt-2.5 pt-2 border-t border-slate-100">
          <span className="text-[10px] uppercase font-bold text-slate-400 mr-1">Active:</span>
          {filters.startDate && (
            <span className="inline-flex items-center gap-1 bg-sky-50 text-sky-800 border border-sky-200 px-2 py-0.5 rounded text-[11px] font-medium">
              From: {filters.startDate}
              <button onClick={() => setFilter('startDate', '')} className="hover:text-rose-600">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {filters.endDate && (
            <span className="inline-flex items-center gap-1 bg-sky-50 text-sky-800 border border-sky-200 px-2 py-0.5 rounded text-[11px] font-medium">
              To: {filters.endDate}
              <button onClick={() => setFilter('endDate', '')} className="hover:text-rose-600">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {filters.state && (
            <span className="inline-flex items-center gap-1 bg-teal-50 text-teal-800 border border-teal-200 px-2 py-0.5 rounded text-[11px] font-medium">
              State: {filters.state}
              <button onClick={() => setFilter('state', '')} className="hover:text-rose-600">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {filters.category && (
            <span className="inline-flex items-center gap-1 bg-purple-50 text-purple-800 border border-purple-200 px-2 py-0.5 rounded text-[11px] font-medium">
              Category: {filters.category.replace(/_/g, ' ')}
              <button onClick={() => setFilter('category', '')} className="hover:text-rose-600">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {filters.orderStatus && (
            <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-800 border border-amber-200 px-2 py-0.5 rounded text-[11px] font-medium">
              Status: {filters.orderStatus}
              <button onClick={() => setFilter('orderStatus', '')} className="hover:text-rose-600">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
}
