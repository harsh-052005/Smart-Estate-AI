import React, { useState, useEffect } from 'react';
import { api, ModelBenchmarks } from '../api';
import { 
  FlaskConical, 
  Award, 
  HelpCircle, 
  TrendingUp, 
  CheckCircle2, 
  Timer,
  Gauge
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

export const ModelPerformanceLabPage: React.FC = () => {
  const [data, setData] = useState<ModelBenchmarks | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getModels()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load benchmarks:', err);
        setLoading(false);
      });
  }, []);

  const chartData = data?.validation_benchmark.map((m) => ({
    name: m.model,
    mae: m.mae_lakhs,
    rmse: m.rmse_lakhs,
    r2: m.r2_score,
    time: m.train_time_sec
  })) || [];

  return (
    <div className="space-y-8 animate-fadeIn">
      
      {/* Editorial Header */}
      <div className="pb-6 border-b border-[#E8E4DC]">
        <div className="flex items-center gap-2 mb-2">
          <span className="editorial-badge">
            <FlaskConical className="w-3.5 h-3.5 text-[#BC7B6F]" />
            Machine Learning Evaluation
          </span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-[#3D221C] tracking-tight">
          Model Performance & Benchmarking Lab
        </h1>
        <p className="text-sm text-[#826F6A] mt-1">
          Comparative empirical benchmarking across candidate regression architectures evaluated on reproducible train, validation, and held-out test splits.
        </p>
      </div>

      {/* Regression vs Classification Callout */}
      <div className="editorial-card p-5 border-l-4 border-l-[#718A9E] flex items-start gap-4">
        <div className="p-2 rounded-lg bg-[#EDF2F6] text-[#718A9E] shrink-0">
          <HelpCircle className="w-5 h-5" />
        </div>
        <div className="space-y-1 text-xs sm:text-sm">
          <h4 className="font-bold text-[#3D221C] uppercase tracking-wide text-xs">
            Methodological Notice: Continuous Regression vs. Classification
          </h4>
          <p className="text-[#826F6A] leading-relaxed">
            Property price valuation is a continuous numerical estimation task. Performance is evaluated using <b>Mean Absolute Error (MAE)</b>, <b>Root Mean Squared Error (RMSE)</b>, and the <b>Coefficient of Determination (R²)</b>. Concepts such as classification accuracy, precision, recall, confusion matrices, or F1-scores do not apply to real estate regression modeling.
          </p>
        </div>
      </div>

      {/* Candidate Benchmark Table */}
      <div className="editorial-card overflow-hidden">
        <div className="p-5 border-b border-[#E8E4DC] bg-[#FAF8F5] flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-[#3D221C] flex items-center gap-2">
              <Award className="w-4 h-4 text-[#BC7B6F]" />
              Candidate Models Validation Benchmark (n = 2,000 validation rows)
            </h3>
            <p className="text-xs text-[#826F6A]">All models fitted on raw training partition (8,000 sub-training rows, random seed 42).</p>
          </div>
          <span className="text-[11px] font-mono text-[#BC7B6F] bg-[#FAF0ED] px-2.5 py-1 rounded-full border border-[#E8DCD6]">
            Phase 4 Verified
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#5A322A]">
            <thead className="bg-[#FAF8F5] border-b border-[#E8E4DC] text-[11px] font-bold text-[#826F6A] uppercase tracking-wider">
              <tr>
                <th className="px-5 py-3">Model Architecture</th>
                <th className="px-5 py-3">Validation MAE</th>
                <th className="px-5 py-3">Validation RMSE</th>
                <th className="px-5 py-3">Validation R²</th>
                <th className="px-5 py-3">Training Time</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F0ECE6]">
              {data?.validation_benchmark.map((m) => (
                <tr key={m.model} className={m.winner ? 'bg-[#FDF9F7] font-semibold' : 'hover:bg-[#FAF8F5]'}>
                  <td className="px-5 py-3.5 text-[#3D221C] font-semibold flex items-center gap-2">
                    {m.model}
                    {m.winner && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#BC7B6F] text-[#FAF8F5]">
                        Selected Winner
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-[#BC7B6F] font-bold">₹ {m.mae_lakhs}L</td>
                  <td className="px-5 py-3.5 font-mono text-[#5A322A]">₹ {m.rmse_lakhs}L</td>
                  <td className="px-5 py-3.5 font-mono text-[#718A9E]">{m.r2_score.toFixed(4)}</td>
                  <td className="px-5 py-3.5 font-mono text-[#826F6A]">{m.train_time_sec}s</td>
                  <td className="px-5 py-3.5">
                    {m.winner ? (
                      <span className="text-emerald-700 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Optimal MAE
                      </span>
                    ) : (
                      <span className="text-[#826F6A]">Evaluated</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Two Column Grid: Test Evaluation & Baseline Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Held-Out Test Evaluation */}
        <div className="editorial-card p-6 sm:p-7 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#BC7B6F]">
                Final Model Verification
              </span>
              <h3 className="text-base font-serif font-bold text-[#3D221C]">
                Untouched Test Set Evaluation (n = 2,500)
              </h3>
            </div>
            <span className="editorial-badge-slate">
              Zero Leakage
            </span>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex justify-between items-center p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC]">
              <span className="text-xs text-[#826F6A]">Test MAE (Mean Absolute Error)</span>
              <span className="text-base font-mono font-bold text-[#BC7B6F]">₹ {data?.final_test_evaluation.mae_lakhs}L</span>
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC]">
              <span className="text-xs text-[#826F6A]">Test RMSE</span>
              <span className="text-base font-mono font-bold text-[#5A322A]">₹ {data?.final_test_evaluation.rmse_lakhs}L</span>
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC]">
              <span className="text-xs text-[#826F6A]">Coefficient of Determination (R²)</span>
              <span className="text-base font-mono font-bold text-[#718A9E]">{data?.final_test_evaluation.r2_score.toFixed(4)}</span>
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC]">
              <span className="text-xs text-[#826F6A]">Throughput Rate</span>
              <span className="text-xs font-mono font-bold text-[#5A322A]">{data?.final_test_evaluation.rows_per_second.toLocaleString()} rows / sec</span>
            </div>
          </div>
        </div>

        {/* Baseline Comparison */}
        <div className="editorial-card p-6 sm:p-7 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#F0ECE6]">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#BC7B6F]">
                Baseline Comparison
              </span>
              <h3 className="text-base font-serif font-bold text-[#3D221C]">
                Model vs. Training-Mean Baseline
              </h3>
            </div>
            <span className="editorial-badge">
              60.4% Gain
            </span>
          </div>

          <p className="text-xs text-[#826F6A] leading-relaxed">
            Comparing the trained XGBoost model against a simple baseline that predicts the training-set mean (₹ {data?.baseline_comparison.baseline_value_lakhs}L) for all properties:
          </p>

          <div className="space-y-3 pt-2">
            <div className="flex justify-between items-center p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC]">
              <span className="text-xs text-[#826F6A]">Baseline MAE (Mean Guess)</span>
              <span className="text-sm font-mono text-[#826F6A]">₹ {data?.baseline_comparison.baseline_mae_lakhs}L</span>
            </div>

            <div className="flex justify-between items-center p-3 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC]">
              <span className="text-xs text-[#826F6A]">XGBoost Model MAE</span>
              <span className="text-sm font-mono font-bold text-[#BC7B6F]">₹ {data?.baseline_comparison.model_mae_lakhs}L</span>
            </div>

            <div className="flex justify-between items-center p-3.5 rounded-xl bg-[#FAF0ED] border border-[#E4A499]">
              <span className="text-xs font-bold text-[#3D221C]">Absolute Error Reduction</span>
              <span className="text-sm font-mono font-extrabold text-[#BC7B6F]">{data?.baseline_comparison.mae_delta_lakhs}L (-{data?.baseline_comparison.relative_improvement_pct}%)</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};
