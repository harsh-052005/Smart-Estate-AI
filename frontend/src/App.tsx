import React, { useState, useEffect } from 'react';
import { api, MetaData, OverviewData } from './api';
import { Navbar } from './components/Navbar';
import { OverviewPage } from './pages/OverviewPage';
import { PropertyExplorerPage } from './pages/PropertyExplorerPage';
import { ModelPerformanceLabPage } from './pages/ModelPerformanceLabPage';
import { ExplainabilityStudioPage } from './pages/ExplainabilityStudioPage';
import { PredictionStudioPage } from './pages/PredictionStudioPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { Building2 } from 'lucide-react';
import './App.css';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null);
  const [meta, setMeta] = useState<MetaData | null>(null);
  const [overview, setOverview] = useState<OverviewData | null>(null);

  useEffect(() => {
    // 1. Backend health check
    api.getHealth()
      .then((res) => {
        setApiHealthy(res.status === 'healthy');
      })
      .catch(() => {
        setApiHealthy(false);
      });

    // 2. Load metadata & overview
    Promise.all([api.getMeta(), api.getOverview()])
      .then(([m, o]) => {
        setMeta(m);
        setOverview(o);
      })
      .catch((err) => {
        console.error('Failed to load initial data:', err);
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F5] text-[#5A322A] selection:bg-[#E4A499]/35 selection:text-[#5A322A]">
      
      {/* Top Editorial Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiHealthy={apiHealthy}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {activeTab === 'overview' && (
          <OverviewPage
            data={overview}
            onExploreClick={() => setActiveTab('explorer')}
            onPredictClick={() => setActiveTab('prediction')}
          />
        )}

        {activeTab === 'explorer' && (
          <PropertyExplorerPage meta={meta} />
        )}

        {activeTab === 'lab' && (
          <ModelPerformanceLabPage />
        )}

        {activeTab === 'explainability' && (
          <ExplainabilityStudioPage />
        )}

        {activeTab === 'prediction' && (
          <PredictionStudioPage meta={meta} />
        )}

        {activeTab === 'methodology' && (
          <MethodologyPage />
        )}
      </main>

      {/* Luxury Editorial Footer */}
      <footer className="border-t border-[#E8E4DC] bg-[#FFFFFF] py-8 text-xs text-[#826F6A]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-5 h-5 rounded-md bg-[#BC7B6F] flex items-center justify-center text-white">
              <Building2 className="w-3 h-3" />
            </div>
            <span className="font-serif font-bold text-sm text-[#3D221C] tracking-tight">SMART ESTATE AI</span>
            <span className="text-[#CCCDC7]">|</span>
            <span className="text-[#826F6A]">Indian PropTech Machine Learning & Valuation Intelligence</span>
          </div>

          <div className="flex items-center gap-4 text-[#826F6A]">
            <span>FastAPI Server (:8000)</span>
            <span className="text-[#CCCDC7]">•</span>
            <span>React Production UI (:5173)</span>
            <span className="text-[#CCCDC7]">•</span>
            <span>Streamlit Interface (:8501)</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;
