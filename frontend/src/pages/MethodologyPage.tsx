import React from 'react';
import { 
  BookOpen, 
  ShieldCheck, 
  CheckCircle2, 
  Database, 
  Layers, 
  Cpu, 
  Award, 
  Building2,
  FileText
} from 'lucide-react';

export const MethodologyPage: React.FC = () => {
  return (
    <div className="space-y-10 animate-fadeIn max-w-5xl mx-auto">
      
      {/* Editorial Header */}
      <div className="pb-6 border-b border-[#E8E4DC]">
        <div className="flex items-center gap-2 mb-2">
          <span className="editorial-badge">
            <BookOpen className="w-3.5 h-3.5 text-[#BC7B6F]" />
            Engineering Documentation
          </span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-[#3D221C] tracking-tight">
          System Architecture & Research Methodology
        </h1>
        <p className="text-sm text-[#826F6A] mt-1">
          Comprehensive documentation of dataset provenance, leak-free pipeline engineering, model benchmarking, and explainability standards.
        </p>
      </div>

      {/* Section 1: Provenance & Dataset Upgrade */}
      <div className="editorial-card p-7 space-y-4">
        <div className="flex items-center gap-2 text-[#BC7B6F] font-bold text-sm uppercase tracking-wider">
          <Database className="w-4 h-4" />
          1. Dataset Ingestion & Domain Cleaning
        </div>
        <p className="text-xs sm:text-sm text-[#5A322A] leading-relaxed">
          The platform evaluates residential property valuations using the canonical <b>Bengaluru Residential Housing dataset</b>, 
          comprising 13,320 raw listings across 240+ distinct micro-markets.
        </p>

        <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] text-xs sm:text-sm space-y-2.5 text-[#5A322A]">
          <span className="font-bold text-[#3D221C] block text-xs uppercase tracking-wide">
            Key Data Standardization Steps:
          </span>
          <ul className="list-disc pl-5 space-y-1.5 text-[#826F6A] leading-relaxed text-xs">
            <li>
              <b>Floor Area Normalization:</b> Converted textual range entries (e.g. <code>"2100 - 2850"</code> to their arithmetic mean) and parsed non-standard units (Sq. Yards, Sq. Meters, Perches) into standardized Square Feet.
            </li>
            <li>
              <b>BHK Extraction:</b> Parsed unstructured size descriptions (e.g. <code>"2 BHK"</code>, <code>"4 Bedroom"</code>) into integer bedroom counts.
            </li>
            <li>
              <b>Physical Anomaly Filters:</b> Filtered records violating basic residential standards: requiring minimum <code>total_sqft / BHK &ge; 300</code> sq.ft. and <code>bath &le; BHK + 2</code>. Filtered extreme price per sq.ft. outliers (&lt; ₹ 1,500 or &gt; ₹ 35,000 / sqft).
            </li>
            <li>
              <b>High-Integrity Cleaned Partition:</b> Produced <b>12,496 validated listings</b> with genuine physical co-dependencies ($r = +0.7551$ between area and price).
            </li>
          </ul>
        </div>
      </div>

      {/* Section 2: Leakage Prevention & Preprocessing */}
      <div className="editorial-card p-7 space-y-4">
        <div className="flex items-center gap-2 text-[#718A9E] font-bold text-sm uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4" />
          2. Leak-Free Preprocessing Pipeline Design
        </div>
        <p className="text-xs sm:text-sm text-[#5A322A] leading-relaxed">
          To maintain strict academic and industry machine-learning discipline, transformations are isolated from test partitions:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-1.5">
            <div className="font-mono text-[#BC7B6F] font-bold">Strict 80 / 20 Train-Test Partitioning</div>
            <p className="text-[#826F6A] leading-relaxed">
              Data is deterministically split into 9,996 training rows and 2,500 held-out test rows (Seed 42). Test records are never seen by any preprocessor during fitting.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-1.5">
            <div className="font-mono text-[#718A9E] font-bold">Safe Out-of-Vocabulary Encoding</div>
            <p className="text-[#826F6A] leading-relaxed">
              <code>OneHotEncoder(handle_unknown='ignore')</code> guarantees that unseen localities or rare categories during inference are safely encoded with zero vectors without runtime errors.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-1.5">
            <div className="font-mono text-[#5A322A] font-bold">Scale-Appropriate Branching</div>
            <p className="text-[#826F6A] leading-relaxed">
              Linear models employ <code>StandardScaler()</code> on continuous numeric features, while tree architectures receive unscaled features to preserve natural split boundaries.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] space-y-1.5">
            <div className="font-mono text-[#BC7B6F] font-bold">Zero Target Leakage Guarantee</div>
            <p className="text-[#826F6A] leading-relaxed">
              No target-derived features (such as Price per Sq.Ft.) are permitted as input features. The target variable is exclusively predicted from legitimate property descriptors.
            </p>
          </div>
        </div>
      </div>

      {/* Section 3: Model Benchmarking & Results */}
      <div className="editorial-card p-7 space-y-4">
        <div className="flex items-center gap-2 text-[#BC7B6F] font-bold text-sm uppercase tracking-wider">
          <Cpu className="w-4 h-4" />
          3. Multi-Model Benchmark & Final Selection
        </div>
        <p className="text-xs sm:text-sm text-[#5A322A] leading-relaxed">
          Three candidate architectures were trained and compared on an 80/20 train/validation split (Seed 42):
        </p>

        <div className="space-y-3 text-xs text-[#5A322A]">
          <div className="p-3.5 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] flex justify-between items-center">
            <div>
              <span className="font-bold text-[#3D221C]">XGBoost Regressor (Selected Winner)</span>
              <p className="text-[#826F6A]">150 Trees, Max Depth 6, Learning Rate 0.08, Subsample 0.8</p>
            </div>
            <span className="font-mono font-bold text-[#BC7B6F]">Validation MAE: ₹ 32.48L | Test R²: 0.7628</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] flex justify-between items-center">
            <div>
              <span className="font-bold text-[#3D221C]">Random Forest Regressor</span>
              <p className="text-[#826F6A]">100 Trees, Max Depth 16, Min Samples Leaf 2</p>
            </div>
            <span className="font-mono text-[#826F6A]">Validation MAE: ₹ 32.61L | Test R²: 0.6855</span>
          </div>

          <div className="p-3.5 rounded-xl bg-[#FAF8F5] border border-[#E8E4DC] flex justify-between items-center">
            <div>
              <span className="font-bold text-[#3D221C]">Linear Regression (Ridge Regularization)</span>
              <p className="text-[#826F6A]">L2 Regularization (alpha = 1.0) with Standard Scaling</p>
            </div>
            <span className="font-mono text-[#826F6A]">Validation MAE: ₹ 37.36L | Test R²: 0.6422</span>
          </div>
        </div>
      </div>

      {/* Section 4: Operational Limitations */}
      <div className="editorial-card p-7 space-y-3">
        <h3 className="text-sm font-bold text-[#3D221C] uppercase tracking-wider">
          Commercial Usage Guidelines & Research Limitations
        </h3>
        <p className="text-xs text-[#826F6A] leading-relaxed">
          While the current XGBoost model demonstrates strong explanatory power (R² = 0.7628), real estate prices are subject to unobserved physical nuances: interior fitment quality, builder brand equity, view corridors, floor orientation, and individual negotiation margins. This system is created for research, scenario analysis, and comparative valuation; it is not certified for bank appraisal or statutory mortgage underwriting.
        </p>
      </div>

    </div>
  );
};
