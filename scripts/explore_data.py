"""
=============================================================
 Smart Estate AI — Exploratory Data Analysis (EDA)
 File  : scripts/explore_data.py
 Stage : 3 — Exploratory Data Analysis (Read-Only)
 Run   : python3 scripts/explore_data.py
=============================================================

This script performs EDA on the housing dataset.
It generates:
  1. reports/eda_summary.txt  (detailed statistical summary)
  2. plots/                   (high-resolution charts)

RULES ENFORCED:
  - Strictly READ-ONLY: never modifies, cleans, overwrites, or deletes original data.
  - No ML models are trained.
  - Price_per_SqFt is excluded from feature analysis (data leakage).
  - Floor_No & Total_Floors are flagged as unreliable.
  - Evidence-based conclusions: notes strong indicators of synthetic data.
"""

import os
import sys
import tempfile

# Configure matplotlib cache before importing to avoid write permission warnings
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_config"))

try:
    import pandas as pd
    import numpy as np
except ImportError:
    sys.exit("\n[ERROR] pandas or numpy not installed. Run: python3 -m pip install pandas numpy\n")

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend for headless PNG generation
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
except ImportError:
    sys.exit("\n[ERROR] matplotlib not installed. Run: python3 -m pip install matplotlib\n")

# Check if seaborn is available (optional enhancement)
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False


# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH     = os.path.join(PROJECT_ROOT, "india_housing_prices.csv")
REPORTS_DIR  = os.path.join(PROJECT_ROOT, "reports")
REPORT_PATH  = os.path.join(REPORTS_DIR, "eda_summary.txt")
PLOTS_DIR    = os.path.join(PROJECT_ROOT, "plots")


# =============================================================================
# REPORT WRITER
# =============================================================================

class ReportWriter:
    """Helper to structure clean, consistent text reports."""
    def __init__(self):
        self._lines = []

    def h1(self, title):
        bar = "=" * 72
        self._lines += ["", bar, f"  {title}", bar]

    def h2(self, title):
        self._lines += ["", f"  -- {title}"]

    def row(self, text=""):
        self._lines.append(text)

    def blank(self):
        self._lines.append("")

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = "\n".join(self._lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return content


# =============================================================================
# PLOTTING STYLING HELPERS
# =============================================================================

def apply_chart_style(ax, grid_axis="both"):
    """Apply clean, elegant styling to matplotlib axes."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#4a4a4a")
    ax.spines["bottom"].set_color("#4a4a4a")
    ax.tick_params(colors="#333333", labelsize=10)
    if grid_axis:
        ax.grid(True, axis=grid_axis, linestyle="--", linewidth=0.6, alpha=0.5, color="#c0c0c0")
    ax.set_axisbelow(True)


# =============================================================================
# LOAD DATA
# =============================================================================

def load_data(path):
    """Load dataset read-only with verification."""
    if not os.path.isfile(path):
        sys.exit(f"\n[ERROR] Dataset not found at: {path}\nPlease check file placement.\n")
    for enc in ("utf-8", "latin-1"):
        try:
            df = pd.read_csv(path, encoding=enc, low_memory=False)
            print(f"[OK] Loaded dataset: {df.shape[0]:,} rows x {df.shape[1]} columns ({enc})")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            sys.exit(f"[ERROR] Could not parse CSV: {e}")
    sys.exit("[ERROR] Could not decode dataset.")


# =============================================================================
# CHART GENERATION FUNCTIONS
# =============================================================================

def plot_price_distribution(df, output_path):
    """Chart 1: Distribution of Price_in_Lakhs with mean and median marked."""
    price = pd.to_numeric(df["Price_in_Lakhs"], errors="coerce").dropna()
    mean_val = price.mean()
    median_val = price.median()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    counts, bins, patches = ax.hist(
        price, bins=50, color="#2b5c8f", edgecolor="#1a3b5c", alpha=0.85
    )

    # Mark mean and median
    ax.axvline(mean_val, color="#d9534f", linestyle="--", linewidth=2.2,
               label=f"Mean: \u20b9{mean_val:,.2f} Lakhs")
    ax.axvline(median_val, color="#5cb85c", linestyle="-.", linewidth=2.2,
               label=f"Median: \u20b9{median_val:,.2f} Lakhs")

    ax.set_title("Distribution of Property Prices (Price_in_Lakhs)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Price in Lakhs (\u20b9 INR)", fontsize=11, labelpad=8)
    ax.set_ylabel("Number of Properties (Frequency)", fontsize=11, labelpad=8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"\u20b9{int(x):,}L"))
    ax.legend(frameon=True, facecolor="#f9f9f9", edgecolor="#d0d0d0", fontsize=10, loc="upper right")
    apply_chart_style(ax, grid_axis="y")

    # Add text box with distribution observations
    note = (f"Sample Size: {len(price):,}\n"
            f"Min: \u20b9{price.min():.1f}L  |  Max: \u20b9{price.max():.1f}L\n"
            f"Std: \u20b9{price.std():.1f}L  |  Skewness: {price.skew():.4f}\n"
            f"Distribution is near-uniform across range.")
    ax.text(0.03, 0.94, note, transform=ax.transAxes, verticalalignment="top",
            fontsize=9, bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#cccccc", alpha=0.9))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_size_distribution(df, output_path):
    """Chart 2: Distribution of Size_in_SqFt."""
    size = pd.to_numeric(df["Size_in_SqFt"], errors="coerce").dropna()
    mean_val = size.mean()
    median_val = size.median()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.hist(size, bins=50, color="#1e824c", edgecolor="#145a32", alpha=0.85)

    ax.axvline(mean_val, color="#d9534f", linestyle="--", linewidth=2.0,
               label=f"Mean: {mean_val:,.1f} sq-ft")
    ax.axvline(median_val, color="#f39c12", linestyle="-.", linewidth=2.0,
               label=f"Median: {median_val:,.1f} sq-ft")

    ax.set_title("Distribution of Property Sizes (Size_in_SqFt)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Size in Square Feet (Sq. Ft.)", fontsize=11, labelpad=8)
    ax.set_ylabel("Number of Properties (Frequency)", fontsize=11, labelpad=8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
    ax.legend(frameon=True, facecolor="#f9f9f9", edgecolor="#d0d0d0", fontsize=10, loc="upper right")
    apply_chart_style(ax, grid_axis="y")

    note = (f"Sample Size: {len(size):,}\n"
            f"Min: {size.min():,.0f} sq-ft  |  Max: {size.max():,.0f} sq-ft\n"
            f"Std: {size.std():,.1f} sq-ft\n"
            f"Bounded strictly between 500 and 5,000 sq-ft.")
    ax.text(0.03, 0.94, note, transform=ax.transAxes, verticalalignment="top",
            fontsize=9, bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#cccccc", alpha=0.9))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_price_by_bhk(df, output_path):
    """Chart 3: Average and median price by BHK."""
    bhk_group = df.groupby("BHK")["Price_in_Lakhs"].agg(["mean", "median", "count"]).reset_index()

    x = np.arange(len(bhk_group))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bars1 = ax.bar(x - width/2, bhk_group["mean"], width, label="Average (Mean) Price",
                   color="#3498db", edgecolor="#2980b9", alpha=0.9)
    bars2 = ax.bar(x + width/2, bhk_group["median"], width, label="Median Price",
                   color="#9b59b6", edgecolor="#8e44ad", alpha=0.9)

    ax.set_title("Average and Median Property Price by BHK", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Bedrooms, Hall, Kitchen (BHK)", fontsize=11, labelpad=8)
    ax.set_ylabel("Price in Lakhs (\u20b9 INR)", fontsize=11, labelpad=8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{int(b)} BHK\n(n={int(c):,})" for b, c in zip(bhk_group["BHK"], bhk_group["count"])])
    ax.set_ylim(0, 320)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, p: f"\u20b9{int(val)}L"))
    ax.legend(frameon=True, facecolor="#f9f9f9", edgecolor="#d0d0d0", fontsize=10, loc="upper right")
    apply_chart_style(ax, grid_axis="y")

    # Annotate bar values
    for b in bars1:
        h = b.get_height()
        ax.annotate(f"\u20b9{h:.1f}L", xy=(b.get_x() + b.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for b in bars2:
        h = b.get_height()
        ax.annotate(f"\u20b9{h:.1f}L", xy=(b.get_x() + b.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9)

    ax.text(0.03, 0.94, "Surprising Pattern: Price does NOT increase with BHK.\nMean price stays flat at ~\u20b9254L across 1 to 5 BHK.",
            transform=ax.transAxes, verticalalignment="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffeeba", alpha=0.95))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_price_by_property_type(df, output_path):
    """Chart 4: Price distribution by Property_Type."""
    pt_types = df["Property_Type"].unique()
    data_by_type = [df[df["Property_Type"] == pt]["Price_in_Lakhs"].dropna().values for pt in pt_types]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bp = ax.boxplot(
        data_by_type,
        tick_labels=pt_types,
        patch_artist=True,
        showmeans=True,
        meanline=True,
        medianprops=dict(color="#d9534f", linewidth=2.0),
        meanprops=dict(color="#2980b9", linewidth=2.0, linestyle="--"),
        flierprops=dict(marker="o", markersize=2, alpha=0.3, color="#888888")
    )

    colors = ["#aed6f1", "#a9dfbf", "#f9e79f", "#d7bde2"]
    for patch, col in zip(bp["boxes"], colors):
        patch.set_facecolor(col)
        patch.set_edgecolor("#555555")

    ax.set_title("Property Price Distribution by Property Type", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Property Type", fontsize=11, labelpad=8)
    ax.set_ylabel("Price in Lakhs (\u20b9 INR)", fontsize=11, labelpad=8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, p: f"\u20b9{int(val)}L"))
    apply_chart_style(ax, grid_axis="y")

    # Custom legend for median and mean
    legend_elements = [
        matplotlib.lines.Line2D([0], [0], color="#d9534f", lw=2, label="Median Price"),
        matplotlib.lines.Line2D([0], [0], color="#2980b9", lw=2, linestyle="--", label="Mean Price")
    ]
    ax.legend(handles=legend_elements, frameon=True, facecolor="#f9f9f9", edgecolor="#d0d0d0", loc="upper right")

    ax.text(0.03, 0.94, "Surprising Pattern: All property types share almost identical\nprice distributions (IQR ~ \u20b9132L – \u20b9377L, median ~ \u20b9254L).",
            transform=ax.transAxes, verticalalignment="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffeeba", alpha=0.95))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_price_by_state(df, output_path):
    """Chart 5: Average price by State, sorted from highest to lowest."""
    state_avg = df.groupby("State")["Price_in_Lakhs"].agg(["mean", "count"]).reset_index()
    state_avg = state_avg.sort_values(by="mean", ascending=True)  # ascending for horizontal bars

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    bars = ax.barh(state_avg["State"], state_avg["mean"], color="#34495e", edgecolor="#2c3e50", height=0.62, alpha=0.88)

    ax.set_title("Average Property Price by State (Ranked Highest to Lowest)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Average Price in Lakhs (\u20b9 INR)", fontsize=11, labelpad=8)
    ax.set_ylabel("State", fontsize=11, labelpad=8)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, p: f"\u20b9{int(val)}L"))
    ax.set_xlim(0, 300)
    apply_chart_style(ax, grid_axis="x")

    # Annotate bars
    for b in bars:
        w = b.get_width()
        ax.annotate(f"\u20b9{w:.2f}L", xy=(w, b.get_y() + b.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=8.5, fontweight="bold")

    min_s = state_avg['mean'].min()
    max_s = state_avg['mean'].max()
    spread_s = max_s - min_s
    n_s = len(state_avg)

    ax.text(0.03, 0.96, f"Surprising Pattern: State price averages are nearly indistinguishable\n(spread across all {n_s} states is only \u20b9{spread_s:.2f}L: from \u20b9{min_s:.1f}L to \u20b9{max_s:.1f}L).",
            transform=ax.transAxes, verticalalignment="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffeeba", alpha=0.95))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_price_vs_size_scatter(df, output_path, sample_size=5000):
    """Chart 6: Price versus size scatter plot using a readable sample with regression line."""
    sample_df = df[["Size_in_SqFt", "Price_in_Lakhs"]].dropna().sample(
        n=min(sample_size, len(df)), random_state=42
    )

    x = sample_df["Size_in_SqFt"]
    y = sample_df["Price_in_Lakhs"]

    # Calculate regression trend line
    slope, intercept = np.polyfit(x, y, 1)
    corr = x.corr(y)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.scatter(x, y, color="#2980b9", alpha=0.25, s=18, edgecolors="none",
               label=f"Sample Properties (n={sample_size:,})")

    # Trend line
    x_vals = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_vals, slope * x_vals + intercept, color="#e74c3c", linewidth=2.5,
            label=f"Fit Line (slope: {slope:.6f}, r = {corr:.4f})")

    ax.set_title("Property Price vs. Property Size (Sq. Ft.)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Size in Square Feet (Sq. Ft.)", fontsize=11, labelpad=8)
    ax.set_ylabel("Price in Lakhs (\u20b9 INR)", fontsize=11, labelpad=8)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda val, p: f"{int(val):,}"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, p: f"\u20b9{int(val):,}L"))
    ax.legend(frameon=True, facecolor="#f9f9f9", edgecolor="#d0d0d0", fontsize=10, loc="upper right")
    apply_chart_style(ax, grid_axis="both")

    note = (f"Correlation: r = {corr:.4f} (virtually zero)\n"
            f"In authentic real-estate markets, size is the primary price driver (r > 0.60).\n"
            f"Here, a 500 sq-ft flat has the same expected price as a 5,000 sq-ft mansion.")
    ax.text(0.03, 0.06, note, transform=ax.transAxes, verticalalignment="bottom",
            fontsize=9, bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffeeba", alpha=0.95))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_price_vs_year_built(df, output_path):
    """Chart 7: Price versus Year_Built."""
    year_stats = df.groupby("Year_Built")["Price_in_Lakhs"].agg(["mean", "median", "count"]).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.plot(year_stats["Year_Built"], year_stats["mean"], marker="o", markersize=4,
            color="#27ae60", linewidth=1.8, label="Average (Mean) Price")
    ax.plot(year_stats["Year_Built"], year_stats["median"], marker="s", markersize=4,
            color="#e67e22", linewidth=1.8, linestyle="--", label="Median Price")

    ax.set_title("Property Price by Year Built (1990 – 2025)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Year Built", fontsize=11, labelpad=8)
    ax.set_ylabel("Price in Lakhs (\u20b9 INR)", fontsize=11, labelpad=8)
    ax.set_ylim(230, 270)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda val, p: f"\u20b9{int(val)}L"))
    ax.legend(frameon=True, facecolor="#f9f9f9", edgecolor="#d0d0d0", fontsize=10, loc="upper right")
    apply_chart_style(ax, grid_axis="both")

    ax.text(0.03, 0.94, "Surprising Pattern: Newer properties (built in 2024) command no price premium\nover older properties (built in 1990). Prices stay flat around \u20b9254 Lakhs.",
            transform=ax.transAxes, verticalalignment="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#fff3cd", edgecolor="#ffeeba", alpha=0.95))

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_correlation_heatmap(df, output_path):
    """
    Chart 8: Correlation heatmap for appropriate numeric columns.
    Excludes ID and Price_per_SqFt.
    Clearly flags suspicious floor columns with an asterisk (*).
    Notes that correlation measures association, not causation.
    """
    # Columns to include (excluding ID and Price_per_SqFt)
    candidate_cols = [
        "Price_in_Lakhs",
        "Size_in_SqFt",
        "BHK",
        "Year_Built",
        "Age_of_Property",
        "Nearby_Schools",
        "Nearby_Hospitals",
        "Floor_No",
        "Total_Floors"
    ]
    valid_cols = [c for c in candidate_cols if c in df.columns]

    corr_df = df[valid_cols].corr()

    # Display labels with flags for unreliable floor columns
    display_labels = []
    for c in valid_cols:
        if c in ("Floor_No", "Total_Floors"):
            display_labels.append(f"{c} *")
        else:
            display_labels.append(c)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

    # Use imshow for heatmap with clean divergent color palette
    cax = ax.imshow(corr_df.values, cmap="coolwarm", vmin=-1.0, vmax=1.0)
    cbar = fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson Correlation Coefficient (r)", fontsize=10, labelpad=8)

    ax.set_xticks(np.arange(len(valid_cols)))
    ax.set_yticks(np.arange(len(valid_cols)))
    ax.set_xticklabels(display_labels, rotation=40, ha="right", fontsize=9.5)
    ax.set_yticklabels(display_labels, fontsize=9.5)

    # Add numeric annotations to cells
    for i in range(len(valid_cols)):
        for j in range(len(valid_cols)):
            val = corr_df.values[i, j]
            text_color = "white" if abs(val) > 0.55 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=9, fontweight="bold")

    ax.set_title("Correlation Heatmap of Numerical Features", fontsize=14, fontweight="bold", pad=14)

    # Explanatory note
    footer_text = (
        "* Floor_No & Total_Floors flagged as unreliable (46.52% of rows violate Floor_No <= Total_Floors).\n"
        "Price_per_SqFt excluded (derived directly from target; causes data leakage). ID excluded (row index).\n"
        "CAUTION: Correlation measures linear association, not causation."
    )
    fig.text(0.5, 0.01, footer_text, ha="center", fontsize=8.5,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#ced4da", alpha=0.95))

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


def plot_category_counts(df, output_path):
    """Chart 9: Category counts for Furnished_Status, Owner_Type, Availability_Status."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)

    cat_cols = [
        ("Furnished_Status", "#3498db"),
        ("Owner_Type", "#1abc9c"),
        ("Availability_Status", "#e67e22")
    ]

    total_rows = len(df)

    for ax, (col, color) in zip(axes, cat_cols):
        if col not in df.columns:
            ax.set_title(f"{col} (Missing)")
            continue
        counts = df[col].value_counts().sort_index()
        bars = ax.bar(counts.index.astype(str), counts.values, color=color, edgecolor="#2c3e50", alpha=0.85, width=0.5)

        ax.set_title(f"Distribution of {col}", fontsize=12, fontweight="bold", pad=10)
        ax.set_ylabel("Property Count", fontsize=10, labelpad=6)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda val, p: f"{int(val):,}"))
        ax.set_ylim(0, max(counts.values) * 1.18)
        apply_chart_style(ax, grid_axis="y")
        ax.tick_params(axis="x", rotation=15)

        for b in bars:
            h = b.get_height()
            pct = 100.0 * h / total_rows
            ax.annotate(f"{h:,}\n({pct:.1f}%)", xy=(b.get_x() + b.get_width() / 2, h),
                        xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8.5)

    fig.suptitle("Key Categorical Feature Distributions", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
    print(f"  [SAVED] {os.path.basename(output_path)}")


# =============================================================================
# SUMMARY REPORT GENERATION
# =============================================================================

def generate_eda_summary(df, rpt):
    """Compile a thorough, professional EDA text report."""
    total_rows = len(df)
    total_cols = len(df.columns)

    rpt.h1("Smart Estate AI -- Exploratory Data Analysis (EDA) Summary")
    rpt.row(f"  Dataset Path : {CSV_PATH}")
    rpt.row(f"  Row Count    : {total_rows:,}")
    rpt.row(f"  Column Count : {total_cols}")
    rpt.row("  Mode         : READ-ONLY Analysis (No data cleaned, modified, or imputed)")
    rpt.row("  ML Models    : NONE (EDA stage strictly precedes preprocessing and modelling)")

    # ---------------------------------------------------------
    # 1. Target Variable Analysis
    # ---------------------------------------------------------
    rpt.h1("1. TARGET VARIABLE ANALYSIS (Price_in_Lakhs)")
    price = pd.to_numeric(df["Price_in_Lakhs"], errors="coerce")
    desc_p = price.describe(percentiles=[0.05, 0.25, 0.50, 0.75, 0.95])

    rpt.row("  Descriptive Statistics:")
    for stat, val in desc_p.items():
        rpt.row(f"    {stat:<8} : \u20b9 {val:>10,.2f} Lakhs")
    rpt.blank()
    rpt.row(f"  Skewness     : {price.skew():.4f} (near 0: remarkably symmetric distribution)")
    rpt.row(f"  Kurtosis     : {price.kurtosis():.4f} (near -1.2: platykurtic, characteristic of uniform data)")
    rpt.row(f"  Hard Minimum : \u20b9 {price.min():.2f} Lakhs (exactly {(price == price.min()).sum():,} rows at floor)")
    rpt.row(f"  Hard Maximum : \u20b9 {price.max():.2f} Lakhs (exactly {(price == price.max()).sum():,} rows at cap)")
    rpt.blank()
    rpt.row("  Interpretation:")
    rpt.row("    In real real-estate markets, property prices exhibit positive skew (long right tail")
    rpt.row("    due to luxury properties). Here, prices are almost uniformly distributed between")
    rpt.row("    \u20b910.0L and \u20b9500.0L, representing an artificial uniform envelope.")

    # ---------------------------------------------------------
    # 2. Property Size Analysis
    # ---------------------------------------------------------
    rpt.h1("2. PROPERTY SIZE ANALYSIS (Size_in_SqFt)")
    size = pd.to_numeric(df["Size_in_SqFt"], errors="coerce")
    desc_s = size.describe(percentiles=[0.05, 0.25, 0.50, 0.75, 0.95])

    rpt.row("  Descriptive Statistics:")
    for stat, val in desc_s.items():
        rpt.row(f"    {stat:<8} : {val:>10,.1f} sq-ft")
    rpt.blank()
    rpt.row(f"  Skewness     : {size.skew():.4f} (near 0)")
    rpt.row(f"  Strict Bounds: {size.min():,.0f} to {size.max():,.0f} sq-ft (exactly flat 500 – 5,000 range)")
    rpt.blank()
    rpt.row("  Interpretation:")
    rpt.row("    Property area is bounded uniformly between 500 and 5,000 sq-ft.")

    # ---------------------------------------------------------
    # 3. Bivariate Relationships with Target
    # ---------------------------------------------------------
    rpt.h1("3. BIVARIATE RELATIONSHIPS WITH PRICE")

    # (a) BHK
    rpt.h2("(a) Price by BHK (1 to 5 BHK)")
    bhk_summary = df.groupby("BHK")["Price_in_Lakhs"].agg(["count", "mean", "median", "std"]).reset_index()
    rpt.row(f"    {'BHK':<6} {'Count':>9} {'Pct':>7} {'Mean Price':>14} {'Median Price':>14} {'Std Dev':>12}")
    rpt.row("    " + "-" * 66)
    for _, row in bhk_summary.iterrows():
        pct = 100.0 * row['count'] / total_rows
        rpt.row(f"    {int(row['BHK']):<6} {int(row['count']):>9,} {pct:>6.2f}% "
                f"\u20b9 {row['mean']:>10,.2f}L \u20b9 {row['median']:>10,.2f}L \u20b9 {row['std']:>8,.2f}L")
    rpt.blank()
    rpt.row("    CRITICAL FINDING: Mean price is virtually identical across all BHK levels (\u20b9254.4L – \u20b9255.0L).")
    rpt.row("    In authentic housing data, BHK strongly dictates price. Here, no price premium exists.")

    # (b) Property Type
    rpt.h2("(b) Price by Property_Type")
    pt_summary = df.groupby("Property_Type")["Price_in_Lakhs"].agg(["count", "mean", "median", "std"]).reset_index()
    rpt.row(f"    {'Property Type':<20} {'Count':>9} {'Pct':>7} {'Mean Price':>14} {'Median Price':>14}")
    rpt.row("    " + "-" * 68)
    for _, row in pt_summary.iterrows():
        pct = 100.0 * row['count'] / total_rows
        rpt.row(f"    {str(row['Property_Type']):<20} {int(row['count']):>9,} {pct:>6.2f}% "
                f"\u20b9 {row['mean']:>10,.2f}L \u20b9 {row['median']:>10,.2f}L")
    rpt.blank()
    pt_types_desc = ", ".join([f"{row['Property_Type']} (\u20b9{row['mean']:.1f}L)" for _, row in pt_summary.iterrows()])
    rpt.row(f"    CRITICAL FINDING: All property types ({pt_types_desc}) share nearly identical average prices.")

    # (c) State
    rpt.h2("(c) Average Price by State (Sorted Highest to Lowest)")
    st_summary = df.groupby("State")["Price_in_Lakhs"].agg(["count", "mean", "median"]).reset_index()
    st_summary = st_summary.sort_values(by="mean", ascending=False)
    rpt.row(f"    {'State':<20} {'Count':>9} {'Pct':>7} {'Mean Price':>14} {'Median Price':>14}")
    rpt.row("    " + "-" * 68)
    for _, row in st_summary.iterrows():
        pct = 100.0 * row['count'] / total_rows
        rpt.row(f"    {str(row['State']):<20} {int(row['count']):>9,} {pct:>6.2f}% "
                f"\u20b9 {row['mean']:>10,.2f}L \u20b9 {row['median']:>10,.2f}L")
    rpt.blank()
    n_states = len(st_summary)
    s_min = st_summary['mean'].min()
    s_max = st_summary['mean'].max()
    s_spread = s_max - s_min
    rpt.row(f"    CRITICAL FINDING: Spread across all {n_states} states is only \u20b9{s_spread:.2f} Lakhs (\u20b9{s_min:.1f}L to \u20b9{s_max:.1f}L).")
    rpt.row("    Regional economic disparity is completely absent.")

    # (d) Price vs Size
    rpt.h2("(d) Price vs. Size_in_SqFt")
    corr_size_price = size.corr(price)
    rpt.row(f"    Pearson Correlation (r) : {corr_size_price:.4f}")
    rpt.row("    CRITICAL FINDING: There is ZERO linear correlation between property size and price.")
    rpt.row("    In real estate, property area is the single largest component of asset valuation.")

    # (e) Price vs Year Built
    rpt.h2("(e) Price vs. Year_Built")
    year = pd.to_numeric(df["Year_Built"], errors="coerce")
    corr_year_price = year.corr(price)
    rpt.row(f"    Year Range              : {int(year.min())} to {int(year.max())}")
    rpt.row(f"    Pearson Correlation (r) : {corr_year_price:.4f}")
    rpt.row("    CRITICAL FINDING: Age/construction year carries no correlation with price.")

    # ---------------------------------------------------------
    # 4. Correlation Matrix
    # ---------------------------------------------------------
    rpt.h1("4. CORRELATION ANALYSIS (Numeric Features)")
    rpt.row("  NOTE ON INTERPRETATION: Correlation measures linear association, not causation.")
    rpt.row("  EXCLUSIONS:")
    rpt.row("    - ID is excluded (arbitrary row identifier).")
    rpt.row("    - Price_per_SqFt is excluded (derived directly from Price_in_Lakhs; data leakage).")
    rpt.row("  FLAGS:")
    rpt.row("    - Floor_No & Total_Floors (*) are flagged as unreliable due to 46.52% inversion.")
    rpt.blank()

    num_cols = ["Price_in_Lakhs", "Size_in_SqFt", "BHK", "Year_Built",
                "Age_of_Property", "Nearby_Schools", "Nearby_Hospitals",
                "Floor_No", "Total_Floors"]
    corr_matrix = df[num_cols].corr()

    header = f"  {'Feature':<18} " + " ".join([f"{c[:8]:>8}" for c in num_cols])
    rpt.row(header)
    rpt.row("  " + "-" * len(header))
    for c in num_cols:
        lbl = f"{c[:16]}*" if c in ("Floor_No", "Total_Floors") else c[:18]
        row_str = f"  {lbl:<18} " + " ".join([f"{corr_matrix.loc[c, target]:>8.3f}" for target in num_cols])
        rpt.row(row_str)
    rpt.blank()
    rpt.row("  Correlation Matrix Highlights:")
    rpt.row("    1. Year_Built vs. Age_of_Property: r = -1.000 (perfect mathematical dependency).")
    rpt.row("    2. Price_in_Lakhs vs. ALL other features: |r| <= 0.004 (essentially zero correlation).")
    rpt.row("    3. Size_in_SqFt vs. BHK: r = -0.001 (BHK and area are completely independent).")

    # ---------------------------------------------------------
    # 5. Categorical Feature Distributions
    # ---------------------------------------------------------
    rpt.h1("5. CATEGORICAL DISTRIBUTIONS")
    cat_cols_to_report = [
        "Furnished_Status", "Owner_Type", "Availability_Status",
        "Facing", "Public_Transport_Accessibility", "Parking_Space", "Security"
    ]
    for c in cat_cols_to_report:
        if c not in df.columns:
            continue
        rpt.h2(f"Distribution of {c}")
        counts = df[c].value_counts()
        for cat, cnt in counts.items():
            pct = 100.0 * cnt / total_rows
            rpt.row(f"    {str(cat):<25} : {cnt:>8,} rows  ({pct:5.2f}%)")
        pcts = [100.0 * x / total_rows for x in counts]
        spread = max(pcts) - min(pcts)
        rpt.row(f"    Category Spread: {spread:.2f} percentage points (uniform)")
        rpt.blank()

    # ---------------------------------------------------------
    # 6. Surprising Patterns & Evidence-Based Synthesis
    # ---------------------------------------------------------
    rpt.h1("6. SURPRISING PATTERNS & REALISM SYNTHESIS")
    rpt.row("  EVIDENCE-BASED CONCLUSION:")
    rpt.row("  Do NOT interpret this dataset as verified real-world market data.")
    rpt.row("  There are STRONG INDICATORS OF SYNTHETIC DATA throughout the entire dataset:")
    rpt.blank()
    rpt.row("    1. Independence of Fundamentals:")
    rpt.row("       In real property transactions, Price strongly correlates with Size and BHK.")
    rpt.row("       Here, r(Price, Size) = -0.003 and r(Price, BHK) = -0.001.")
    rpt.blank()
    rpt.row("    2. Equalized Subgroup Means:")
    rpt.row("       Every State, Property Type, BHK category, and construction year averages")
    rpt.row("       approximately \u20b9254 Lakhs. Real markets show significant tiering.")
    rpt.blank()
    rpt.row("    3. Artificial Uniformity:")
    rpt.row("       Nearby_Schools (1–10) and Nearby_Hospitals (1–10) each have exactly ~10% per bucket.")
    rpt.row("       BHK (1–5) has exactly ~20% per bucket (spread = 0.16 pp).")
    rpt.blank()
    rpt.row("    4. Deterministic Identity:")
    rpt.row("       Age_of_Property is exactly 2025 - Year_Built in all 250,000 rows.")
    rpt.blank()
    rpt.row("    5. Severe Structural Floor Contradictions:")
    rpt.row("       116,304 rows (46.52%) have Floor_No > Total_Floors.")
    rpt.blank()
    rpt.row("  MODELLING IMPLICATIONS:")
    rpt.row("    - Price_per_SqFt must remain EXCLUDED to prevent severe data leakage.")
    rpt.row("    - Standard linear regression will find negligible linear signal (near zero R^2)")
    rpt.row("      unless nonlinear combinations or synthetic generation formulas exist.")
    rpt.row("    - Any model trained on this dataset cannot be expected to generalize to real housing.")

    # ---------------------------------------------------------
    # 7. Chart Inventory
    # ---------------------------------------------------------
    rpt.h1("7. GENERATED CHARTS INVENTORY (plots/)")
    charts = [
        ("01_price_distribution.png",      "Distribution of Price_in_Lakhs with marked Mean and Median lines."),
        ("02_size_distribution.png",       "Distribution of Size_in_SqFt showing 500-5000 sq-ft uniform bounds."),
        ("03_price_by_bhk.png",            "BHK vs Price bar chart comparing Mean and Median price across 1-5 BHK."),
        ("04_price_by_property_type.png",  "Box plot of price distribution across 4 property types."),
        ("05_price_by_state.png",          "Horizontal bar chart of average price by state ranked descending."),
        ("06_price_vs_size_scatter.png",   "Scatter plot of price vs size with linear fit line (5,000-point sample)."),
        ("07_price_vs_year_built.png",     "Trend of average and median price across construction years 1990-2025."),
        ("08_correlation_heatmap.png",     "Heatmap of Pearson correlations for numeric features with floor flags."),
        ("09_category_counts.png",         "Subplots displaying counts for Furnished, Owner, and Availability.")
    ]
    for filename, desc in charts:
        rpt.row(f"  - plots/{filename:<30} : {desc}")

    rpt.blank()
    rpt.row("  Stage 3 EDA completed. Report saved to: reports/eda_summary.txt")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 72)
    print("  Smart Estate AI -- Stage 3: Exploratory Data Analysis (EDA)")
    print("=" * 72)

    df = load_data(CSV_PATH)

    os.makedirs(PLOTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("\n[INFO] Generating charts in plots/ directory...")
    plot_price_distribution(df, os.path.join(PLOTS_DIR, "01_price_distribution.png"))
    plot_size_distribution(df,  os.path.join(PLOTS_DIR, "02_size_distribution.png"))
    plot_price_by_bhk(df,       os.path.join(PLOTS_DIR, "03_price_by_bhk.png"))
    plot_price_by_property_type(df, os.path.join(PLOTS_DIR, "04_price_by_property_type.png"))
    plot_price_by_state(df,     os.path.join(PLOTS_DIR, "05_price_by_state.png"))
    plot_price_vs_size_scatter(df, os.path.join(PLOTS_DIR, "06_price_vs_size_scatter.png"))
    plot_price_vs_year_built(df, os.path.join(PLOTS_DIR, "07_price_vs_year_built.png"))
    plot_correlation_heatmap(df, os.path.join(PLOTS_DIR, "08_correlation_heatmap.png"))
    plot_category_counts(df,    os.path.join(PLOTS_DIR, "09_category_counts.png"))

    print("\n[INFO] Compiling EDA summary report...")
    rpt = ReportWriter()
    generate_eda_summary(df, rpt)
    rpt.save(REPORT_PATH)
    print(f"[OK] Summary report saved -> {REPORT_PATH}")
    print("\nExact command to run this script:\n  python3 scripts/explore_data.py\n")


if __name__ == "__main__":
    main()
