import React from 'react';
import { HelpCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendLabel,
  tooltip,
  colorScheme = 'blue', // 'blue', 'teal', 'emerald', 'amber', 'purple', 'rose'
  loading = false,
}) {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      border: 'border-blue-100',
      accent: 'text-blue-700',
    },
    teal: {
      bg: 'bg-teal-50',
      text: 'text-teal-600',
      border: 'border-teal-100',
      accent: 'text-teal-700',
    },
    emerald: {
      bg: 'bg-emerald-50',
      text: 'text-emerald-600',
      border: 'border-emerald-100',
      accent: 'text-emerald-700',
    },
    amber: {
      bg: 'bg-amber-50',
      text: 'text-amber-600',
      border: 'border-amber-100',
      accent: 'text-amber-700',
    },
    purple: {
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      border: 'border-purple-100',
      accent: 'text-purple-700',
    },
    rose: {
      bg: 'bg-rose-50',
      text: 'text-rose-600',
      border: 'border-rose-100',
      accent: 'text-rose-700',
    },
  };

  const scheme = colorMap[colorScheme] || colorMap.blue;

  if (loading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-4 bg-slate-200 rounded w-24"></div>
          <div className="w-10 h-10 bg-slate-100 rounded-lg"></div>
        </div>
        <div className="h-8 bg-slate-200 rounded w-36 mt-4"></div>
        <div className="h-3 bg-slate-100 rounded w-28 mt-2"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs hover:shadow-md transition-shadow relative group">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">{title}</span>
          {tooltip && (
            <div className="relative group/tooltip cursor-help">
              <HelpCircle className="w-3.5 h-3.5 text-slate-400 hover:text-slate-600" />
              <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 hidden group-hover/tooltip:flex flex-col z-30 w-52 p-2 bg-slate-900 text-white text-[11px] leading-relaxed rounded-md shadow-lg pointer-events-none">
                {tooltip}
                <div className="absolute left-1/2 -translate-x-1/2 top-full border-4 border-transparent border-t-slate-900"></div>
              </div>
            </div>
          )}
        </div>
        {Icon && (
          <div className={`w-10 h-10 rounded-lg ${scheme.bg} ${scheme.text} flex items-center justify-center border ${scheme.border}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-slate-900 font-mono">
          {value}
        </div>
        
        {(subtitle || trend !== undefined) && (
          <div className="mt-1.5 flex items-center gap-2 text-xs">
            {trend !== undefined && (
              <span
                className={`inline-flex items-center gap-0.5 font-medium px-1.5 py-0.5 rounded ${
                  trend > 0
                    ? 'text-emerald-700 bg-emerald-50'
                    : trend < 0
                    ? 'text-rose-700 bg-rose-50'
                    : 'text-slate-600 bg-slate-100'
                }`}
              >
                {trend > 0 ? (
                  <TrendingUp className="w-3 h-3" />
                ) : trend < 0 ? (
                  <TrendingDown className="w-3 h-3" />
                ) : (
                  <Minus className="w-3 h-3" />
                )}
                {trend > 0 ? `+${trend}%` : `${trend}%`}
              </span>
            )}
            {trendLabel && <span className="text-slate-400 font-medium">{trendLabel}</span>}
            {subtitle && <span className="text-slate-500">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
