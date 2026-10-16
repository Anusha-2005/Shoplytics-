import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { analyticsService, healthService } from '../api/services';

const FilterContext = createContext(null);

const DEFAULT_FILTERS = {
  startDate: '',
  endDate: '',
  state: '',
  category: '',
  orderStatus: '',
};

export function FilterProvider({ children }) {
  const [filters, setFiltersState] = useState(DEFAULT_FILTERS);
  const [options, setOptions] = useState({
    states: [],
    categories: [],
    orderStatuses: [],
    dateRange: { minDate: '2016-09-04', maxDate: '2018-10-17' },
  });
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [isBackendOnline, setIsBackendOnline] = useState(null);
  const [backendMeta, setBackendMeta] = useState(null);

  // Check health and load filter options
  const checkHealthAndOptions = useCallback(async () => {
    try {
      const health = await healthService.getHealth();
      setIsBackendOnline(health.status === 'healthy');
      setBackendMeta(health);
    } catch (err) {
      console.warn('Backend health check failed:', err);
      setIsBackendOnline(false);
    }

    try {
      setOptionsLoading(true);
      const res = await analyticsService.getFilterOptions();
      setOptions({
        states: res.available_states || res.states || [],
        categories: res.available_categories || res.categories || [],
        orderStatuses: res.available_statuses || res.order_statuses || [],
        dateRange: {
          minDate: res.min_date || res.date_range?.min_date || '2016-09-04',
          maxDate: res.max_date || res.date_range?.max_date || '2018-10-17',
        },
      });
    } catch (err) {
      console.error('Failed to load filter options:', err);
    } finally {
      setOptionsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealthAndOptions();
  }, [checkHealthAndOptions]);

  const setFilter = useCallback((key, value) => {
    setFiltersState((prev) => ({
      ...prev,
      [key]: value === 'all' ? '' : value,
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setFiltersState(DEFAULT_FILTERS);
  }, []);

  const triggerRefresh = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1);
    checkHealthAndOptions();
  }, [checkHealthAndOptions]);

  const activeFilterCount = useMemo(() => {
    return Object.values(filters).filter((val) => val !== '' && val !== null && val !== undefined).length;
  }, [filters]);

  const contextValue = useMemo(
    () => ({
      filters,
      setFilter,
      setFilters: setFiltersState,
      resetFilters,
      options,
      optionsLoading,
      refreshTrigger,
      triggerRefresh,
      isBackendOnline,
      backendMeta,
      activeFilterCount,
    }),
    [
      filters,
      setFilter,
      resetFilters,
      options,
      optionsLoading,
      refreshTrigger,
      triggerRefresh,
      isBackendOnline,
      backendMeta,
      activeFilterCount,
    ]
  );

  return <FilterContext.Provider value={contextValue}>{children}</FilterContext.Provider>;
}

export function useFilters() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
}
