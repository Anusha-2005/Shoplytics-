import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, RefreshCw, Wifi, WifiOff, Calendar, Filter } from 'lucide-react';
import { useFilters } from '../context/FilterContext';

const PAGE_TITLES = {
  '/': { title: 'Executive Overview', desc: 'Holistic business health, GMV, orders, AOV, and verified executive metrics' },
  '/sales': { title: 'Sales Analytics', desc: 'Revenue velocity, MoM growth trends, daily volume, and order status breakdown' },
  '/products': { title: 'Product Analytics', desc: 'Catalog performance, Pareto 80/20 distribution, pricing & weight tiers' },
  '/customers': { title: 'Customer Insights', desc: 'RFM segmentation, monthly cohort retention matrix, and buyer behavior' },
  '/delivery': { title: 'Delivery & Reviews', desc: 'Carrier SLA fulfillment, delivery duration, lead times, and CSAT review patterns' },
  '/geo': { title: 'Geographic Analysis', desc: 'Regional market penetration across 27 Brazilian states and 5 macro-regions' },
  '/data-quality': { title: 'Data Quality & Audits', desc: 'Star schema entity health, referential integrity tests, and null audits' },
};

export function Header({ onToggleSidebar }) {
  const location = useLocation();
  const { isBackendOnline, triggerRefresh, activeFilterCount, options } = useFilters();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const currentPage = PAGE_TITLES[location.pathname] || {
    title: 'Analytics Dashboard',
    desc: 'Brazilian E-Commerce Business Intelligence',
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    triggerRefresh();
    setTimeout(() => setIsRefreshing(false), 800);
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-2xs">
      {/* Left: Mobile Menu + Page Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight">
              {currentPage.title}
            </h2>
            {activeFilterCount > 0 && (
              <span className="inline-flex items-center gap-1 text-[11px] font-semibold bg-sky-50 text-sky-700 border border-sky-200 px-2 py-0.5 rounded-full">
                <Filter className="w-3 h-3" />
                {activeFilterCount} filter{activeFilterCount > 1 ? 's' : ''} active
              </span>
            )}
          </div>
          <p className="text-[11px] text-slate-500 hidden sm:block truncate max-w-md">
            {currentPage.desc}
          </p>
        </div>
      </div>

      {/* Right: Date span info, Status, Refresh */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        {/* Dataset Date Scope */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 text-xs text-slate-500 bg-slate-50 border border-slate-200/80 rounded-lg">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span className="font-medium text-slate-600">
            {options.dateRange?.minDate || '2016-09-04'} to {options.dateRange?.maxDate || '2018-10-17'}
          </span>
        </div>

        {/* API Status Badge */}
        <div
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium rounded-lg border ${
            isBackendOnline === true
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : isBackendOnline === false
              ? 'bg-rose-50 text-rose-700 border-rose-200'
              : 'bg-slate-50 text-slate-600 border-slate-200'
          }`}
          title={isBackendOnline ? 'FastAPI Backend Online (Port 8000)' : 'FastAPI Backend Offline'}
        >
          {isBackendOnline === true ? (
            <>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="hidden sm:inline">API Online</span>
            </>
          ) : isBackendOnline === false ? (
            <>
              <WifiOff className="w-3.5 h-3.5 text-rose-500" />
              <span>Offline</span>
            </>
          ) : (
            <>
              <Wifi className="w-3.5 h-3.5 text-slate-400 animate-pulse" />
              <span>Connecting</span>
            </>
          )}
        </div>

        {/* Refresh Button */}
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          title="Refresh dashboard data from backend"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 active:bg-slate-100 border border-slate-200 rounded-lg shadow-2xs transition-all cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${isRefreshing ? 'animate-spin text-sky-600' : ''}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>
    </header>
  );
}
