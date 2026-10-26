import React, { useState, useEffect } from 'react';
import { api, ExplainabilityData } from '../api';
import { 
  Cpu, 
  HelpCircle, 
  ShieldCheck,
  TrendingUp,
  BarChart3,
  Layers,
  MapPin,
  Maximize2
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

export const ExplainabilityStudioPage: React.FC = () => {
  const [data, setData] = useState<ExplainabilityData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getExplainability()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load explainability data:', err);
        setLoading(false);
      });
  }, []);

  const permData = data?.permutation_importance.map((p) => ({
    feature: p.feature,
    impact: p.delta_mae_lakhs,
    direction: p.direction
  })) || [];

  const mdiData = data?.mdi_importance.map((m) => ({
    feature: m.feature,
    pct: m.pct
  })) || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Editorial Header */}
      <div className="pb-6 border-b border-[#E8E4DC]">
        <div className="flex items-center gap-2 mb-2">
          <span className="editorial-badge">
            <Cpu className="w-3.5 h-3.5 text-[#BC7B6F]" />
            Explainable Artificial Intelligence (XAI)
          </span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-[#3D221C] tracking-tight">
          Model Interpretation & Valuation Drivers
        </h1>
        <p className="text-sm text-[#826F6A] mt-1">
          Quantitative diagnostic analysis evaluating tree split feature weights and out-of-sample permutation error sensitivity.
        </p>
      </div>

      {/* Primary Key Takeaway Card */}
      <div className="editorial-card p-6 border-l-4 border-l-[#BC7B6F] flex items-start gap-4">
        <div className="p-2.5 rounded-xl bg-[#FAF0ED] text-[#BC7B6F] shrink-0">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div className="space-y-1 text-xs sm:text-sm">
          <h4 className="font-bold text-[#3D221C] uppercase tracking-wide text-xs">
            Core Real Estate Valuation Principle: Area & Micro-Market Dominance
          </h4>
          <p className="text-[#826F6A] leading-relaxed">
            In residential real estate economics, property value is primarily driven by <b>Floor Area</b> and <b>Micro-Market Locality</b>. Out-of-sample permutation tests confirm that randomly shuffling <code className="text-[#5A322A] font-bold">total_sqft</code> causes an immediate <b>+₹ 44.20 Lakhs MAE error spike</b>, validating that the XGBoost model has captured legitimate physical relationships rather than memorizing noise.
          </p>
        </div>
      </div>

      {/* Two Column Grid: Permutation Impact vs. MDI Weights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        
        {/* Left: Permutation Importance (Gold Standard) */}
        <div className="editorial-card p-6 sm:p-7 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#BC7B6F]">
                Test Set Sensitivity
              </span>
              <h3 className="text-base font-serif font-bold text-[#3D221C]">
                Permutation Importance (MAE Increase in ₹ Lakhs)
              </h3>
            </div>
            <span className="editorial-badge">
              Out-of-Sample
            </span>
          </div>

          <p className="text-xs text-[#826F6A]">
            Measures how much the model's test error worsens when a feature is randomly shuffled. Higher indicates greater true economic impact.
          </p>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={permData} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8E4DC" horizontal={false} />
                <XAxis type="number" stroke="#826F6A" fontSize={10} tickFormatter={(v) => `+₹${v}L`} />
                <YAxis dataKey="feature" type="category" stroke="#826F6A" fontSize={11} width={90} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#CCCDC7', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                  formatter={(v: any) => [`+₹ ${v} Lakhs error increase`, 'Permutation Impact']}
                />
                <Bar dataKey="impact" fill="#BC7B6F" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: MDI Tree Split Weights */}
        <div className="editorial-card p-6 sm:p-7 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#718A9E]">
                Tree Split Architecture
              </span>
              <h3 className="text-base font-serif font-bold text-[#3D221C]">
                Mean Decrease in Impurity (MDI Share %)
              </h3>
            </div>
            <span className="editorial-badge-slate">
              Internal Splits
            </span>
          </div>

          <p className="text-xs text-[#826F6A]">
            Internal tree split contribution across all boosting iterations. Location dominates due to high-dimensional locality branching.
          </p>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mdiData} layout="vertical" margin={{ top: 5, right: 20, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8E4DC" horizontal={false} />
                <XAxis type="number" stroke="#826F6A" fontSize={10} tickFormatter={(v) => `${v}%`} />
                <YAxis dataKey="feature" type="category" stroke="#826F6A" fontSize={11} width={90} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#FFFFFF', borderColor: '#CCCDC7', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                  formatter={(v: any) => [`${v}%`, 'MDI Share']}
                />
                <Bar dataKey="pct" fill="#718A9E" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Feature Narrative Table */}
      <div className="editorial-card p-6 sm:p-7 space-y-4">
        <h3 className="text-base font-serif font-bold text-[#3D221C]">
          Economic Narrative of Model Predictors
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-2">
            <div className="flex items-center gap-2 text-[#BC7B6F] font-bold text-sm">
              <Maximize2 className="w-4 h-4" /> Total Floor Area
            </div>
            <p className="text-[#826F6A] leading-relaxed">
              Acts as the core linear and non-linear scale factor. In Bengaluru, base rate multiplier scales directly with usable square footage.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-2">
            <div className="flex items-center gap-2 text-[#718A9E] font-bold text-sm">
              <MapPin className="w-4 h-4" /> Locality Premium
            </div>
            <p className="text-[#826F6A] leading-relaxed">
              Differentiates established central hubs (Indiranagar, Koramangala at ₹ 15,000–25,000/sqft) from developing corridors (Electronic City, Chandapura at ₹ 3,500–6,000/sqft).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-2">
            <div className="flex items-center gap-2 text-[#5A322A] font-bold text-sm">
              <Layers className="w-4 h-4" /> Layout & Area Type
            </div>
            <p className="text-[#826F6A] leading-relaxed">
              Distinguishes independent plot developments and standalone homes from high-density super built-up apartment complexes.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
};
