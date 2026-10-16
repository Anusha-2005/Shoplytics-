import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { FilterProvider } from './context/FilterContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';

// Pages
import { ExecutiveOverview } from './pages/ExecutiveOverview';
import { SalesAnalytics } from './pages/SalesAnalytics';
import { ProductAnalytics } from './pages/ProductAnalytics';
import { CustomerInsights } from './pages/CustomerInsights';
import { DeliveryReviews } from './pages/DeliveryReviews';
import { GeographicAnalysis } from './pages/GeographicAnalysis';
import { DataQuality } from './pages/DataQuality';

export function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <BrowserRouter>
      <FilterProvider>
        <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col antialiased">
          {/* Collapsible Sidebar */}
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

          {/* Main Layout Area (shifted on desktop for sidebar) */}
          <div className="lg:pl-64 flex flex-col flex-1 min-w-0">
            {/* Top Compact Header */}
            <Header onToggleSidebar={() => setSidebarOpen((prev) => !prev)} />

            {/* Global Interactive Filter Bar */}
            <FilterBar />

            {/* Dynamic Page Views */}
            <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
              <Routes>
                <Route path="/" element={<ExecutiveOverview />} />
                <Route path="/sales" element={<SalesAnalytics />} />
                <Route path="/products" element={<ProductAnalytics />} />
                <Route path="/customers" element={<CustomerInsights />} />
                <Route path="/delivery" element={<DeliveryReviews />} />
                <Route path="/geo" element={<GeographicAnalysis />} />
                <Route path="/data-quality" element={<DataQuality />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>

            {/* Footer */}
            <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
                <div className="flex items-center gap-1.5 font-medium text-slate-600">
                  <span>Shoplytics</span>
                  <span className="text-slate-300">•</span>
                  <span>E-Commerce Analytics Dashboard</span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  Data Analyst Internship Portfolio • Brazilian E-Commerce (Olist) • React + FastAPI + SQLite
                </div>
              </div>
            </footer>
          </div>
        </div>
      </FilterProvider>
    </BrowserRouter>
  );
}

export default App;
