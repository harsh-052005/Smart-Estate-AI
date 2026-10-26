"""
================================================================================
  SMART ESTATE AI — FastAPI Backend Server (Bengaluru Housing)
  File   : backend/main.py
  Purpose: Production API layer serving real-time model predictions,
           dataset exploration queries, benchmarking metrics, and explainability data.
================================================================================
"""

import os
import sys
import io
import time
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLEAN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "bengaluru_cleaned.csv")
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "bengaluru_house_prices.csv")
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "best_model.joblib")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

app = FastAPI(
    title="Smart Estate AI API",
    description="High-performance PropTech analytics & machine-learning inference backend.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PIPELINE = None
DF_HOUSING = None
LOCATIONS_LIST: List[str] = []


def format_inr(lakhs: float) -> str:
    rupees = int(round(lakhs * 100_000))
    s = str(abs(rupees))
    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        rem = s[:-3]
        groups = []
        while len(rem) > 2:
            groups.append(rem[-2:])
            rem = rem[:-2]
        if rem:
            groups.append(rem)
        groups.reverse()
        res = ",".join(groups) + "," + last3
    return f"-₹ {res}" if rupees < 0 else f"₹ {res}"


def load_backend_artifacts():
    global MODEL_PIPELINE, DF_HOUSING, LOCATIONS_LIST

    if os.path.exists(MODEL_PATH):
        try:
            MODEL_PIPELINE = joblib.load(MODEL_PATH)
            print(f"[OK] Loaded ML pipeline from {MODEL_PATH}")
        except Exception as e:
            print(f"[ERROR] Failed to load model pipeline: {e}")
            MODEL_PIPELINE = None
    else:
        print(f"[WARNING] Model artifact not found at {MODEL_PATH}")

    data_file = CLEAN_DATA_PATH if os.path.exists(CLEAN_DATA_PATH) else RAW_DATA_PATH
    if os.path.exists(data_file):
        try:
            DF_HOUSING = pd.read_csv(data_file)
            print(f"[OK] Loaded dataset ({data_file}): {len(DF_HOUSING):,} rows")
            LOCATIONS_LIST = sorted(list(DF_HOUSING["location"].dropna().unique()))
        except Exception as e:
            print(f"[ERROR] Failed to load dataset: {e}")
            DF_HOUSING = None
    else:
        print(f"[WARNING] Dataset not found at {data_file}")


load_backend_artifacts()


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

class PredictionRequest(BaseModel):
    location: str = Field(default="Whitefield", description="Locality in Bengaluru")
    total_sqft: float = Field(default=1200.0, ge=300, le=10000, description="Total size in square feet")
    bhk: int = Field(default=2, ge=1, le=10, description="Number of bedrooms (BHK)")
    bath: int = Field(default=2, ge=1, le=10, description="Number of bathrooms")
    balcony: int = Field(default=1, ge=0, le=5, description="Number of balconies")
    area_type: str = Field(default="Super built-up  Area", description="Area classification")
    availability: str = Field(default="Ready To Move", description="Possession readiness")


class PredictionResponse(BaseModel):
    predicted_price_lakhs: float
    predicted_price_inr: int
    formatted_lakhs: str
    formatted_inr: str
    price_per_sqft: float
    baseline_training_mean_lakhs: float
    model_name: str
    r2_score: float
    mae_lakhs: float
    inference_time_ms: float
    market_context: str


# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Smart Estate AI API (Bengaluru Edition)",
        "model_loaded": MODEL_PIPELINE is not None,
        "dataset_loaded": DF_HOUSING is not None,
        "dataset_records": len(DF_HOUSING) if DF_HOUSING is not None else 0,
        "timestamp": time.time()
    }


@app.get("/api/meta")
def get_metadata():
    if DF_HOUSING is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded.")

    return {
        "locations": LOCATIONS_LIST,
        "area_types": sorted(list(DF_HOUSING["area_type"].dropna().unique())),
        "availabilities": ["Ready To Move", "Under Construction"],
        "bhk_options": [1, 2, 3, 4, 5, 6],
        "bath_options": [1, 2, 3, 4, 5],
        "balcony_options": [0, 1, 2, 3],
        "price_bounds": {
            "min": float(DF_HOUSING["price"].min()),
            "max": float(DF_HOUSING["price"].max()),
            "mean": float(DF_HOUSING["price"].mean()),
            "median": float(DF_HOUSING["price"].median())
        },
        "size_bounds": {
            "min": float(DF_HOUSING["total_sqft"].min()),
            "max": float(DF_HOUSING["total_sqft"].max()),
            "mean": float(DF_HOUSING["total_sqft"].mean()),
            "median": float(DF_HOUSING["total_sqft"].median())
        }
    }


@app.get("/api/overview")
def get_overview_data():
    return {
        "kpis": {
            "total_properties": 12496,
            "training_partition_rows": 9996,
            "test_partition_rows": 2500,
            "selected_model": "XGBoost Regressor (Tuned)",
            "model_hyperparameters": "150 Trees, Max Depth 6, Learning Rate 0.08",
            "test_mae_lakhs": 28.64,
            "test_mae_inr": "₹ 28,63,909",
            "test_rmse_lakhs": 66.96,
            "test_rmse_inr": "₹ 66,95,876",
            "test_r2_score": 0.7628,
            "baseline_mae_lakhs": 72.30,
            "baseline_r2_score": -0.0003
        },
        "lifecycle_stages": [
            {
                "phase": 1,
                "title": "Dataset Provenance Upgrade",
                "summary": "Replaced synthetic dataset with verified canonical Bengaluru residential housing data (13,320 records).",
                "badge": "Real Data Ingested"
            },
            {
                "phase": 2,
                "title": "Domain Cleaning & Unit Normalization",
                "summary": "Parsed total_sqft unit variations and ranges, extracted BHK numbers, removed corrupt entries (sqft/BHK < 300).",
                "badge": "12,496 Cleaned Records"
            },
            {
                "phase": 3,
                "title": "Leak-Free Preprocessing & Splits",
                "summary": "Partitioned 80/20 train/test. OneHotEncoder fitted strictly on training partition with handle_unknown='ignore'.",
                "badge": "247 Transformed Features"
            },
            {
                "phase": 4,
                "title": "Model Benchmarking & Selection",
                "summary": "Trained Ridge, Random Forest, and XGBoost. XGBoost achieved winning validation MAE (₹ 32.48L) and Test R² of 0.7628.",
                "badge": "R² = 0.7628"
            },
            {
                "phase": 5,
                "title": "Baseline Comparison & Error Analysis",
                "summary": "Slashed test MAE by 60.39% compared to predicting training mean (₹ 28.64L vs ₹ 72.30L baseline).",
                "badge": "-60.4% Error Reduction"
            },
            {
                "phase": 6,
                "title": "Explainability & Feature Drivers",
                "summary": "Established total_sqft and location as the dominant economic drivers (+₹ 44.2L error on total_sqft permutation).",
                "badge": "Explainability Verified"
            }
        ],
        "warning_notice": "Bengaluru real estate valuation model. Predictions reflect genuine market dynamics across 240+ localities."
    }


@app.get("/api/properties")
def query_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    location: Optional[str] = None,
    area_type: Optional[str] = None,
    bhk: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_size: Optional[float] = None,
    max_size: Optional[float] = None,
    search: Optional[str] = None
):
    if DF_HOUSING is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded.")

    df = DF_HOUSING

    if location and location != "All":
        df = df[df["location"] == location]

    if area_type and area_type != "All":
        df = df[df["area_type"] == area_type]

    if bhk is not None:
        df = df[df["bhk"] == bhk]

    if min_price is not None:
        df = df[df["price"] >= min_price]
    if max_price is not None:
        df = df[df["price"] <= max_price]

    if min_size is not None:
        df = df[df["total_sqft"] >= min_size]
    if max_size is not None:
        df = df[df["total_sqft"] <= max_size]

    if search:
        s = search.lower()
        df = df[df["location"].str.lower().str.contains(s, na=False)]

    total_count = len(df)

    if total_count > 0:
        avg_price = float(df["price"].mean())
        median_price = float(df["price"].median())
        avg_size = float(df["total_sqft"].mean())
        avg_price_per_sqft = float(df["price_per_sqft"].mean())
    else:
        avg_price = median_price = avg_size = avg_price_per_sqft = 0.0

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_df = df.iloc[start_idx:end_idx]

    records = []
    for idx, row in page_df.iterrows():
        p = float(row.get("price", 0))
        records.append({
            "id": int(idx),
            "location": str(row.get("location", "")),
            "area_type": str(row.get("area_type", "")),
            "availability": str(row.get("availability", "")),
            "bhk": int(row.get("bhk", 0)),
            "bath": int(row.get("bath", 0)),
            "balcony": int(row.get("balcony", 0)),
            "size_sqft": round(float(row.get("total_sqft", 0)), 1),
            "price_lakhs": round(p, 2),
            "price_inr_formatted": format_inr(p),
            "price_per_sqft": round(float(row.get("price_per_sqft", 0)), 0),
        })

    return {
        "total_records": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": int(np.ceil(total_count / page_size)) if total_count > 0 else 0,
        "summary": {
            "avg_price_lakhs": round(avg_price, 2),
            "avg_price_inr": format_inr(avg_price),
            "median_price_lakhs": round(median_price, 2),
            "avg_size_sqft": round(avg_size, 0),
            "avg_price_per_sqft": round(avg_price_per_sqft, 0)
        },
        "records": records
    }


@app.get("/api/properties/analytics")
def get_property_analytics(
    location: Optional[str] = None,
    area_type: Optional[str] = None
):
    if DF_HOUSING is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded.")

    df = DF_HOUSING
    if location and location != "All":
        df = df[df["location"] == location]
    if area_type and area_type != "All":
        df = df[df["area_type"] == area_type]

    # Price Distribution
    price_bins = [0, 40, 70, 100, 150, 200, 300, 500, 1000]
    price_labels = ["<40L", "40-70L", "70-100L", "100-150L", "150-200L", "200-300L", "300-500L", "500L+"]
    binned = pd.cut(df["price"], bins=price_bins, labels=price_labels)
    price_dist = binned.value_counts().sort_index().to_dict()

    # BHK breakdown
    bhk_grp = df.groupby("bhk")["price"].agg(["count", "mean"]).reset_index()
    bhk_data = [
        {"bhk": int(r["bhk"]), "count": int(r["count"]), "avg_price": round(float(r["mean"]), 2)}
        for _, r in bhk_grp.iterrows() if int(r["bhk"]) <= 6
    ]

    # Area Type breakdown
    at_grp = df.groupby("area_type")["price"].agg(["count", "mean"]).reset_index()
    at_data = [
        {"type": str(r["area_type"]), "count": int(r["count"]), "avg_price": round(float(r["mean"]), 2)}
        for _, r in at_grp.iterrows()
    ]

    # Top Localities
    top_locs = DF_HOUSING.groupby("location")["price"].agg(["count", "mean"]).reset_index()
    top_locs = top_locs[top_locs["count"] >= 30].sort_values(by="mean", ascending=False).head(15)
    loc_rankings = [
        {"location": str(r["location"]), "avg_price": round(float(r["mean"]), 2), "count": int(r["count"])}
        for _, r in top_locs.iterrows()
    ]

    return {
        "price_distribution": [{"range": k, "count": int(v)} for k, v in price_dist.items()],
        "bhk_distribution": bhk_data,
        "property_type_distribution": at_data,
        "top_localities": loc_rankings
    }


@app.get("/api/properties/export")
def export_filtered_properties(
    location: Optional[str] = None,
    area_type: Optional[str] = None,
    bhk: Optional[int] = None,
    limit: int = Query(1000, le=5000)
):
    if DF_HOUSING is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded.")

    df = DF_HOUSING
    if location and location != "All":
        df = df[df["location"] == location]
    if area_type and area_type != "All":
        df = df[df["area_type"] == area_type]
    if bhk is not None:
        df = df[df["bhk"] == bhk]

    export_subset = df.head(limit)
    csv_stream = io.StringIO()
    export_subset.to_csv(csv_stream, index=False)
    csv_stream.seek(0)

    return StreamingResponse(
        iter([csv_stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=bengaluru_properties_export_{int(time.time())}.csv"}
    )


@app.get("/api/models")
def get_model_benchmarks():
    return {
        "validation_benchmark": [
            {
                "model": "XGBoost",
                "mae_lakhs": 32.48,
                "rmse_lakhs": 94.06,
                "r2_score": 0.6446,
                "mae_inr": "₹ 32,47,937",
                "rmse_inr": "₹ 94,06,386",
                "train_time_sec": 0.30,
                "infer_time_sec": 0.0055,
                "winner": True
            },
            {
                "model": "Random Forest",
                "mae_lakhs": 32.61,
                "rmse_lakhs": 88.48,
                "r2_score": 0.6855,
                "mae_inr": "₹ 32,61,129",
                "rmse_inr": "₹ 88,47,961",
                "train_time_sec": 0.67,
                "infer_time_sec": 0.0195,
                "winner": False
            },
            {
                "model": "Linear Regression (Ridge)",
                "mae_lakhs": 37.36,
                "rmse_lakhs": 94.38,
                "r2_score": 0.6422,
                "mae_inr": "₹ 37,36,017",
                "rmse_inr": "₹ 94,38,485",
                "train_time_sec": 0.05,
                "infer_time_sec": 0.0044,
                "winner": False
            }
        ],
        "final_test_evaluation": {
            "model_name": "XGBoost Regressor (Trained on 9,996 rows)",
            "test_rows": 2500,
            "mae_lakhs": 28.64,
            "mae_inr": "₹ 28,63,909",
            "rmse_lakhs": 66.96,
            "rmse_inr": "₹ 66,95,876",
            "r2_score": 0.7628,
            "inference_duration_sec": 0.0069,
            "rows_per_second": 362318
        },
        "baseline_comparison": {
            "strategy": "Constant Mean Predictor (fitted on y_train)",
            "baseline_value_lakhs": 110.15,
            "baseline_mae_lakhs": 72.30,
            "baseline_rmse_lakhs": 137.52,
            "baseline_r2_score": -0.0003,
            "model_mae_lakhs": 28.64,
            "mae_delta_lakhs": -43.67,
            "mae_delta_inr": "-₹ 43,66,516",
            "relative_improvement_pct": 60.39
        }
    }


@app.get("/api/explainability")
def get_explainability_data():
    return {
        "mdi_importance": [
            {"feature": "Location", "importance": 0.8137, "pct": 81.37, "type": "Categorical Micro-Market Premium"},
            {"feature": "Total Sq.Ft.", "importance": 0.0687, "pct": 6.87, "type": "Continuous Primary Scale Metric"},
            {"feature": "Area Type", "importance": 0.0516, "pct": 5.16, "type": "Categorical Area Classification"},
            {"feature": "Availability", "importance": 0.0237, "pct": 2.37, "type": "Ready to Move vs Construction"},
            {"feature": "BHK Count", "importance": 0.0190, "pct": 1.90, "type": "Discrete Bedroom Configuration"},
            {"feature": "Bathrooms", "importance": 0.0145, "pct": 1.45, "type": "Discrete Bathroom Count"},
            {"feature": "Balconies", "importance": 0.0087, "pct": 0.87, "type": "Discrete Balcony Count"}
        ],
        "permutation_importance": [
            {"feature": "Total Sq.Ft.", "delta_mae_lakhs": 44.20, "std": 1.82, "impact_inr": "₹ 44,20,000", "direction": "Highest Economic Impact"},
            {"feature": "Location", "delta_mae_lakhs": 5.73, "std": 0.65, "impact_inr": "₹ 5,73,000", "direction": "Strong Local Premium"},
            {"feature": "Bathrooms", "delta_mae_lakhs": 4.83, "std": 0.42, "impact_inr": "₹ 4,83,000", "direction": "High Utility Weight"},
            {"feature": "Area Type", "delta_mae_lakhs": 3.05, "std": 0.38, "impact_inr": "₹ 3,05,000", "direction": "Plot / Super Built-up Diff"},
            {"feature": "BHK Count", "delta_mae_lakhs": 2.81, "std": 0.35, "impact_inr": "₹ 2,81,000", "direction": "Configuration Weight"},
            {"feature": "Availability", "delta_mae_lakhs": 0.24, "std": 0.12, "impact_inr": "₹ 24,000", "direction": "Ready-to-Move Premium"},
            {"feature": "Balconies", "delta_mae_lakhs": -0.13, "std": 0.08, "impact_inr": "-₹ 13,000", "direction": "Minor Marginal Variation"}
        ]
    }


@app.post("/api/predict", response_model=PredictionResponse)
def predict_property_price(req: PredictionRequest):
    if MODEL_PIPELINE is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning model pipeline (models/best_model.joblib) is not available on server."
        )

    t_start = time.time()

    row_dict = {
        "total_sqft": float(req.total_sqft),
        "bhk": int(req.bhk),
        "bath": int(req.bath),
        "balcony": int(req.balcony),
        "location": str(req.location).strip(),
        "area_type": str(req.area_type).strip(),
        "availability": str(req.availability).strip()
    }
    input_df = pd.DataFrame([row_dict])

    try:
        pred_val = float(MODEL_PIPELINE.predict(input_df)[0])
        # Floor price at reasonable minimum if extreme negative extrapolation occurs
        pred_val = max(10.0, pred_val)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference pipeline execution error: {str(e)}"
        )

    inference_ms = round((time.time() - t_start) * 1000, 2)
    inr_val = int(round(pred_val * 100_000))
    pps = round((pred_val * 100_000) / req.total_sqft, 0)

    return PredictionResponse(
        predicted_price_lakhs=round(pred_val, 2),
        predicted_price_inr=inr_val,
        formatted_lakhs=f"₹ {pred_val:,.2f} Lakhs",
        formatted_inr=format_inr(pred_val),
        price_per_sqft=pps,
        baseline_training_mean_lakhs=110.15,
        model_name="XGBoost Regressor (Bengaluru PropTech Engine)",
        r2_score=0.7628,
        mae_lakhs=28.64,
        inference_time_ms=inference_ms,
        market_context=f"Valuation estimated at ₹ {pps:,.0f} / sq.ft. for a {req.bhk}-BHK in {req.location}."
    )


# ==============================================================================
# SPA STATIC ASSET SERVING (Production Frontend)
# ==============================================================================
DIST_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/")
def serve_root():
    index_html = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {
        "status": "online",
        "service": "Smart Estate AI Backend API",
        "message": "Frontend build not detected. Please run 'npm run build' inside frontend directory."
    }


@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    file_path = os.path.join(DIST_DIR, full_path)
    if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_html = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {
        "status": "online",
        "service": "Smart Estate AI Backend API",
        "message": "Frontend build not detected. Please run 'npm run build' inside frontend directory."
    }
