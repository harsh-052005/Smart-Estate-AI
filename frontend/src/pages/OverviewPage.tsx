import React from 'react';
import { OverviewData } from '../api';
import { 
  Building2, 
  Sparkles, 
  ArrowRight,
  TrendingDown,
  CheckCircle,
  ShieldCheck,
  Award,
  Layers,
  Database,
  BarChart3
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

interface OverviewPageProps {
  data: OverviewData | null;
  onExploreClick: () => void;
  onPredictClick: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ data, onExploreClick, onPredictClick }) => {
  const benchmarkComparison = [
    { name: 'XGBoost (Winner)', mae: 28.64, rmse: 66.96, r2: 0.7628 },
    { name: 'Random Forest', mae: 32.61, rmse: 88.48, r2: 0.6855 },
    { name: 'Linear (Ridge)', mae: 37.36, rmse: 94.38, r2: 0.6422 },
    { name: 'Training Baseline', mae: 72.30, rmse: 137.52, r2: 0.0000 },
  ];

  return (
    <div className="space-y-10 animate-fadeIn">
      
      {/* Luxury Editorial Hero Section */}
      <div className="relative overflow-hidden rounded-2xl border border-[#E8E4DC] bg-[#FFFFFF] p-8 sm:p-12 shadow-sm">
        <div className="max-w-3xl space-y-4">
          <div className="flex items-center gap-2">
            <span className="editorial-badge">
              <Sparkles className="w-3.5 h-3.5 text-[#BC7B6F]" />
              PropTech Valuation Intelligence
            </span>
            <span className="text-xs font-mono text-[#718A9E] px-2.5 py-0.5 rounded-full bg-[#EDF2F6]">
              Bengaluru Residential Index
            </span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-serif font-bold text-[#3D221C] tracking-tight leading-[1.15]">
            Sophisticated Market Valuation. <br />
            <span className="text-[#BC7B6F] italic font-normal">
              Grounded in Authentic Property Evidence.
            </span>
          </h1>

          <p className="text-[#826F6A] text-sm sm:text-base leading-relaxed max-w-2xl font-sans">
            A rigorous PropTech machine learning platform evaluating residential property prices across 
            12,496 verified Bengaluru listings. Engineered with leak-free preprocessing, multi-model benchmarking, 
            and out-of-sample explainability auditing.
          </p>
          
          <div className="flex flex-wrap gap-3.5 pt-3">
            <button
              onClick={onPredictClick}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#5A322A] hover:bg-[#3D221C] text-[#FAF8F5] font-sans font-bold text-sm shadow-sm hover:shadow-md transition-all cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-[#E4A499]" />
              Open Valuation Studio
            </button>
            <button
              onClick={onExploreClick}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#FAF8F5] hover:bg-[#F3EFEA] text-[#5A322A] font-sans font-semibold text-sm border border-[#D8D4CC] transition-all cursor-pointer"
            >
              Explore 12,496 Listings
              <ArrowRight className="w-4 h-4 text-[#BC7B6F]" />
            </button>
          </div>
        </div>
      </div>

      {/* Top Level Metric Tiles */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="editorial-card p-5 border-t-4 border-t-[#BC7B6F]">
          <div className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider">Cleaned Listings</div>
          <div className="text-2xl sm:text-3xl font-serif font-bold text-[#3D221C] mt-1.5">
            {data?.kpis.total_properties.toLocaleString() || '12,496'}
          </div>
          <div className="text-xs text-[#BC7B6F] font-medium mt-1">240+ Localities</div>
        </div>

        <div className="editorial-card p-5 border-t-4 border-t-[#5A322A]">
          <div className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider">Winning Model</div>
          <div className="text-xl sm:text-2xl font-serif font-bold text-[#3D221C] mt-1.5 truncate">
            XGBoost
          </div>
          <div className="text-xs text-[#826F6A] font-mono mt-1">Depth 6 | 150 Trees</div>
        </div>

        <div className="editorial-card p-5 border-t-4 border-t-[#718A9E]">
          <div className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider">Model Accuracy</div>
          <div className="text-2xl sm:text-3xl font-mono font-bold text-[#718A9E] mt-1.5">
            0.7628
          </div>
          <div className="text-xs text-[#718A9E] font-medium mt-1">Authentic Test R²</div>
        </div>

        <div className="editorial-card p-5 border-t-4 border-t-[#BC7B6F]">
          <div className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider">Test Error (MAE)</div>
          <div className="text-2xl sm:text-3xl font-mono font-bold text-[#3D221C] mt-1.5">
            ₹ 28.64L
          </div>
          <div className="text-xs text-[#BC7B6F] font-medium mt-1">-60.4% vs Baseline</div>
        </div>

        <div className="editorial-card p-5 border-t-4 border-t-[#E4A499]">
          <div className="text-[11px] font-bold text-[#826F6A] uppercase tracking-wider">Inference Speed</div>
          <div className="text-2xl sm:text-3xl font-mono font-bold text-[#5A322A] mt-1.5">
            2.8 ms
          </div>
          <div className="text-xs text-[#826F6A] font-medium mt-1">Real-Time Prediction</div>
        </div>
      </div>

      {/* Two Column Section: Benchmark Chart & Research Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Benchmark Chart (7 cols) */}
        <div className="lg:col-span-7 editorial-card p-6 sm:p-8 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#BC7B6F]">
                Model Evaluation
              </span>
              <h3 className="text-lg font-serif font-bold text-[#3D221C]">
                Mean Absolute Error Across Architectures
              </h3>
            </div>
            <span className="editorial-badge-slate">
              Lower is Better
            </span>
          </div>

          <div className="h-64 sm:h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={benchmarkComparison} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8E4DC" vertical={false} />
                <XAxis dataKey="name" stroke="#826F6A" fontSize={11} tickLine={false} />
                <YAxis stroke="#826F6A" fontSize={11} tickLine={false} tickFormatter={(val) => `₹${val}L`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#CCCDC7', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                  formatter={(val: any) => [`₹ ${val} Lakhs`, 'Test MAE']}
                />
                <Bar dataKey="mae" fill="#BC7B6F" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p className="text-xs text-[#826F6A] leading-relaxed pt-2 border-t border-[#F0ECE6]">
            The tuned XGBoost pipeline cuts valuation error by <b>60.39%</b> compared to predicting the dataset average, demonstrating substantial predictive utility on genuine Bengaluru residential transactions.
          </p>
        </div>

        {/* Research Highlights (5 cols) */}
        <div className="lg:col-span-5 editorial-card p-6 sm:p-8 space-y-5">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#BC7B6F]">
            Methodological Standards
          </span>
          <h3 className="text-lg font-serif font-bold text-[#3D221C] -mt-3">
            Core Engineering Principles
          </h3>

          <div className="space-y-4 text-xs text-[#5A322A]">
            <div className="flex items-start gap-3">
              <div className="p-1.5 rounded-lg bg-[#FAF0ED] text-[#BC7B6F] shrink-0 mt-0.5">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-[#3D221C] block text-sm">Strict Leak Prevention</span>
                All preprocessors and categorical encoders are fitted strictly on the training partition to prevent held-out test contamination.
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-1.5 rounded-lg bg-[#EDF2F6] text-[#718A9E] shrink-0 mt-0.5">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-[#3D221C] block text-sm">Authentic Data Ingestion</span>
                Replaced artificial uniform distributions with verified Bengaluru housing records reflecting real location premiums.
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-1.5 rounded-lg bg-[#FAF0ED] text-[#BC7B6F] shrink-0 mt-0.5">
                <Award className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-[#3D221C] block text-sm">Empirical Explainability</span>
                Permutation importance proves that total floor area and micro-market locality account for the bulk of real estate valuation.
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Lifecycle Stages */}
      <div className="editorial-card p-6 sm:p-8 space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#BC7B6F]">
            Research Lifecycle
          </span>
          <h3 className="text-xl font-serif font-bold text-[#3D221C] mt-1">
            System Implementation Phases
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data?.lifecycle_stages?.map((stage) => (
            <div key={stage.phase} className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#BC7B6F]">Phase {stage.phase}</span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-[#FFFFFF] border border-[#CCCDC7] text-[#5A322A]">
                  {stage.badge}
                </span>
              </div>
              <h4 className="text-sm font-bold text-[#3D221C]">{stage.title}</h4>
              <p className="text-xs text-[#826F6A] leading-relaxed">{stage.summary}</p>
            </div>
          )) || null}
        </div>
      </div>

    </div>
  );
};
