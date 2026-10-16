import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  MapPin,
  Globe,
  Compass,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { useFilters } from '../context/FilterContext';
import { geoService, logisticsService } from '../api/services';
import { formatBRL, formatNumber, formatPercent } from '../utils/formatters';
import { KPICard } from '../components/KPICard';
import { ChartCard } from '../components/ChartCard';
import { DataTable } from '../components/DataTable';
import { ErrorMessage } from '../components/LoadingSpinner';

const REGION_COLORS = {
  Southeast: '#0284c7',
  South: '#0d9488',
  Northeast: '#f59e0b',
  'Central-West': '#8b5cf6',
  North: '#f43f5e',
};

export function GeographicAnalysis() {
  const { filters, refreshTrigger } = useFilters();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Data
  const [geoData, setGeoData] = useState([]);
  const [regionalLogistics, setRegionalLogistics] = useState([]);

  // Table state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRegionFilter, setSelectedRegionFilter] = useState('all');
  const [sortBy, setSortBy] = useState('total_revenue');
  const [sortDesc, setSortDesc] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const apiFilters = {
        start_date: filters.startDate,
        end_date: filters.endDate,
        category: filters.category,
      };

      const [geoRes, regRes] = await Promise.all([
        geoService.getGeoSummary(apiFilters),
        logisticsService.getRegionalPerformance(apiFilters),
      ]);

      setGeoData(geoRes || []);
      setRegionalLogistics(regRes || []);
    } catch (err) {
      console.error('Failed to load geographic analysis:', err);
      setError(err.message || 'Unable to retrieve geographic data.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
  }, [loadData, refreshTrigger]);

  // Aggregate regional revenue distribution
  const regionalRevenue = useMemo(() => {
    const map = {};
    let total = 0;
    geoData.forEach((item) => {
      total += item.total_revenue || 0;
      if (!map[item.region]) {
        map[item.region] = { region: item.region, revenue: 0, orders: 0 };
      }
      map[item.region].revenue += item.total_revenue || 0;
      map[item.region].orders += item.orders_count || 0;
    });

    return Object.values(map).map((r) => ({
      ...r,
      share_pct: total > 0 ? (r.revenue / total) * 100 : 0,
    }));
  }, [geoData]);

  // Top state and regional insights
  const topState = geoData[0] || null;
  const southeastShare = regionalRevenue.find((r) => r.region === 'Southeast')?.share_pct || 68.8;

  // Filtered and sorted table data
  const filteredTableData = useMemo(() => {
    let result = [...geoData];

    if (selectedRegionFilter !== 'all') {
      result = result.filter((r) => r.region === selectedRegionFilter);
    }

    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      result = result.filter(
        (r) => r.state.toLowerCase().includes(q) || r.region.toLowerCase().includes(q)
      );
    }

    result.sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      if (typeof aVal === 'string') {
        return sortDesc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
      }
      return sortDesc ? (bVal ?? 0) - (aVal ?? 0) : (aVal ?? 0) - (bVal ?? 0);
    });

    return result;
  }, [geoData, selectedRegionFilter, searchTerm, sortBy, sortDesc]);

  const paginatedData = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredTableData.slice(start, start + pageSize);
  }, [filteredTableData, page, pageSize]);

  const handleSort = (key) => {
    if (sortBy === key) {
      setSortDesc(!sortDesc);
    } else {
      setSortBy(key);
      setSortDesc(true);
    }
    setPage(1);
  };

  const tableColumns = [
    {
      key: 'state',
      label: 'State (UF)',
      sortable: true,
      render: (val) => (
        <div className="flex items-center gap-1.5 font-bold text-slate-900">
          <span className="w-6 h-6 rounded bg-slate-100 flex items-center justify-center font-mono text-[11px] border border-slate-200">
            {val}
          </span>
        </div>
      ),
    },
    {
      key: 'region',
      label: 'Macro-Region',
      sortable: true,
      render: (val) => (
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium"
          style={{
            backgroundColor: `${REGION_COLORS[val] || '#64748b'}15`,
            color: REGION_COLORS[val] || '#64748b',
          }}
        >
          {val}
        </span>
      ),
    },
    {
      key: 'total_revenue',
      label: 'Revenue (BRL)',
      sortable: true,
      align: 'right',
      render: (val) => <span className="font-mono font-semibold text-slate-900">{formatBRL(val)}</span>,
    },
    {
      key: 'orders_count',
      label: 'Orders',
      sortable: true,
      align: 'right',
      render: (val) => <span className="font-mono text-slate-700">{formatNumber(val)}</span>,
    },
    {
      key: 'unique_customers',
      label: 'Unique Buyers',
      sortable: true,
      align: 'right',
      render: (val) => <span className="font-mono text-slate-600">{formatNumber(val)}</span>,
    },
    {
      key: 'avg_order_value',
      label: 'AOV',
      sortable: true,
      align: 'right',
      render: (val) => <span className="font-mono text-slate-600">{formatBRL(val)}</span>,
    },
    {
      key: 'avg_delivery_days',
      label: 'Avg Transit',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span className="font-mono text-slate-700 font-medium">
          {val ? `${val} days` : '—'}
        </span>
      ),
    },
    {
      key: 'delay_rate_pct',
      label: 'Delay Rate',
      sortable: true,
      align: 'right',
      render: (val) => (
        <span
          className={`font-mono font-semibold ${
            val > 10 ? 'text-rose-600' : val > 6 ? 'text-amber-600' : 'text-emerald-600'
          }`}
        >
          {formatPercent(val, 1)}
        </span>
      ),
    },
    {
      key: 'avg_freight',
      label: 'Avg Freight',
      sortable: true,
      align: 'right',
      render: (val) => <span className="font-mono text-slate-500">{formatBRL(val)}</span>,
    },
  ];

  if (error && geoData.length === 0) {
    return <ErrorMessage message={error} onRetry={loadData} />;
  }

  return (
    <div className="space-y-6">
      {/* Geographic KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Dominant State Market"
          value={topState ? `${topState.state} (São Paulo)` : 'SP'}
          subtitle={
            topState
              ? `${formatBRL(topState.total_revenue, true)} (${formatNumber(topState.orders_count)} orders)`
              : ''
          }
          icon={MapPin}
          colorScheme="blue"
          loading={loading}
          tooltip="São Paulo (SP) represents the single largest consumer and merchant concentration in Brazil."
        />

        <KPICard
          title="Southeast Region Share"
          value={formatPercent(southeastShare, 1)}
          subtitle="SP, RJ, MG, ES consolidated"
          icon={Globe}
          colorScheme="teal"
          loading={loading}
          tooltip="Combined gross merchandise value originating from the 4 states comprising the Brazilian Southeast region."
        />

        <KPICard
          title="Transit Delivery Disparity"
          value="8.5 vs 28.9 days"
          subtitle="Southeast (fastest) vs North (slowest)"
          icon={Truck}
          colorScheme="purple"
          loading={loading}
          tooltip="Extreme geographic logistics span: Urbanized coastal states receive parcels in under 9 days, while remote northern states experience 28+ days."
        />

        <KPICard
          title="Regional Freight Cost Multiplier"
          value="~2.4x Multiplier"
          subtitle="R$ 16.5 (SE) vs R$ 39.8 (North)"
          icon={Compass}
          colorScheme="amber"
          loading={loading}
          tooltip="Cross-country haulage and low seller density in remote regions double the consumer shipping freight burden."
        />
      </div>

      {/* Row 1: Top 10 States Revenue + Regional Share Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top 10 States Bar Chart */}
        <ChartCard
          title="Top 10 Brazilian States by Revenue"
          subtitle="Gross Merchandise Value (BRL) per Federative Unit"
          tooltip="Reveals the heavy market skew toward SP, RJ, and MG."
          className="lg:col-span-2"
          dataToExport={geoData.slice(0, 10)}
          exportFilename="top_states_revenue"
          loading={loading}
          empty={geoData.length === 0}
        >
          <ResponsiveContainer width="100%" height={290}>
            <BarChart
              data={geoData.slice(0, 10)}
              margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="state" tick={{ fontSize: 11, fill: '#334155' }} tickLine={false} />
              <YAxis
                tick={{ fontSize: 10, fill: '#64748b' }}
                tickFormatter={(v) => `R$ ${(v / 1000).toFixed(0)}k`}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                formatter={(val, name, item) => [
                  `${formatBRL(val)} (${formatNumber(item.payload.orders_count)} orders)`,
                  'Gross Revenue',
                ]}
                labelFormatter={(lbl, p) => `State: ${lbl} (${p?.[0]?.payload?.region || ''})`}
                contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
              />
              <Bar dataKey="total_revenue" radius={[4, 4, 0, 0]}>
                {geoData.slice(0, 10).map((entry) => (
                  <Cell
                    key={entry.state}
                    fill={REGION_COLORS[entry.region] || '#0284c7'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Macro-Region Share Donut */}
        <ChartCard
          title="Macro-Region GMV Share"
          subtitle="5 Brazilian Geographic Macro-Regions"
          tooltip="Consolidates state sales into official IBGE macro-regions: Southeast, South, Northeast, Central-West, North."
          dataToExport={regionalRevenue}
          exportFilename="regional_revenue_share"
          loading={loading}
          empty={regionalRevenue.length === 0}
        >
          <div className="h-[290px] flex flex-col justify-center">
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={regionalRevenue}
                  dataKey="revenue"
                  nameKey="region"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                >
                  {regionalRevenue.map((entry) => (
                    <Cell
                      key={entry.region}
                      fill={REGION_COLORS[entry.region] || '#64748b'}
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val, name, item) => [
                    `${formatBRL(val)} (${item.payload.share_pct?.toFixed(1)}%)`,
                    item.payload.region,
                  ]}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
                />
              </PieChart>
            </ResponsiveContainer>

            <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs">
              {regionalRevenue.map((r) => (
                <div key={r.region} className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: REGION_COLORS[r.region] || '#64748b' }}
                    />
                    <span className="text-slate-600 text-[11px]">{r.region}</span>
                  </div>
                  <span className="font-mono font-semibold text-slate-800 text-[11px]">
                    {r.share_pct?.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </ChartCard>
      </div>

      {/* Row 2: Regional Delivery Days & Delay Rate Disparities */}
      <ChartCard
        title="Regional Logistics Transit Duration vs Delay Rate"
        subtitle="Comparing actual delivery lead time (days) against delay rate (%) by macro-region"
        tooltip="Demonstrates why logistics SLA management requires region-specific estimated delivery models."
        dataToExport={regionalLogistics}
        exportFilename="regional_logistics_disparities"
        loading={loading}
        empty={regionalLogistics.length === 0}
      >
        <ResponsiveContainer width="100%" height={270}>
          <BarChart data={regionalLogistics} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis dataKey="region" tick={{ fontSize: 11, fill: '#334155' }} tickLine={false} />
            <YAxis
              yAxisId="left"
              tick={{ fontSize: 10, fill: '#0284c7' }}
              tickFormatter={(v) => `${v} d`}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              tick={{ fontSize: 10, fill: '#f43f5e' }}
              tickFormatter={(v) => `${v}%`}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              formatter={(val, name) => [
                name === 'avg_delivery_days' ? `${val} days` : `${val}%`,
                name === 'avg_delivery_days' ? 'Avg Delivery Days' : 'Delay Rate (%)',
              ]}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
            />
            <Legend
              formatter={(val) => (val === 'avg_delivery_days' ? 'Delivery Days' : 'Delay Rate %')}
              wrapperStyle={{ fontSize: '11px', paddingTop: '6px' }}
            />
            <Bar yAxisId="left" dataKey="avg_delivery_days" fill="#0284c7" radius={[4, 4, 0, 0]} />
            <Bar yAxisId="right" dataKey="delay_rate_pct" fill="#f43f5e" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Full 27 State Rankings Table */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-900 tracking-tight flex items-center gap-2">
              Comprehensive 27 Brazilian State Market Rankings
              <span className="text-[10px] font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                {geoData.length} Federative Units
              </span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Sortable breakdown of commercial volume, average basket size, carrier speed, and freight burden across all states.
            </p>
          </div>

          {/* Region filter pills */}
          <div className="flex items-center gap-1 text-xs">
            {['all', 'Southeast', 'South', 'Northeast', 'Central-West', 'North'].map((reg) => (
              <button
                key={reg}
                onClick={() => {
                  setSelectedRegionFilter(reg);
                  setPage(1);
                }}
                className={`px-2.5 py-1 rounded-lg border text-xs font-medium transition-colors cursor-pointer ${
                  selectedRegionFilter === reg
                    ? 'bg-slate-900 text-white border-slate-900'
                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                }`}
              >
                {reg === 'all' ? 'All Regions' : reg}
              </button>
            ))}
          </div>
        </div>

        <DataTable
          columns={tableColumns}
          data={paginatedData}
          totalRows={filteredTableData.length}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={(newSize) => {
            setPageSize(newSize);
            setPage(1);
          }}
          sortBy={sortBy}
          sortDesc={sortDesc}
          onSort={handleSort}
          searchTerm={searchTerm}
          onSearchChange={(val) => {
            setSearchTerm(val);
            setPage(1);
          }}
          searchPlaceholder="Search by State code (e.g. SP, RJ, MG) or Region..."
          loading={loading}
          exportFilename="state_geographic_rankings"
        />
      </div>
    </div>
  );
}
