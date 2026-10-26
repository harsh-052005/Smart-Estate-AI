/**
 * Smart Estate AI — API Service & Types (Bengaluru Housing)
 */

export interface OverviewData {
  kpis: {
    total_properties: number;
    training_partition_rows: number;
    test_partition_rows: number;
    selected_model: string;
    model_hyperparameters: string;
    test_mae_lakhs: number;
    test_mae_inr: string;
    test_rmse_lakhs: number;
    test_rmse_inr: string;
    test_r2_score: number;
    baseline_mae_lakhs: number;
    baseline_r2_score: number;
  };
  lifecycle_stages: Array<{
    phase: number;
    title: string;
    summary: string;
    badge: string;
  }>;
  warning_notice: string;
}

export interface PropertyRecord {
  id: number;
  location: string;
  area_type: string;
  availability: string;
  bhk: number;
  bath: number;
  balcony: number;
  size_sqft: number;
  price_lakhs: number;
  price_inr_formatted: string;
  price_per_sqft: number;
}

export interface PropertiesResponse {
  total_records: number;
  page: number;
  page_size: number;
  total_pages: number;
  summary: {
    avg_price_lakhs: number;
    avg_price_inr: string;
    median_price_lakhs: number;
    avg_size_sqft: number;
    avg_price_per_sqft: number;
  };
  records: PropertyRecord[];
}

export interface PropertyAnalytics {
  price_distribution: Array<{ range: string; count: number }>;
  bhk_distribution: Array<{ bhk: number; count: number; avg_price: number }>;
  property_type_distribution: Array<{ type: string; count: number; avg_price: number }>;
  top_localities: Array<{ location: string; avg_price: number; count: number }>;
}

export interface ModelBenchmarks {
  validation_benchmark: Array<{
    model: string;
    mae_lakhs: number;
    rmse_lakhs: number;
    r2_score: number;
    mae_inr: string;
    rmse_inr: string;
    train_time_sec: number;
    infer_time_sec: number;
    winner: boolean;
  }>;
  final_test_evaluation: {
    model_name: string;
    test_rows: number;
    mae_lakhs: number;
    mae_inr: string;
    rmse_lakhs: number;
    rmse_inr: string;
    r2_score: number;
    inference_duration_sec: number;
    rows_per_second: number;
  };
  baseline_comparison: {
    strategy: string;
    baseline_value_lakhs: number;
    baseline_mae_lakhs: number;
    baseline_rmse_lakhs: number;
    baseline_r2_score: number;
    model_mae_lakhs: number;
    mae_delta_lakhs: number;
    mae_delta_inr: string;
    relative_improvement_pct: number;
  };
}

export interface ExplainabilityData {
  mdi_importance: Array<{
    feature: string;
    importance: number;
    pct: number;
    type: string;
  }>;
  permutation_importance: Array<{
    feature: string;
    delta_mae_lakhs: number;
    std: number;
    impact_inr: string;
    direction: string;
  }>;
}

export interface PredictionPayload {
  location: string;
  total_sqft: number;
  bhk: number;
  bath: number;
  balcony: number;
  area_type: string;
  availability: string;
}

export interface PredictionResult {
  predicted_price_lakhs: number;
  predicted_price_inr: number;
  formatted_lakhs: string;
  formatted_inr: string;
  price_per_sqft: number;
  baseline_training_mean_lakhs: number;
  model_name: string;
  r2_score: number;
  mae_lakhs: number;
  inference_time_ms: number;
  market_context: string;
}

export interface MetaData {
  locations: string[];
  area_types: string[];
  availabilities: string[];
  bhk_options: number[];
  bath_options: number[];
  balcony_options: number[];
  price_bounds: { min: number; max: number; mean: number; median: number };
  size_bounds: { min: number; max: number; mean: number; median: number };
}

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export const api = {
  getHealth: async () => {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  },

  getMeta: async (): Promise<MetaData> => {
    const res = await fetch(`${API_BASE}/meta`);
    if (!res.ok) throw new Error('Failed to load metadata');
    return res.json();
  },

  getOverview: async (): Promise<OverviewData> => {
    const res = await fetch(`${API_BASE}/overview`);
    if (!res.ok) throw new Error('Failed to load overview data');
    return res.json();
  },

  getProperties: async (params: {
    page?: number;
    page_size?: number;
    location?: string;
    area_type?: string;
    bhk?: number | null;
    min_price?: number | null;
    max_price?: number | null;
    min_size?: number | null;
    max_size?: number | null;
    search?: string;
  }): Promise<PropertiesResponse> => {
    const query = new URLSearchParams();
    if (params.page) query.set('page', params.page.toString());
    if (params.page_size) query.set('page_size', params.page_size.toString());
    if (params.location && params.location !== 'All') query.set('location', params.location);
    if (params.area_type && params.area_type !== 'All') query.set('area_type', params.area_type);
    if (params.bhk !== undefined && params.bhk !== null) query.set('bhk', params.bhk.toString());
    if (params.min_price !== undefined && params.min_price !== null) query.set('min_price', params.min_price.toString());
    if (params.max_price !== undefined && params.max_price !== null) query.set('max_price', params.max_price.toString());
    if (params.min_size !== undefined && params.min_size !== null) query.set('min_size', params.min_size.toString());
    if (params.max_size !== undefined && params.max_size !== null) query.set('max_size', params.max_size.toString());
    if (params.search) query.set('search', params.search);

    const res = await fetch(`${API_BASE}/properties?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to load properties');
    return res.json();
  },

  getAnalytics: async (params?: {
    location?: string;
    area_type?: string;
  }): Promise<PropertyAnalytics> => {
    const query = new URLSearchParams();
    if (params?.location && params.location !== 'All') query.set('location', params.location);
    if (params?.area_type && params.area_type !== 'All') query.set('area_type', params.area_type);

    const res = await fetch(`${API_BASE}/properties/analytics?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to load property analytics');
    return res.json();
  },

  getModels: async (): Promise<ModelBenchmarks> => {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to load model benchmarks');
    return res.json();
  },

  getExplainability: async (): Promise<ExplainabilityData> => {
    const res = await fetch(`${API_BASE}/explainability`);
    if (!res.ok) throw new Error('Failed to load explainability data');
    return res.json();
  },

  predict: async (payload: PredictionPayload): Promise<PredictionResult> => {
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        let msg = 'Inference failed';
        if (typeof err.detail === 'string') {
          msg = err.detail;
        } else if (Array.isArray(err.detail)) {
          msg = err.detail.map((e: any) => `${e.loc?.slice(-1)[0] || 'field'}: ${e.msg}`).join(', ');
        }
        throw new Error(msg);
      }
      return res.json();
    } catch (err: any) {
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        throw new Error('Unable to reach backend server on port 8000. Please ensure FastAPI is running.');
      }
      throw err;
    }
  }
};
