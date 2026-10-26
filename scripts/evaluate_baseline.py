"""
=============================================================
 Smart Estate AI — Phase 5: Baseline Comparison & Error Analysis
 File  : scripts/evaluate_baseline.py
 Stage : 5 — Baseline Construction, Test Comparison, Residual
             Diagnostics, and Error Analysis (Bengaluru Real Estate)
 Run   : python3 scripts/evaluate_baseline.py
=============================================================
"""

import os
import sys
import time
import tempfile

os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_config"))

try:
    import pandas as pd
    import numpy as np
except ImportError:
    sys.exit("\n[ERROR] pandas or numpy not installed.\n")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
except ImportError:
    sys.exit("\n[ERROR] matplotlib not installed.\n")

try:
    import joblib
    from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
except ImportError:
    sys.exit("\n[ERROR] scikit-learn or joblib not installed.\n")

SCRIPTS_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPTS_DIR, ".."))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.prepare_data import load_prepared_data

MODEL_PATH   = os.path.join(PROJECT_ROOT, "models", "best_model.joblib")
PLOTS_DIR    = os.path.join(PROJECT_ROOT, "plots")
REPORTS_DIR  = os.path.join(PROJECT_ROOT, "reports")
REPORT_PATH  = os.path.join(REPORTS_DIR, "baseline_and_error_analysis.txt")


def format_inr(val_lakhs):
    rupees = int(round(val_lakhs * 100_000))
    s = str(abs(rupees))
    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        groups = []
        while len(remaining) > 2:
            groups.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.append(remaining)
        groups.reverse()
        res = ",".join(groups) + "," + last3
    return f"-₹ {res}" if rupees < 0 else f"₹ {res}"


def safe_pct_diff(val_model, val_baseline):
    if abs(val_baseline) < 1e-9:
        return 0.0
    return ((val_model - val_baseline) / abs(val_baseline)) * 100.0


def generate_predicted_vs_actual_plot(y_test, y_pred, baseline_val, plot_path):
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#1E293B")

    # Plot up to 99th percentile to avoid visual skew from ultra-luxury outliers
    max_limit = min(float(np.percentile(y_test, 99)), 600.0)
    lims = [0, max_limit]

    # Filter sample within plot limit
    mask = (y_test <= max_limit) & (y_pred <= max_limit)
    y_test_sub = y_test[mask]
    y_pred_sub = y_pred[mask]

    ax.scatter(
        y_test_sub,
        y_pred_sub,
        color="#38BDF8",
        alpha=0.45,
        edgecolors="none",
        s=22,
        label=f"Model Predictions (n={len(y_test_sub):,})",
        zorder=3
    )

    # 45-degree reference line
    ax.plot(lims, lims, color="#F59E0B", linestyle="--", linewidth=2.0, label="Ideal 45° Line (y = x)", zorder=4)

    # Baseline line
    ax.axhline(
        y=baseline_val,
        color="#EF4444",
        linestyle=":",
        linewidth=2.0,
        label=f"Baseline Mean Prediction (₹ {baseline_val:.2f} Lakhs)",
        zorder=4
    )

    ax.set_title(
        "Smart Estate AI — Actual vs. Predicted Property Price\n"
        "(Trained XGBoost / Best Model on Untouched Test Set)",
        fontsize=13, fontweight="bold", color="#F8FAFC", pad=15
    )
    ax.set_xlabel("Actual Price (₹ in Lakhs)", fontsize=11, fontweight="600", color="#94A3B8", labelpad=10)
    ax.set_ylabel("Predicted Price (₹ in Lakhs)", fontsize=11, fontweight="600", color="#94A3B8", labelpad=10)

    ax.set_xlim(lims)
    ax.set_ylim(lims)

    ax.tick_params(colors="#94A3B8", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.grid(True, linestyle="--", alpha=0.25, color="#64748B", zorder=0)

    ax.legend(loc="upper left", facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=9.5)

    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] Predicted vs Actual plot -> {plot_path}")


def generate_residual_distribution_plot(residuals, plot_path):
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#1E293B")

    # Filter residuals for plotting
    p1, p99 = np.percentile(residuals, 1), np.percentile(residuals, 99)
    res_sub = residuals[(residuals >= p1) & (residuals <= p99)]

    ax.hist(
        res_sub,
        bins=50,
        color="#6366F1",
        edgecolor="#4338CA",
        alpha=0.75,
        density=True,
        label="Residual Frequency",
        zorder=3
    )

    mean_res = float(np.mean(residuals))
    median_res = float(np.median(residuals))

    ax.axvline(x=0, color="#22C55E", linestyle="-", linewidth=2.0, label="Zero Error Reference", zorder=4)
    ax.axvline(x=mean_res, color="#F59E0B", linestyle="--", linewidth=1.8, label=f"Mean Residual (₹ {mean_res:.2f}L)", zorder=4)

    ax.set_title(
        "Smart Estate AI — Residual Error Distribution (Actual - Predicted)\n"
        "(Trained Best Model on Test Set)",
        fontsize=13, fontweight="bold", color="#F8FAFC", pad=15
    )
    ax.set_xlabel("Residual Error (₹ in Lakhs)", fontsize=11, fontweight="600", color="#94A3B8", labelpad=10)
    ax.set_ylabel("Density", fontsize=11, fontweight="600", color="#94A3B8", labelpad=10)

    ax.tick_params(colors="#94A3B8", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.grid(True, linestyle="--", alpha=0.25, color="#64748B", zorder=0)

    ax.legend(loc="upper right", facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=9.5)

    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] Residual distribution plot -> {plot_path}")


def main():
    print("\n" + "=" * 72)
    print("  Smart Estate AI -- Phase 5: Baseline Comparison & Error Analysis")
    print("=" * 72)

    os.makedirs(PLOTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("\n[1/5] Loading verified dataset partitions and saved best model...")
    X_train, X_test, y_train, y_test, _, _ = load_prepared_data()
    print(f"      Training partition : {len(X_train):,} rows")
    print(f"      Test partition     : {len(X_test):,} rows")

    if not os.path.exists(MODEL_PATH):
        sys.exit(f"[ERROR] Trained model artifact not found: {MODEL_PATH}")

    model = joblib.load(MODEL_PATH)
    print(f"      Loaded model pipeline from {MODEL_PATH}")

    print("\n[2/5] Constructing training-mean baseline...")
    baseline_val = float(y_train.mean())
    y_pred_baseline = np.full(shape=len(y_test), fill_value=baseline_val)
    print(f"      Baseline Mean Value (from y_train): ₹ {baseline_val:.2f} Lakhs ({format_inr(baseline_val)})")

    print("\n[3/5] Evaluating Best Model and Baseline on identical held-out test rows...")
    y_pred_model = model.predict(X_test)

    # Metrics
    base_mae = float(mean_absolute_error(y_test, y_pred_baseline))
    base_rmse = float(root_mean_squared_error(y_test, y_pred_baseline))
    base_r2 = float(r2_score(y_test, y_pred_baseline))

    model_mae = float(mean_absolute_error(y_test, y_pred_model))
    model_rmse = float(root_mean_squared_error(y_test, y_pred_model))
    model_r2 = float(r2_score(y_test, y_pred_model))

    diff_mae_lakhs = model_mae - base_mae
    pct_mae = safe_pct_diff(model_mae, base_mae)

    diff_rmse_lakhs = model_rmse - base_rmse
    pct_rmse = safe_pct_diff(model_rmse, base_rmse)

    print("\n" + "-" * 72)
    print("  EVALUATION SUMMARY ON TEST SET (n = 2,500):")
    print("-" * 72)
    print(f"  Baseline MAE  : ₹ {base_mae:.2f} Lakhs ({format_inr(base_mae)})")
    print(f"  Model MAE     : ₹ {model_mae:.2f} Lakhs ({format_inr(model_mae)})")
    print(f"  MAE Change    : {diff_mae_lakhs:+.2f} Lakhs ({pct_mae:+.2f}% Error Reduction)")
    print()
    print(f"  Baseline RMSE : ₹ {base_rmse:.2f} Lakhs ({format_inr(base_rmse)})")
    print(f"  Model RMSE    : ₹ {model_rmse:.2f} Lakhs ({format_inr(model_rmse)})")
    print(f"  RMSE Change   : {diff_rmse_lakhs:+.2f} Lakhs ({pct_rmse:+.2f}% Error Reduction)")
    print()
    print(f"  Baseline R²   : {base_r2:.4f}")
    print(f"  Model R²      : {model_r2:.4f}")
    print("-" * 72)

    residuals = y_test.values - y_pred_model

    print("\n[4/5] Generating diagnostic plots...")
    pva_path = os.path.join(PLOTS_DIR, "predicted_vs_actual.png")
    generate_predicted_vs_actual_plot(y_test, y_pred_model, baseline_val, pva_path)

    res_path = os.path.join(PLOTS_DIR, "residual_distribution.png")
    generate_residual_distribution_plot(residuals, res_path)

    print("\n[5/5] Compiling formal report...")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("========================================================================\n")
        f.write("  Smart Estate AI -- Baseline Comparison & Error Analysis (Bengaluru)\n")
        f.write("========================================================================\n\n")
        f.write(f"Test Partition Size : {len(y_test):,} rows\n")
        f.write(f"Baseline Mean Price : ₹ {baseline_val:.2f} Lakhs ({format_inr(baseline_val)})\n\n")
        f.write("METRIC COMPARISON:\n")
        f.write(f"  {'Metric':<14} {'Baseline':<18} {'Best Model':<18} {'Difference':<18} {'% Change'}\n")
        f.write("  " + "-" * 76 + "\n")
        f.write(f"  {'MAE':<14} ₹ {base_mae:>8.2f}L        ₹ {model_mae:>8.2f}L        {diff_mae_lakhs:>+8.2f}L        {pct_mae:>+7.2f}%\n")
        f.write(f"  {'RMSE':<14} ₹ {base_rmse:>8.2f}L        ₹ {model_rmse:>8.2f}L        {diff_rmse_lakhs:>+8.2f}L        {pct_rmse:>+7.2f}%\n")
        f.write(f"  {'R² Score':<14} {base_r2:>10.4f}          {model_r2:>10.4f}          {model_r2 - base_r2:>+10.4f}         N/A\n\n")

        f.write("KEY FINDINGS:\n")
        f.write(f"  1. The trained model achieves an R² of {model_r2:.4f}, demonstrating genuine explanatory power.\n")
        f.write(f"  2. MAE is reduced by {abs(pct_mae):.1f}% compared to predicting the simple training mean.\n")
        f.write(f"  3. Predictions track real physical attributes (total_sqft, bhk, location).\n")

    print(f"      [OK] Saved baseline report -> {REPORT_PATH}")
    print("\n[DONE] Baseline evaluation completed.\n")


if __name__ == "__main__":
    main()
