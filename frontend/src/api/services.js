import apiClient from './client';

// Helper to filter out undefined or empty query params
function cleanParams(params = {}) {
  const cleaned = {};
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '' && value !== 'all') {
      cleaned[key] = value;
    }
  }
  return cleaned;
}

export const analyticsService = {
  getKPISummary: (params) => apiClient.get('/analytics/kpi-summary', { params: cleanParams(params) }),
  getFilterOptions: () => apiClient.get('/analytics/filter-options'),
};

export const salesService = {
  getOverview: (params) => apiClient.get('/sales/overview', { params: cleanParams(params) }),
  getMonthlyTrends: (params) => apiClient.get('/sales/monthly-trends', { params: cleanParams(params) }),
  getDailyTrends: (params) => apiClient.get('/sales/daily-trends', { params: cleanParams(params) }),
  getStatusBreakdown: (params) => apiClient.get('/sales/status-breakdown', { params: cleanParams(params) }),
  getPaymentMethods: (params) => apiClient.get('/sales/payment-methods', { params: cleanParams(params) }),
  getHourlyPatterns: (params) => apiClient.get('/sales/hourly-patterns', { params: cleanParams(params) }),
};

export const productService = {
  getTopCategories: (params) => apiClient.get('/products/top-categories', { params: cleanParams(params) }),
  getParetoAnalysis: (params) => apiClient.get('/products/pareto-analysis', { params: cleanParams(params) }),
  getWeightTiers: (params) => apiClient.get('/products/weight-tiers', { params: cleanParams(params) }),
  getProductTable: (params = {}) => apiClient.get('/products/table', { params: cleanParams(params) }),
};

export const customerService = {
  getRFMSummary: (params) => apiClient.get('/customers/rfm-summary', { params: cleanParams(params) }),
  getRepeatBehavior: (params) => apiClient.get('/customers/repeat-behavior', { params: cleanParams(params) }),
  getStateDistribution: (params) => apiClient.get('/customers/state-distribution', { params: cleanParams(params) }),
  getCohorts: () => apiClient.get('/customers/cohorts'),
  getReviewPatterns: () => apiClient.get('/customers/review-patterns'),
};

export const logisticsService = {
  getOverview: (params) => apiClient.get('/logistics/overview', { params: cleanParams(params) }),
  getStatePerformance: (params) => apiClient.get('/logistics/state-performance', { params: cleanParams(params) }),
  getRegionalPerformance: (params) => apiClient.get('/logistics/regional-performance', { params: cleanParams(params) }),
  getRouteComparison: (params) => apiClient.get('/logistics/route-comparison', { params: cleanParams(params) }),
};

export const reviewsService = {
  getOverview: (params) => apiClient.get('/reviews/overview', { params: cleanParams(params) }),
  getDelayImpact: (params) => apiClient.get('/reviews/delay-impact', { params: cleanParams(params) }),
  getScoreVsLeadtime: () => apiClient.get('/reviews/score-vs-leadtime'),
};

export const geoService = {
  getGeoSummary: (params) => apiClient.get('/geo/summary', { params: cleanParams(params) }),
};

export const healthService = {
  getHealth: () => apiClient.get('/health'),
  getQualityAudit: () => apiClient.get('/health/quality-audit'),
};
