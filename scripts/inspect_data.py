"""
=============================================================
 Smart Estate AI — Dataset Reconnaissance & Data-Quality Audit
 File  : scripts/inspect_data.py
 Author: Smart Estate AI project
 Stage : 1 — Read-only audit (NO model training, NO data changes)
=============================================================

HOW TO READ THIS SCRIPT
-----------------------
Python reads files top-to-bottom.  Each block (separated by blank
lines and a comment starting with  # ---) does one clear job.
The triple-quoted strings (like this one) are called docstrings;
they document what the code does without affecting execution.
"""

# ── Standard-library imports (no installation needed) ────────────────────────
import os          # file-system helpers (path checks, makedirs)
import sys         # lets us exit early with an error message

# ── Third-party imports (pre-installed with Python's data ecosystem) ──────────
try:
    import pandas as pd      # the core data-manipulation library
    import numpy as np       # numerical operations (mean, std, etc.)
except ImportError:
    sys.exit(
        "\n[ERROR] 'pandas' or 'numpy' is not installed.\n"
        "Fix: run  python3 -m pip install pandas numpy\n"
    )

# =============================================================================
# 0.  CONFIGURATION — Change these paths if your layout differs
# =============================================================================

# Path to the raw CSV supplied by the student / Kaggle download
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "india_housing_prices.csv")

# Where the human-readable report will be saved
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "data_audit.txt")

# Columns we expect to find.  The audit will flag any that are missing.
# NOTE: This list reflects the ACTUAL columns found in the Kaggle dataset
# (250,000 rows x 23 columns).  Columns that differ from the original
# specification are noted with a comment.
EXPECTED_COLUMNS = [
    "ID",                           # identifier (dataset uses 'ID', not 'Property_ID')
    "State",
    "City",
    "Locality",
    "Property_Type",
    "BHK",
    "Size_in_SqFt",
    "Price_in_Lakhs",               # TARGET variable
    "Price_per_SqFt",               # derived / potentially leaky column
    "Year_Built",
    "Age_of_Property",
    "Furnished_Status",             # dataset uses 'Furnished_Status', not 'Furnishing_Status'
    "Floor_No",                     # dataset uses 'Floor_No', not 'Floor_Number'
    "Total_Floors",
    "Nearby_Schools",
    "Nearby_Hospitals",
    "Public_Transport_Accessibility",
    "Parking_Space",               # dataset uses 'Parking_Space', not 'Parking_Spaces'
    "Security",
    "Amenities",
    "Facing",
    "Owner_Type",
    "Availability_Status",
]

# Column name aliases: maps specification names -> actual dataset column names
# Used by audit functions that reference columns by their spec name.
COLUMN_ALIASES = {
    "Property_ID"     : "ID",
    "Furnishing_Status": "Furnished_Status",
    "Floor_Number"    : "Floor_No",
    "Parking_Spaces"  : "Parking_Space",
    "Amenities_Score" : "Amenities",   # Note: Amenities is text, not a score
}

# Tolerance for floating-point rounding when cross-checking derived columns
PRICE_TOLERANCE_PERCENT = 3.0   # allow up to 3 % rounding gap


# =============================================================================
# 1.  HELPER — Report Writer
# =============================================================================

class ReportWriter:
    """
    Accumulates text lines in memory, then writes them all at once.
    Using a class here keeps all "printing" logic in one place so
    the audit functions can stay focused on data logic.
    """

    def __init__(self):
        self._lines = []

    def h1(self, title: str):
        """Top-level section header."""
        bar = "=" * 70
        self._lines += ["", bar, f"  {title}", bar]

    def h2(self, title: str):
        """Sub-section header."""
        self._lines += ["", f"-- {title} " + "-" * max(0, 64 - len(title))]

    def row(self, text: str = ""):
        """Append one line of text."""
        self._lines.append(text)

    def save(self, path: str):
        """Write accumulated lines to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        content = "\n".join(self._lines)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(content)          # also echo to terminal
        print(f"\n[OK] Report saved -> {os.path.abspath(path)}")


# =============================================================================
# 2.  LOAD THE CSV SAFELY
# =============================================================================

def load_csv(path: str) -> pd.DataFrame:
    """
    Attempt to load the CSV with UTF-8 encoding first; fall back to
    latin-1 if the file contains non-ASCII characters (common in Indian
    city or locality names).

    A DataFrame is like a spreadsheet in memory:
      * Each ROW    = one property listing
      * Each COLUMN = one attribute (feature or target)
    """
    abs_path = os.path.abspath(path)

    # Check the file even exists before pandas tries to open it
    if not os.path.isfile(abs_path):
        sys.exit(
            f"\n[ERROR] Dataset not found at:\n  {abs_path}\n\n"
            "Please place  india_housing_prices.csv  in the project root:\n"
            f"  {os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}\n"
            "Then re-run:  python3 scripts/inspect_data.py\n"
        )

    # Try UTF-8 first, silently fall back to latin-1
    for encoding in ("utf-8", "latin-1"):
        try:
            df = pd.read_csv(abs_path, encoding=encoding, low_memory=False)
            print(f"[OK] Loaded '{os.path.basename(abs_path)}' "
                  f"with {encoding} encoding -- "
                  f"{df.shape[0]:,} rows x {df.shape[1]} columns")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as exc:
            sys.exit(f"\n[ERROR] Could not parse the CSV file.\nDetail: {exc}\n")

    sys.exit("[ERROR] File could not be decoded as UTF-8 or latin-1.\n")


# =============================================================================
# 3.  AUDIT FUNCTIONS  (each returns nothing; they write into `rpt`)
# =============================================================================

def audit_dimensions(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION A -- Dimensions
    What it does: reports shape and checks for expected columns.
    """
    rpt.h1("SECTION A -- Dataset Dimensions")
    rpt.row(f"  Total rows    (properties) : {df.shape[0]:>10,}")
    rpt.row(f"  Total columns (attributes) : {df.shape[1]:>10,}")
    rpt.row(f"  Memory usage               : {df.memory_usage(deep=True).sum() / 1e6:>9.2f} MB")

    rpt.h2("Expected vs. actual columns")
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra_cols   = [c for c in df.columns if c not in EXPECTED_COLUMNS]

    if not missing_cols and not extra_cols:
        rpt.row("  All expected columns are present with no extras.")
    else:
        if missing_cols:
            rpt.row(f"  MISSING columns  : {missing_cols}")
        if extra_cols:
            rpt.row(f"  EXTRA columns    : {extra_cols}")


def audit_dtypes(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION B -- Data Types
    What it does: lists each column's inferred type and non-null count.
    """
    rpt.h1("SECTION B -- Column Names & Inferred Data Types")
    rpt.row(f"  {'Column':<25} {'Pandas dtype':<15} {'Non-null count':>15}")
    rpt.row("  " + "-" * 58)
    for col in df.columns:
        rpt.row(f"  {col:<25} {str(df[col].dtype):<15} {df[col].count():>15,}")


def audit_missing(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION C -- Missing Values
    What it does: counts NaN per column and flags columns > 20 % missing.
    """
    rpt.h1("SECTION C -- Missing Values")
    total = len(df)
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        rpt.row("  No missing values found in any column.")
    else:
        rpt.row(f"  {'Column':<25} {'Missing Count':>15} {'% of rows':>12}")
        rpt.row("  " + "-" * 55)
        for col, cnt in missing.items():
            pct = 100.0 * cnt / total
            flag = "  [WARNING: >20%]" if pct > 20 else ""
            rpt.row(f"  {col:<25} {cnt:>15,} {pct:>11.2f}%{flag}")

    rpt.row(f"\n  Rows with at least 1 missing value: "
            f"{df.isnull().any(axis=1).sum():,} "
            f"({100 * df.isnull().any(axis=1).mean():.2f}%)")


def audit_duplicates(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION D -- Duplicates
    What it does: counts fully duplicated rows and duplicated IDs.
    NOTE: This script never drops duplicates.
    """
    rpt.h1("SECTION D -- Duplicate Rows & IDs")

    dup_rows = df.duplicated().sum()
    rpt.row(f"  Full duplicate rows   : {dup_rows:,}")

    # Check both 'Property_ID' and its alias 'ID'
    id_col = next((c for c in ["Property_ID", "ID"] if c in df.columns), None)
    if id_col:
        dup_ids = df[id_col].duplicated().sum()
        rpt.row(f"  Duplicate {id_col:<15}: {dup_ids:,}")
        if dup_ids > 0:
            duped = df[df[id_col].duplicated(keep=False)][id_col].unique()[:10]
            rpt.row(f"  Sample duplicated IDs : {list(duped)}")
    else:
        rpt.row("  No ID column found -- skipping ID duplicate check.")


def audit_categoricals(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION E -- Categorical Columns
    What it does: shows value counts for text / low-cardinality columns.
    """
    rpt.h1("SECTION E -- Categorical Columns -- Unique Value Counts")

    cat_cols = [c for c in df.columns
                if df[c].dtype == object or
                   (df[c].dtype in ("int64", "int32") and df[c].nunique() < 30)]

    for col in cat_cols:
        n_unique = df[col].nunique(dropna=True)
        rpt.h2(f"{col}  ({n_unique} unique values)")
        counts = df[col].value_counts(dropna=False).head(15)
        for val, cnt in counts.items():
            pct = 100 * cnt / len(df)
            rpt.row(f"    {str(val):<35} {cnt:>8,}  ({pct:5.1f}%)")
        if n_unique > 15:
            rpt.row(f"    ... and {n_unique - 15} more unique values")


def audit_numerics(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION F -- Numerical Summary Statistics
    What it does: shows count, mean, std, min, 25th/50th/75th pct, max.
    """
    rpt.h1("SECTION F -- Numerical Summary Statistics")
    num_df = df.select_dtypes(include="number")

    if num_df.empty:
        rpt.row("  No numeric columns detected.")
        return

    desc = num_df.describe(percentiles=[0.25, 0.50, 0.75]).T
    desc.index.name = "Column"
    rpt.row("")
    rpt.row(desc.to_string())


def audit_implausible(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION G -- Implausible / Negative / Zero Values
    What it does: flags logically impossible or highly suspicious values.
    Column names use the ACTUAL dataset names (not the original specification).
    """
    rpt.h1("SECTION G -- Implausible / Negative / Zero Values in Key Columns")

    checks = {
        "Size_in_SqFt"    : ("negative or zero area",         lambda s: s <= 0),
        "Price_in_Lakhs"  : ("negative or zero price",        lambda s: s <= 0),
        "Price_per_SqFt"  : ("zero or negative price/sqft",   lambda s: s <= 0),
        "BHK"             : ("zero or negative BHK",          lambda s: s <= 0),
        "Total_Floors"    : ("zero or negative floors",       lambda s: s <= 0),
        "Nearby_Schools"  : ("negative school count",         lambda s: s < 0),
        "Nearby_Hospitals": ("negative hospital count",       lambda s: s < 0),
    }

    for col, (label, condition) in checks.items():
        if col not in df.columns:
            rpt.row(f"  '{col}' not in dataset -- skipped.")
            continue
        series = pd.to_numeric(df[col], errors="coerce")
        flagged = series[condition(series)]
        rpt.row(f"  {col:<22}  {label:<40}  Count: {len(flagged):,}")
        if not flagged.empty:
            rpt.row(f"    Sample row indices: {list(flagged.index[:5])}")
            rpt.row(f"    Sample values     : {list(flagged.values[:5])}")

    rpt.h2("Extreme price outliers (above 99th percentile)")
    if "Price_in_Lakhs" in df.columns:
        prices = pd.to_numeric(df["Price_in_Lakhs"], errors="coerce").dropna()
        p99 = prices.quantile(0.99)
        extreme = prices[prices > p99]
        rpt.row(f"  99th-percentile cutoff : Rs {p99:,.2f} Lakhs")
        rpt.row(f"  Properties above cutoff: {len(extreme):,} rows")
        if not extreme.empty:
            rpt.row(f"  Max price found        : Rs {extreme.max():,.2f} Lakhs")


def audit_derived_column(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION H -- Cross-Column Consistency: Price_per_SqFt
    What it does: recomputes the derived column and flags discrepancies.
    Also explains data leakage risk.
    """
    rpt.h1("SECTION H -- Derived Column Consistency: Price_per_SqFt")

    needed = {"Price_in_Lakhs", "Size_in_SqFt", "Price_per_SqFt"}
    if not needed.issubset(df.columns):
        rpt.row(f"  Missing column(s): {needed - set(df.columns)} -- check skipped.")
        return

    p   = pd.to_numeric(df["Price_in_Lakhs"],  errors="coerce")
    s   = pd.to_numeric(df["Size_in_SqFt"],    errors="coerce")
    pps = pd.to_numeric(df["Price_per_SqFt"],  errors="coerce")

    # Formula: Price_per_SqFt = (Price_in_Lakhs * 100000) / Size_in_SqFt
    computed = (p * 100_000) / s

    valid = (p.notna()) & (s.notna()) & (pps.notna()) & (s > 0) & (p > 0)
    n_valid = valid.sum()
    rpt.row(f"  Rows usable for this check : {n_valid:,}")

    if n_valid == 0:
        rpt.row("  No rows with valid Price, Size, AND Price_per_SqFt.")
        return

    diff_pct = ((computed - pps).abs() / pps.abs() * 100).where(pps != 0)

    consistent   = (diff_pct[valid] <= PRICE_TOLERANCE_PERCENT).sum()
    inconsistent = (diff_pct[valid] >  PRICE_TOLERANCE_PERCENT).sum()

    rpt.row(f"  Consistent rows (within {PRICE_TOLERANCE_PERCENT}%) : {consistent:,}")
    rpt.row(f"  Inconsistent rows (gap > {PRICE_TOLERANCE_PERCENT}%): {inconsistent:,}")

    if inconsistent > 0:
        bad_idx = diff_pct[valid][diff_pct[valid] > PRICE_TOLERANCE_PERCENT].index[:5]
        rpt.row("  Sample inconsistent rows (index | Price | Size | Stored | Computed):")
        for i in bad_idx:
            rpt.row(f"    [{i}]  Rs {p[i]:.2f}L  |  {s[i]:.0f} sqft  "
                    f"|  stored {pps[i]:,.0f}  |  computed {computed[i]:,.0f}")

    rpt.row("")
    rpt.row("  DATA LEAKAGE WARNING:")
    rpt.row("  Price_per_SqFt = (Price_in_Lakhs * 100000) / Size_in_SqFt")
    rpt.row("  It directly encodes the target variable.  Do NOT use it as")
    rpt.row("  an ML feature -- the model would be memorising the answer.")


def audit_age_vs_year(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION I -- Age_of_Property vs. Year_Built Consistency
    What it does: checks internal logical consistency without assuming
    the current year or which convention was used.

    From the audit: Year_Built + Age_of_Property = 2025 for ALL rows.
    Spread = 0 years, which is perfectly consistent.
    We highlight this as a finding: the dataset uses 2025 as reference year.
    """
    rpt.h1("SECTION I -- Age_of_Property vs. Year_Built Consistency")

    if "Age_of_Property" not in df.columns or "Year_Built" not in df.columns:
        rpt.row("  One or both columns (Age_of_Property, Year_Built) not found -- skipped.")
        return

    age  = pd.to_numeric(df["Age_of_Property"], errors="coerce")
    year = pd.to_numeric(df["Year_Built"],       errors="coerce")

    valid = age.notna() & year.notna()
    rpt.row(f"  Rows with both columns non-null: {valid.sum():,}")

    neg_age = (age[valid] < 0).sum()
    rpt.row(f"  Rows with negative Age_of_Property  : {neg_age:,}  [impossible]")

    # Estimate reference year from the data itself (median of Year_Built + Age)
    implied = year[valid] + age[valid]
    estimated_ref_year = int(implied.median())
    spread  = implied.max() - implied.min()

    rpt.row(f"  Estimated reference year (from data): {estimated_ref_year}")
    rpt.row(f"  Spread of (Year_Built + Age)         : {spread:.0f} years")
    rpt.row(f"  (Small spread = consistent; large spread = mixed conventions or errors)")

    future_built = (year[valid] > estimated_ref_year).sum()
    rpt.row(f"  Rows with Year_Built > reference year: {future_built:,}")

    threshold = 5   # allow +/-5 years as rounding / convention slack
    inconsistent = ((implied - estimated_ref_year).abs() > threshold).sum()
    rpt.row(f"  Rows where |Year_Built + Age - {estimated_ref_year}| > {threshold}: {inconsistent:,}")


def audit_floor_bhk(df: pd.DataFrame, rpt: ReportWriter):
    """
    SECTION J -- Suspicious BHK / Floor / Total_Floors Combinations
    What it does: applies domain knowledge to flag logical impossibilities
    and statistically rare combinations.
    Note: dataset uses 'Floor_No' (not 'Floor_Number').
    """
    rpt.h1("SECTION J -- Suspicious BHK / Floor / Total_Floors Combinations")

    # Accept either 'Floor_Number' or the alias 'Floor_No'
    floor_col = next((c for c in ["Floor_Number", "Floor_No"] if c in df.columns), None)

    if floor_col and "Total_Floors" in df.columns:
        fn = pd.to_numeric(df[floor_col],       errors="coerce")
        tf = pd.to_numeric(df["Total_Floors"],  errors="coerce")
        bad = (fn > tf) & fn.notna() & tf.notna()
        rpt.row(f"  {floor_col} > Total_Floors : {bad.sum():,} rows  [confirmed error]")
        neg_floor = (fn < 0).sum()
        rpt.row(f"  {floor_col} < 0 (basement?): {neg_floor:,} rows")

    if "BHK" in df.columns:
        bhk = pd.to_numeric(df["BHK"], errors="coerce")
        rpt.row(f"  BHK < 1 (impossible)              : {(bhk < 1).sum():,} rows")
        rpt.row(f"  BHK > 8 (rare, worth reviewing)   : {(bhk > 8).sum():,} rows")
        unique_bhk = sorted([int(x) for x in bhk.dropna().unique()])
        rpt.row(f"  All BHK values present            : {unique_bhk}")

    if "BHK" in df.columns and "Size_in_SqFt" in df.columns:
        bhk  = pd.to_numeric(df["BHK"],          errors="coerce")
        size = pd.to_numeric(df["Size_in_SqFt"], errors="coerce")
        tiny = (bhk == 1) & (size < 200) & bhk.notna() & size.notna()
        rpt.row(f"  1-BHK with size < 200 sq-ft       : {tiny.sum():,} rows  [suspicious]")
        huge = (bhk == 2) & (size > 10_000) & bhk.notna() & size.notna()
        rpt.row(f"  2-BHK with size > 10,000 sq-ft    : {huge.sum():,} rows  [suspicious]")


# =============================================================================
# 4.  MAIN -- Wire everything together
# =============================================================================

def main():
    print("\n" + "=" * 70)
    print("  Smart Estate AI -- Data Audit Script")
    print("=" * 70)

    df = load_csv(CSV_PATH)

    rpt = ReportWriter()
    rpt.h1("Smart Estate AI -- Data Quality Audit Report")
    rpt.row(f"  Dataset file : {os.path.abspath(CSV_PATH)}")
    rpt.row(f"  Rows x Cols  : {df.shape[0]:,} x {df.shape[1]}")
    rpt.row("  This script is READ-ONLY.  The CSV was NOT modified.")

    audit_dimensions(df,      rpt)
    audit_dtypes(df,          rpt)
    audit_missing(df,         rpt)
    audit_duplicates(df,      rpt)
    audit_categoricals(df,    rpt)
    audit_numerics(df,        rpt)
    audit_implausible(df,     rpt)
    audit_derived_column(df,  rpt)
    audit_age_vs_year(df,     rpt)
    audit_floor_bhk(df,       rpt)

    rpt.h1("AUDIT COMPLETE")
    rpt.row("  Next step: review this report with your instructor / mentor.")
    rpt.row("  Do NOT proceed to data-cleaning or model training until the")
    rpt.row("  findings above have been understood and discussed.")
    rpt.row("")
    rpt.row("  Output file:")
    rpt.row("    reports/data_audit.txt -- full human-readable audit report")
    rpt.row("")

    rpt.save(REPORT_PATH)


# Python entry point:
# This block runs only when you execute the file directly with python3.
# It does NOT run if another file imports this script as a module.
if __name__ == "__main__":
    main()
