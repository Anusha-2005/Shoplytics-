import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  Package,
  Users,
  Truck,
  MapPin,
  ShieldCheck,
  Database,
  ExternalLink,
  BarChart3,
  X,
} from 'lucide-react';
import { useFilters } from '../context/FilterContext';

const NAV_ITEMS = [
  { path: '/', label: 'Executive Overview', icon: LayoutDashboard },
  { path: '/sales', label: 'Sales Analytics', icon: TrendingUp },
  { path: '/products', label: 'Product Analytics', icon: Package },
  { path: '/customers', label: 'Customer Insights', icon: Users },
  { path: '/delivery', label: 'Delivery & Reviews', icon: Truck },
  { path: '/geo', label: 'Geographic Analysis', icon: MapPin },
  { path: '/data-quality', label: 'Data Quality & Audits', icon: ShieldCheck },
];

export function Sidebar({ isOpen, onClose }) {
  const { isBackendOnline } = useFilters();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-slate-950 text-slate-300 flex flex-col border-r border-slate-800 transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-800/80 bg-slate-950">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-600 to-teal-400 flex items-center justify-center text-white shadow-md shadow-sky-900/30">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
                Shoplytics
                <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30">
                  BI
                </span>
              </h1>
              <p className="text-[10px] text-slate-400 font-medium">Brazilian E-Commerce</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="lg:hidden p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Section */}
        <div className="flex-1 py-5 px-3 overflow-y-auto space-y-1">
          <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Analytics Modules
          </div>

          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => onClose && onClose()}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                    isActive
                      ? 'bg-sky-600 text-white shadow-sm shadow-sky-600/30 font-semibold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      className={`w-4 h-4 transition-colors ${
                        isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                      }`}
                    />
                    <span>{item.label}</span>
                  </>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* System & Dataset Meta Info */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-[11px] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-teal-400" />
                <span>Olist Star Schema</span>
              </span>
              <span
                className={`w-2 h-2 rounded-full ${
                  isBackendOnline ? 'bg-emerald-400 shadow-xs shadow-emerald-400' : 'bg-rose-500'
                }`}
                title={isBackendOnline ? 'Database connected' : 'Backend offline'}
              />
            </div>
            
            <div className="text-[10px] text-slate-400 leading-tight">
              <span>99,441 Orders • 1.45M records</span>
              <div className="text-slate-400 text-[9px] mt-0.5">SQLite + FastAPI Engine</div>
            </div>

            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="mt-1 flex items-center justify-between text-[10px] text-sky-400 hover:text-sky-300 font-medium pt-1 border-t border-slate-800/80"
            >
              <span>Swagger REST Docs</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </aside>
    </>
  );
}
