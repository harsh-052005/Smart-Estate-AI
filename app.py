"""
================================================================================
  SMART ESTATE AI — Premium Real Estate Machine Learning Analytics Dashboard
  Author : Smart Estate AI Engineering Team
  Stack  : Streamlit | Plotly | scikit-learn | pandas | NumPy
================================================================================
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import joblib

# ==============================================================================
# 1. PAGE SETUP & CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Smart Estate AI — PropTech ML Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CLEAN_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "bengaluru_cleaned.csv")
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "bengaluru_house_prices.csv")
DATA_PATH = CLEAN_DATA_PATH if os.path.exists(CLEAN_DATA_PATH) else RAW_DATA_PATH
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "best_model.joblib")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "plots")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


# ==============================================================================
# 2. DESIGN SYSTEM & CUSTOM CSS
# ==============================================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #E2E8F0;
}

.stApp {
    background: radial-gradient(circle at 15% 15%, #0F172A 0%, #0B1120 40%, #030712 100%);
    background-attachment: fixed;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(11, 17, 32, 0.98) 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
}

.premium-card {
    background: rgba(30, 41, 59, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(12px);
    transition: all 0.25s ease-in-out;
    margin-bottom: 1.25rem;
}

.premium-card:hover {
    border-color: rgba(56, 189, 248, 0.35);
    box-shadow: 0 15px 30px -5px rgba(56, 189, 248, 0.15);
}

.hero-header {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2.25rem;
    margin-bottom: 2rem;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
}

.hero-tag {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.12);
    padding: 0.3rem 0.75rem;
    border-radius: 9999px;
    display: inline-block;
    border: 1px solid rgba(56, 189, 248, 0.3);
    margin-bottom: 0.75rem;
}

.hero-title {
    font-size: 2.25rem;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.03em;
    line-height: 1.2;
    margin: 0 0 0.5rem 0;
}

.hero-subtitle {
    font-size: 1rem;
    color: #94A3B8;
    max-width: 800px;
    line-height: 1.6;
    margin: 0;
}

.kpi-container {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.15rem 1.25rem;
    height: 100%;
}

.kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #F8FAFC;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
    line-height: 1.15;
}

.kpi-sub {
    font-size: 0.75rem;
    color: #38BDF8;
    margin-top: 0.35rem;
    font-weight: 500;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 3. DATA & MODEL LOADERS
# ==============================================================================

@st.cache_data(show_spinner=False)
def load_housing_dataset(filepath=DATA_PATH):
    if not os.path.exists(filepath):
        return None
    try:
        return pd.read_csv(filepath)
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def load_trained_model(model_path=MODEL_PATH):
    if not os.path.exists(model_path):
        return None
    try:
        return joblib.load(model_path)
    except Exception:
        return None


def format_inr(lakhs):
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
    formatted_inr = f"-₹ {res}" if rupees < 0 else f"₹ {res}"
    return f"₹ {lakhs:,.2f} Lakhs", formatted_inr


def apply_dark_theme(fig, height=450):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1", size=11),
        margin=dict(l=40, r=30, t=50, b=40),
        height=height,
    )
    fig.update_xaxes(gridcolor="#1E293B", linecolor="#334155")
    fig.update_yaxes(gridcolor="#1E293B", linecolor="#334155")
    return fig


# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================

with st.sidebar:
    st.markdown("""
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: linear-gradient(135deg, #0284C7 0%, #2DD4BF 100%); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                    🏢
                </div>
                <div>
                    <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">Smart Estate AI</h2>
                    <span style="font-size: 0.72rem; color: #38BDF8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">Bengaluru PropTech ML</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    nav_selection = st.radio(
        "Navigation",
        [
            "1. Overview & Research Summary",
            "2. Property Explorer",
            "3. Model Performance Lab",
            "4. Explainability & Error Studio",
            "5. Interactive Prediction Demo",
            "6. Project & Methodology",
        ],
        label_visibility="collapsed"
    )

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size: 0.75rem; color: #64748B; line-height: 1.5;">
            <b style="color: #94A3B8;">Dataset:</b> Bengaluru Residential Housing<br>
            <b style="color: #94A3B8;">Records:</b> 12,496 Cleaned Listings<br>
            <b style="color: #94A3B8;">Model:</b> Tuned XGBoost Pipeline<br>
            <b style="color: #94A3B8;">Test R² Score:</b> 0.7628
        </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 5. TAB IMPLEMENTATION
# ==============================================================================

df_raw = load_housing_dataset()

# ------------------------------------------------------------------------------
# TAB 1: OVERVIEW & RESEARCH SUMMARY
# ------------------------------------------------------------------------------
if nav_selection == "1. Overview & Research Summary":
    st.markdown("""
        <div class="hero-header">
            <span class="hero-tag">PropTech Research System</span>
            <h1 class="hero-title">Bengaluru Real Estate AI Valuation Platform</h1>
            <p class="hero-subtitle">
                An end-to-end machine learning system trained on authentic Bengaluru residential listings. Powered by leak-free preprocessing, multi-model benchmarking, and feature explainability diagnostics.
            </p>
        </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-label">Dataset Size</div>
                <div class="kpi-value">12,496</div>
                <div class="kpi-sub">Verified Listings</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-label">Winning Model</div>
                <div class="kpi-value" style="font-size: 1.45rem; color: #38BDF8;">XGBoost</div>
                <div class="kpi-sub">150 Trees | Depth 6</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-label">Test R² Score</div>
                <div class="kpi-value" style="color: #2DD4BF;">0.7628</div>
                <div class="kpi-sub">Explains 76.3% of Variance</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown("""
            <div class="kpi-container">
                <div class="kpi-label">Test MAE (Error)</div>
                <div class="kpi-value" style="color: #F8FAFC;">₹ 28.64L</div>
                <div class="kpi-sub">-60.4% vs Baseline</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([7, 5])
    with c1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; color:#F8FAFC;'>🏆 Research Milestones & Findings</h3>", unsafe_allow_html=True)
        st.markdown("""
        - **Synthetic Noise Excluded:** The previous synthetic uniform dataset was retired after empirical tests showed $|r| \le 0.004$ and severe physical contradictions.
        - **Real Market Dynamics:** Ingested 13,320 genuine Bengaluru property records across 240+ localities (Whitefield, Indiranagar, Electronic City, etc.).
        - **Massive Predictive Gain:** Models achieved an **$R^2$ of 0.7628** on held-out test data, slashing baseline prediction errors from ₹ 72.30L to ₹ 28.64L.
        - **True Valuation Drivers:** Total square footage and micro-market locality account for over 88% of real estate value.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; color:#F8FAFC;'>📈 Benchmark Overview</h3>", unsafe_allow_html=True)
        benchmark_data = pd.DataFrame([
            {"Model": "Baseline (Mean)", "MAE (Lakhs)": 72.30, "R² Score": 0.000},
            {"Model": "Linear (Ridge)", "MAE (Lakhs)": 37.36, "R² Score": 0.642},
            {"Model": "Random Forest", "MAE (Lakhs)": 32.61, "R² Score": 0.686},
            {"Model": "XGBoost (Winner)", "MAE (Lakhs)": 28.64, "R² Score": 0.763},
        ])
        fig_bar = px.bar(
            benchmark_data,
            x="Model",
            y="MAE (Lakhs)",
            color="Model",
            color_discrete_sequence=["#EF4444", "#38BDF8", "#818CF8", "#2DD4BF"],
            title="Model Test MAE Comparison (Lower is Better)"
        )
        apply_dark_theme(fig_bar, height=280)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 2: PROPERTY EXPLORER
# ------------------------------------------------------------------------------
elif nav_selection == "2. Property Explorer":
    st.markdown("""
        <div class="hero-header">
            <span class="hero-tag">Exploratory Data Analytics</span>
            <h1 class="hero-title">Bengaluru Property Explorer</h1>
            <p class="hero-subtitle">
                Filter and inspect 12,496 residential properties across Bengaluru's high-demand tech corridors and residential neighborhoods.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if df_raw is not None:
        locations_list = sorted(list(df_raw["location"].dropna().unique()))
        area_types_list = sorted(list(df_raw["area_type"].dropna().unique()))

        with st.expander("🔍 Filter Properties", expanded=True):
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                sel_loc = st.selectbox("Locality", ["All"] + locations_list)
            with f2:
                sel_area = st.selectbox("Area Type", ["All"] + area_types_list)
            with f3:
                sel_bhk = st.multiselect("BHK Configuration", [1, 2, 3, 4, 5, 6], default=[1, 2, 3, 4, 5])
            with f4:
                min_p, max_p = float(df_raw["price"].min()), float(min(df_raw["price"].max(), 800.0))
                sel_price = st.slider("Price (₹ Lakhs)", min_p, max_p, (min_p, max_p))

        # Filter
        f_df = df_raw.copy()
        if sel_loc != "All":
            f_df = f_df[f_df["location"] == sel_loc]
        if sel_area != "All":
            f_df = f_df[f_df["area_type"] == sel_area]
        if sel_bhk:
            f_df = f_df[f_df["bhk"].isin(sel_bhk)]
        f_df = f_df[(f_df["price"] >= sel_price[0]) & (f_df["price"] <= sel_price[1])]

        st.markdown(f"**Found {len(f_df):,} matching properties**")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#F8FAFC;'>Price vs. Total Sq.Ft.</h4>", unsafe_allow_html=True)
            sample_sub = f_df.sample(min(2000, len(f_df)), random_state=42)
            fig_scatter = px.scatter(
                sample_sub,
                x="total_sqft",
                y="price",
                color="area_type",
                opacity=0.5,
                labels={"total_sqft": "Size (Sq.Ft.)", "price": "Price (₹ Lakhs)"}
            )
            apply_dark_theme(fig_scatter, height=350)
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#F8FAFC;'>Price Distribution</h4>", unsafe_allow_html=True)
            fig_hist = px.histogram(
                f_df,
                x="price",
                nbins=40,
                color_discrete_sequence=["#38BDF8"],
                labels={"price": "Price (₹ Lakhs)"}
            )
            apply_dark_theme(fig_hist, height=350)
            st.plotly_chart(fig_hist, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.dataframe(f_df[["location", "area_type", "bhk", "bath", "total_sqft", "price", "price_per_sqft"]].head(100), use_container_width=True)


# ------------------------------------------------------------------------------
# TAB 3: MODEL PERFORMANCE LAB
# ------------------------------------------------------------------------------
elif nav_selection == "3. Model Performance Lab":
    st.markdown("""
        <div class="hero-header">
            <span class="hero-tag">Model Benchmarks</span>
            <h1 class="hero-title">Model Performance & Evaluation Lab</h1>
            <p class="hero-subtitle">
                Systematic evaluation across Linear (Ridge), Random Forest, and XGBoost on held-out test data.
            </p>
        </div>
    """, unsafe_allow_html=True)

    comp_csv = os.path.join(REPORTS_DIR, "model_comparison.csv")
    if os.path.exists(comp_csv):
        cdf = pd.read_csv(comp_csv)
        st.dataframe(cdf, use_container_width=True)

    comp_plot = os.path.join(PLOTS_DIR, "model_comparison.png")
    if os.path.exists(comp_plot):
        st.image(comp_plot, caption="Model Performance Comparison", use_column_width=True)


# ------------------------------------------------------------------------------
# TAB 4: EXPLAINABILITY & ERROR STUDIO
# ------------------------------------------------------------------------------
elif nav_selection == "4. Explainability & Error Studio":
    st.markdown("""
        <div class="hero-header">
            <span class="hero-tag">Explainable AI</span>
            <h1 class="hero-title">Model Interpretation & Error Studio</h1>
            <p class="hero-subtitle">
                Inspect feature importances, permutation sensitivity, and error distributions on test predictions.
            </p>
        </div>
    """, unsafe_allow_html=True)

    pva_path = os.path.join(PLOTS_DIR, "predicted_vs_actual.png")
    if os.path.exists(pva_path):
        st.image(pva_path, caption="Actual vs. Predicted Price", use_column_width=True)

    feat_path = os.path.join(PLOTS_DIR, "feature_importance.png")
    if os.path.exists(feat_path):
        st.image(feat_path, caption="Feature Importance Analysis", use_column_width=True)


# ------------------------------------------------------------------------------
# TAB 5: INTERACTIVE PREDICTION DEMO
# ------------------------------------------------------------------------------
elif nav_selection == "5. Interactive Prediction Demo":
    st.markdown("""
        <div class="hero-header">
            <span class="hero-tag">Live Model Inference</span>
            <h1 class="hero-title">Interactive Bengaluru Valuation Demo</h1>
            <p class="hero-subtitle">
                Input property specifications to generate instant AI price predictions using the trained XGBoost model pipeline.
            </p>
        </div>
    """, unsafe_allow_html=True)

    model_pipeline = load_trained_model()
    if model_pipeline is None:
        st.error("Model pipeline artifact (models/best_model.joblib) could not be loaded.")
        st.stop()

    locations_list = sorted(list(df_raw["location"].dropna().unique())) if df_raw is not None else ["Whitefield"]
    area_types_list = sorted(list(df_raw["area_type"].dropna().unique())) if df_raw is not None else ["Super built-up  Area"]

    with st.form("bengaluru_predict_form"):
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            in_loc = st.selectbox("Locality", locations_list, index=locations_list.index("Whitefield") if "Whitefield" in locations_list else 0)
        with r1_c2:
            in_area = st.selectbox("Area Type", area_types_list)

        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        with r2_c1:
            in_sqft = st.number_input("Total Size (Sq. Ft.)", min_value=300, max_value=8000, value=1350, step=50)
        with r2_c2:
            in_bhk = st.selectbox("BHK", [1, 2, 3, 4, 5, 6], index=1)
        with r2_c3:
            in_bath = st.selectbox("Bathrooms", [1, 2, 3, 4, 5], index=1)
        with r2_c4:
            in_balcony = st.selectbox("Balconies", [0, 1, 2, 3], index=1)

        in_avail = st.selectbox("Possession Readiness", ["Ready To Move", "Under Construction"])

        submit_btn = st.form_submit_button("⚡ Estimate Property Price", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if submit_btn:
        input_df = pd.DataFrame([{
            "total_sqft": float(in_sqft),
            "bhk": int(in_bhk),
            "bath": int(in_bath),
            "balcony": int(in_balcony),
            "location": in_loc,
            "area_type": in_area,
            "availability": in_avail
        }])

        pred_price = float(model_pipeline.predict(input_df)[0])
        pred_price = max(10.0, pred_price)
        pred_lakhs_str, full_inr_str = format_inr(pred_price)
        pps = (pred_price * 100000) / in_sqft

        st.markdown(f"""
            <div class="premium-card" style="border: 1px solid rgba(56, 189, 248, 0.4); background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);">
                <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #38BDF8; letter-spacing: 0.08em; margin-bottom: 0.4rem;">
                    Estimated Market Valuation
                </div>
                <div style="font-size: 2.8rem; font-weight: 800; color: #F8FAFC;">
                    {pred_lakhs_str}
                </div>
                <div style="font-size: 1.25rem; font-weight: 600; color: #2DD4BF;">
                    ({full_inr_str})
                </div>
                <div style="font-size: 0.9rem; color: #94A3B8; margin-top: 0.8rem;">
                    Valuation rate: <b>₹ {pps:,.0f} / sq.ft.</b> for a {in_bhk}-BHK in {in_loc}.<br>
                    Model: Tuned XGBoost Pipeline (R² = 0.7628 on held-out test data).
                </div>
            </div>
        """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 6: PROJECT & METHODOLOGY
# ------------------------------------------------------------------------------
elif nav_selection == "6. Project & Methodology":
    st.markdown("""
        <div class="hero-header">
            <span class="hero-tag">Documentation</span>
            <h1 class="hero-title">Methodology & System Architecture</h1>
            <p class="hero-subtitle">
                Transparent engineering standards, preprocessing pipelines, and model governance documentation.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### Data Pipeline Design
    1. **Data Ingestion & Cleaning:** Ingested canonical Bengaluru property records. Converted irregular total_sqft entries (ranges, unit strings like Sq. Yards and Acres). Extracted integer BHK from unstructured descriptions.
    2. **Domain Anomaly Removal:** Enforced minimum realistic floor space per bedroom (total_sqft / BHK >= 300 sq.ft.) and bathroom counts (bath <= BHK + 2). Filtered extreme price per sq.ft. outliers (< 1,500 or > 35,000 INR/sqft).
    3. **Leak-Free Transformation:** OneHotEncoder and ColumnTransformers fit strictly on training partitions to prevent test data leakage.
    4. **Model Selection:** Evaluated Ridge Regression, Random Forest, and XGBoost using validation MAE and $R^2$. Retrained the selected XGBoost pipeline on the full training set and verified once on untouched held-out test data ($R^2 = 0.7628$).
    """)
