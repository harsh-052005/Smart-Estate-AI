"""
=============================================================
 Smart Estate AI — Investigation of Audit Findings
 File  : scripts/investigate_data.py
 Stage : 2 — Read-only deep-dive into flagged issues
 Run   : python3 scripts/investigate_data.py
=============================================================

This script investigates the five issues flagged by the
audit (inspect_data.py).  It never modifies the original CSV.

WHAT THIS SCRIPT IS NOT:
  - It is not data cleaning.
  - It does not drop, fix, or impute any values.
  - It reports evidence and lets YOU make decisions.
"""

import os
import sys

try:
    import pandas as pd
    import numpy as np
except ImportError:
    sys.exit(
        "\n[ERROR] pandas or numpy not installed.\n"
        "Fix: python3 -m pip install pandas numpy\n"
    )

# =============================================================================
# PATHS
# =============================================================================

CSV_PATH    = os.path.join(os.path.dirname(__file__), "..", "india_housing_prices.csv")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "data_investigation.txt")

# =============================================================================
# REPORT WRITER  (same pattern as inspect_data.py for consistency)
# =============================================================================

class ReportWriter:
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
        print(content)
        print(f"\n[OK] Investigation report saved -> {os.path.abspath(path)}")


# =============================================================================
# LOAD
# =============================================================================

def load_csv(path):
    """Open the CSV read-only; try UTF-8, fall back to latin-1."""
    abs_path = os.path.abspath(path)
    if not os.path.isfile(abs_path):
        sys.exit(
            f"\n[ERROR] CSV not found:\n  {abs_path}\n"
            "Place india_housing_prices.csv in the project root and re-run.\n"
        )
    for enc in ("utf-8", "latin-1"):
        try:
            df = pd.read_csv(abs_path, encoding=enc, low_memory=False)
            print(f"[OK] Loaded {df.shape[0]:,} rows x {df.shape[1]} columns ({enc})")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            sys.exit(f"[ERROR] Could not parse CSV: {e}")
    sys.exit("[ERROR] Could not decode file.")


# =============================================================================
# INVESTIGATION 1 — FLOOR INCONSISTENCY
# =============================================================================

def investigate_floors(df, rpt):
    """
    ISSUE: Many rows have Floor_No > Total_Floors.
    A property cannot be on a floor that does not exist in its building.

    We investigate:
      (a) Exact count and percentage of inconsistent rows.
      (b) Representative examples of the problem rows.
      (c) Distributions of both columns.
      (d) Hypothetical swap test: if we swapped the two columns, how many
          rows would become valid, and how many would remain invalid?
      (e) Interpretation and recommendation.

    The function returns a dict of computed values so main() can use them
    to build a dynamic summary instead of hard-coding conclusions.
    """
    rpt.h1("INVESTIGATION 1 — Floor_No vs Total_Floors Inconsistency")

    # Guard: both columns must exist
    for col in ("Floor_No", "Total_Floors"):
        if col not in df.columns:
            rpt.row(f"  [SKIP] Column '{col}' not found in dataset.")
            return {"n_bad": None, "still_bad_after_swap": None, "fixed_by_swap": None}

    # Convert to numeric; non-numeric cells become NaN
    fn = pd.to_numeric(df["Floor_No"],    errors="coerce")
    tf = pd.to_numeric(df["Total_Floors"], errors="coerce")

    total_rows = len(df)

    # Rows where BOTH values are present (we can only check consistency there)
    both_valid   = fn.notna() & tf.notna()
    n_both_valid = both_valid.sum()

    # --- ORIGINAL inconsistency: Floor_No > Total_Floors ---
    # (a property on floor 22 of a 1-floor building is impossible)
    orig_bad_mask = (fn > tf) & both_valid
    n_orig_bad    = orig_bad_mask.sum()
    pct_orig_bad  = 100.0 * n_orig_bad / total_rows

    rpt.h2("(a) Frequency of Floor_No > Total_Floors (original data)")
    rpt.row(f"  Total rows in dataset                          : {total_rows:>10,}")
    rpt.row(f"  Rows where both Floor_No and Total_Floors exist: {n_both_valid:>10,}")
    rpt.row(f"  Rows where Floor_No > Total_Floors (impossible): {n_orig_bad:>10,}  ({pct_orig_bad:.2f}% of all rows)")
    rpt.row(f"  Consistent rows (Floor_No <= Total_Floors)     : {n_both_valid - n_orig_bad:>10,}  ({100*(n_both_valid - n_orig_bad)/total_rows:.2f}%)")

    rpt.h2("(b) Representative examples of inconsistent rows")
    bad_df = df[orig_bad_mask][["ID", "Floor_No", "Total_Floors",
                                "Property_Type", "BHK"]].head(10)
    rpt.blank()
    rpt.row(bad_df.to_string(index=False))
    rpt.blank()

    rpt.h2("(c) Distributions of Floor_No and Total_Floors")
    rpt.row("  Floor_No — value counts (top 15, sorted):")
    fn_counts = fn.value_counts().sort_index().head(15)
    for val, cnt in fn_counts.items():
        pct = 100 * cnt / total_rows
        rpt.row(f"    Floor {int(val):>3} : {cnt:>7,} rows  ({pct:5.1f}%)")

    rpt.blank()
    rpt.row("  Total_Floors — value counts (top 15, sorted):")
    tf_counts = tf.value_counts().sort_index().head(15)
    for val, cnt in tf_counts.items():
        pct = 100 * cnt / total_rows
        rpt.row(f"    {int(val):>3} floors : {cnt:>7,} rows  ({pct:5.1f}%)")

    rpt.h2("(d) Hypothetical swap test — what happens if we treat Floor_No as "
           "Total_Floors and vice versa?")
    rpt.blank()
    rpt.row("  After a hypothetical swap of the two columns across the dataset:")
    rpt.row("    swapped_Floor_No     = original Total_Floors")
    rpt.row("    swapped_Total_Floors = original Floor_No")
    rpt.blank()

    # 1. Original rows where Floor_No > Total_Floors: n_orig_bad, pct_orig_bad
    # 2. Rows violating Floor_No <= Total_Floors after hypothetical swap:
    #    swapped_Floor_No > swapped_Total_Floors <=> original Total_Floors > Floor_No
    swap_violating_mask = (tf > fn) & both_valid
    n_swap_violating    = swap_violating_mask.sum()
    pct_swap_violating  = 100.0 * n_swap_violating / total_rows

    # 3. Rows valid after hypothetical swap:
    #    swapped_Floor_No <= swapped_Total_Floors <=> original Total_Floors <= Floor_No
    swap_valid_mask     = (tf <= fn) & both_valid
    n_swap_valid        = swap_valid_mask.sum()
    pct_swap_valid      = 100.0 * n_swap_valid / total_rows

    # 4. Impact on original inconsistencies (where fn > tf):
    #    In all original inconsistent rows, tf < fn, which means swapped_Floor_No < swapped_Total_Floors.
    #    Hence, swapping resolves 100% of the original inconsistent rows.
    #    However, swapping the whole columns introduces new violations from previously valid rows (tf > fn).
    orig_resolved_by_swap = n_orig_bad
    pct_orig_resolved     = 100.0 * orig_resolved_by_swap / n_orig_bad if n_orig_bad > 0 else 0.0

    rpt.row(f"  Original rows where Floor_No > Total_Floors          : {n_orig_bad:>10,}  ({pct_orig_bad:.2f}% of all rows)")
    rpt.row(f"  Rows violating Floor_No <= Total_Floors after swap   : {n_swap_violating:>10,}  ({pct_swap_violating:.2f}% of all rows)")
    rpt.row(f"  Rows valid after the swap                            : {n_swap_valid:>10,}  ({pct_swap_valid:.2f}% of all rows)")
    rpt.blank()
    rpt.row(f"  Original inconsistent rows resolved by swap          : {orig_resolved_by_swap:>10,} of {n_orig_bad:,} ({pct_orig_resolved:.1f}%)")
    rpt.row(f"  New violations created by swapping valid rows        : {n_swap_violating:>10,}  ({pct_swap_violating:.2f}% of all rows)")
    rpt.blank()

    # --- Dynamic conclusion based on computed values ---
    if n_orig_bad == 0:
        swap_conclusion = "No inconsistencies exist — no swap needed."
    elif n_swap_violating == 0:
        swap_conclusion = (
            f"Swapping resolves ALL {n_orig_bad:,} inconsistencies (100.0%) and creates "
            "zero new violations dataset-wide. This provides strong evidence that the "
            "two column labels were swapped."
        )
    else:
        swap_conclusion = (
            f"Swapping resolves all {n_orig_bad:,} original inconsistent rows (100.0%). "
            f"However, applying a hypothetical column swap across the entire dataset causes "
            f"{n_swap_violating:,} originally valid rows ({pct_swap_violating:.2f}%) to violate "
            f"Floor_No <= Total_Floors (leaving {n_swap_valid:,} valid rows, {pct_swap_valid:.2f}%). "
            f"Consequently, dataset-wide violations actually increase from {n_orig_bad:,} to {n_swap_violating:,}. "
            "Swapping columns does NOT resolve the inconsistency dataset-wide. This indicates the issue "
            "is not a simple whole-column label reversal, but rather row-level inconsistencies, data-entry "
            "errors, or synthetic generation artifacts."
        )

    rpt.row(f"  FINDING: {swap_conclusion}")

    rpt.h2("(e) Recommendation")
    rpt.row("  Do NOT use Floor_No or Total_Floors as ML features until the")
    rpt.row("  swap hypothesis is verified against the original data source.")
    rpt.row("  Options to discuss at the cleaning stage:")
    rpt.row("    1. Swap the two columns — ONLY if the data owner or documentation")
    rpt.row("       confirms the labels were reversed during dataset creation.")
    rpt.row("    2. Drop both columns and accept the loss of floor information.")
    rpt.row("    3. Derive a single feature: 'is_top_floor' (Floor_No == Total_Floors).")
    rpt.row("    4. Flag rows where Floor_No > Total_Floors and evaluate model")
    rpt.row("       performance with and without them.")

    # Return computed values for use in the dynamic summary
    return {
        "n_orig_bad"               : int(n_orig_bad),
        "pct_orig_bad"             : round(pct_orig_bad, 2),
        "n_swap_violating"         : int(n_swap_violating),
        "pct_swap_violating"       : round(pct_swap_violating, 2),
        "n_swap_valid"             : int(n_swap_valid),
        "pct_swap_valid"           : round(pct_swap_valid, 2),
        "orig_resolved_by_swap"    : int(orig_resolved_by_swap),
        "swap_resolves_all_orig"   : (orig_resolved_by_swap == n_orig_bad and n_orig_bad > 0),
        "swap_fixes_whole_dataset" : (n_swap_violating == 0 and n_orig_bad > 0),
    }


# =============================================================================
# INVESTIGATION 2 — PRICE PER SQUARE FOOT
# =============================================================================

def investigate_price_per_sqft(df, rpt):
    """
    ISSUE: The stored Price_per_SqFt does not match the formula
           (Price_in_Lakhs * 100000) / Size_in_SqFt in most rows.

    We investigate:
      (a) What are the actual stored values?  What scale are they on?
      (b) Recompute the correct value and compare.
      (c) Why would using this column in a model be data leakage?
    """
    rpt.h1("INVESTIGATION 2 — Price_per_SqFt Column Analysis")

    price = pd.to_numeric(df["Price_in_Lakhs"], errors="coerce")
    size  = pd.to_numeric(df["Size_in_SqFt"],   errors="coerce")
    pps   = pd.to_numeric(df["Price_per_SqFt"], errors="coerce")

    rpt.h2("(a) What are the stored Price_per_SqFt values?")

    desc = pps.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.99])
    rpt.row("")
    for stat, val in desc.items():
        rpt.row(f"    {stat:<8}: {val:.4f}")

    zero_count = (pps == 0).sum()
    rpt.blank()
    rpt.row(f"  Rows with stored value = 0.0 : {zero_count:,}  ({100*zero_count/len(df):.2f}%)")
    rpt.row(f"  Min non-zero value           : {pps[pps > 0].min():.4f}")
    rpt.row(f"  Max value                    : {pps.max():.4f}")
    rpt.blank()
    rpt.row("  OBSERVATION: Values range from 0 to ~1.0.  This is NOT rupees per")
    rpt.row("  square foot (which should be in the range 4,000 – 30,000 for India).")
    rpt.row("  The column appears to be stored as a ratio or an unknown scaled unit.")

    rpt.h2("(b) Recomputing the correct Price_per_SqFt (rupees / sq-ft)")

    # Compute: convert Lakhs to rupees then divide by area
    valid       = price.notna() & size.notna() & (size > 0) & (price > 0)
    computed    = (price[valid] * 100_000) / size[valid]

    rpt.row("")
    rpt.row("  Formula used:  computed = (Price_in_Lakhs x 100,000) / Size_in_SqFt")
    rpt.row("")
    comp_desc = computed.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    for stat, val in comp_desc.items():
        rpt.row(f"    {stat:<8}: Rs {val:>12,.2f} / sq-ft")

    rpt.blank()
    rpt.row("  OBSERVATION: Recomputed values are in the range ~2,000 – 20,000")
    rpt.row("  rupees per sq-ft, which is consistent with real Indian property prices.")
    rpt.row("  The stored column is clearly on a different, unknown scale.")

    rpt.h2("(c) Side-by-side sample: stored vs. computed")
    sample_idx = df[(size > 0) & (price > 0)].index[:8]
    rpt.row("")
    rpt.row(f"  {'ID':>6}  {'Price(L)':>10}  {'Size(sqft)':>10}  "
            f"{'Stored PpSqFt':>14}  {'Computed (Rs)':>15}")
    rpt.row("  " + "-" * 65)
    for i in sample_idx:
        pid  = df.loc[i, "ID"]
        p    = price[i]
        s    = size[i]
        st   = pps[i]
        comp = (p * 100_000) / s if s > 0 else float("nan")
        rpt.row(f"  {int(pid):>6}  {p:>10.2f}  {int(s):>10,}  "
                f"{st:>14.4f}  {comp:>15,.0f}")

    rpt.h2("(d) Why Price_per_SqFt must NOT be used as an ML feature")
    rpt.row("")
    rpt.row("  DATA LEAKAGE explained simply:")
    rpt.row("")
    rpt.row("  When you train a model, you show it 'inputs' and ask it to")
    rpt.row("  predict an 'output'.  Here:")
    rpt.row("    INPUT  (features) = City, BHK, Size, Year_Built, ...")
    rpt.row("    OUTPUT (target)   = Price_in_Lakhs")
    rpt.row("")
    rpt.row("  Price_per_SqFt is computed FROM Price_in_Lakhs:")
    rpt.row("    Price_per_SqFt = (Price_in_Lakhs x 100,000) / Size_in_SqFt")
    rpt.row("")
    rpt.row("  So if the model sees Price_per_SqFt as an input, it has ALREADY")
    rpt.row("  seen a transformed version of the answer it's supposed to predict.")
    rpt.row("  This is like letting a student see the answer key during an exam.")
    rpt.row("")
    rpt.row("  In practice the model would score perfectly on training data but")
    rpt.row("  fail completely on real new listings — because new listings won't")
    rpt.row("  have a price yet (that's the whole point of prediction!).")
    rpt.row("")
    rpt.row("  CONCLUSION: Drop Price_per_SqFt before any modelling step.")


# =============================================================================
# INVESTIGATION 3 — AGE AND CONSTRUCTION YEAR
# =============================================================================

def investigate_age_year(df, rpt):
    """
    ISSUE: The audit found Year_Built + Age_of_Property = 2025 for every row
           (spread = 0).  We verify this and discuss implications.

    We investigate:
      (a) Is the sum truly constant across all 250,000 rows?
      (b) What does this tell us about how Age was created?
      (c) How would using the 'current year' (e.g. 2026) affect predictions?
    """
    rpt.h1("INVESTIGATION 3 — Age_of_Property vs. Year_Built")

    age  = pd.to_numeric(df["Age_of_Property"], errors="coerce")
    year = pd.to_numeric(df["Year_Built"],       errors="coerce")

    valid = age.notna() & year.notna()
    implied = year[valid] + age[valid]

    rpt.h2("(a) Is Year_Built + Age_of_Property constant?")
    rpt.blank()
    rpt.row(f"  Rows checked       : {valid.sum():,}")
    rpt.row(f"  Min of (Y + A)     : {implied.min():.0f}")
    rpt.row(f"  Max of (Y + A)     : {implied.max():.0f}")
    rpt.row(f"  Spread (max - min) : {implied.max() - implied.min():.0f} years")
    rpt.row(f"  Unique values      : {implied.nunique()}")
    rpt.blank()

    if implied.nunique() == 1:
        constant = int(implied.iloc[0])
        rpt.row(f"  FINDING: Year_Built + Age_of_Property = {constant} for EVERY row.")
        rpt.row(f"  This is a perfect mathematical identity — no exceptions.")
    else:
        counts = implied.value_counts().sort_index()
        rpt.row("  FINDING: Sum is NOT constant.  Distribution:")
        for val, cnt in counts.items():
            rpt.row(f"    {int(val)} : {cnt:,} rows")

    rpt.h2("(b) What this tells us about how Age was created")
    rpt.blank()
    rpt.row("  If Year_Built + Age = 2025 for every row, then:")
    rpt.row("")
    rpt.row("    Age_of_Property = 2025 - Year_Built")
    rpt.row("")
    rpt.row("  This means Age was NOT collected separately — it was COMPUTED")
    rpt.row("  from Year_Built using 2025 as the reference year.")
    rpt.row("")
    rpt.row("  IMPLICATION 1 — Redundancy:")
    rpt.row("    Age and Year_Built carry identical information.  Using BOTH")
    rpt.row("    as model features is redundant (like using Celsius and Fahrenheit")
    rpt.row("    temperature simultaneously).  Keep only one.")
    rpt.row("")
    rpt.row("  IMPLICATION 2 — No information loss:")
    rpt.row("    Either column fully represents the property's age.  The choice")
    rpt.row("    between them is a modelling preference, not a data problem.")

    rpt.h2("(c) Risk of using the 'current year' instead of 2025")
    rpt.blank()
    rpt.row("  Suppose a future user runs the model in 2027 and tries to re-derive")
    rpt.row("  age from Year_Built using 'today's year':")
    rpt.row("")
    rpt.row("    New age = 2027 - Year_Built")
    rpt.row("")
    rpt.row("  For a property built in 2010:")
    rpt.row("    Dataset age    =  2025 - 2010 = 15 years")
    rpt.row("    Re-derived age =  2027 - 2010 = 17 years  (2 years off)")
    rpt.row("")
    rpt.row("  This 2-year gap can shift predicted prices if the model learned")
    rpt.row("  that age of 15 = one price tier and age of 17 = a lower tier.")
    rpt.row("")
    rpt.row("  RECOMMENDATION:")
    rpt.row("    - Use Year_Built as the feature (absolute, never changes).")
    rpt.row("    - Document that Age_of_Property = 2025 - Year_Built.")
    rpt.row("    - Do NOT compute Age dynamically at prediction time unless")
    rpt.row("      the model was retrained with that convention.")
    rpt.row("    - Do NOT assume 2025 is the real data-collection year;")
    rpt.row("      it is only the value embedded in the formula.")

    # Show a few examples for clarity
    rpt.h2("(d) Sample rows verifying the identity")
    sample = df[["ID", "Year_Built", "Age_of_Property"]].head(8).copy()
    sample["Year + Age"] = (
        pd.to_numeric(sample["Year_Built"], errors="coerce") +
        pd.to_numeric(sample["Age_of_Property"], errors="coerce")
    ).astype("Int64")
    rpt.blank()
    rpt.row(sample.to_string(index=False))

    # Return computed values for the dynamic summary
    return {
        "n_unique_sum" : int(implied.nunique()) if valid.any() else None,
        "spread"       : int(implied.max() - implied.min()) if valid.any() else None,
        "ref_year"     : int(implied.median()) if valid.any() else None,
    }


# =============================================================================
# INVESTIGATION 4 — DATASET REALISM
# =============================================================================

def investigate_realism(df, rpt):
    """
    ISSUE: The dataset claims to be synthetic.  We check the distributions
    for signs that support or contradict this — but we only report evidence.

    Signs of a synthetic dataset often include:
      - Perfectly uniform category distributions
      - Prices that stop exactly at a round cap
      - IDs that are perfectly sequential
      - No missing values whatsoever
      - Regular spacing in numeric columns
    """
    rpt.h1("INVESTIGATION 4 — Dataset Realism Check")

    price = pd.to_numeric(df["Price_in_Lakhs"], errors="coerce")
    size  = pd.to_numeric(df["Size_in_SqFt"],   errors="coerce")

    # ── Price distribution ────────────────────────────────────────────────────
    rpt.h2("(a) Price_in_Lakhs distribution")
    rpt.blank()
    desc = price.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.99])
    for stat, val in desc.items():
        rpt.row(f"    {stat:<6}: Rs {val:>10,.2f} Lakhs")

    price_max = price.max()
    price_min = price.min()
    round_max = (price_max == round(price_max, -1))  # e.g. 500, 1000
    rpt.blank()
    rpt.row(f"  Min price : Rs {price_min:.2f} Lakhs")
    rpt.row(f"  Max price : Rs {price_max:.2f} Lakhs")
    rpt.row(f"  Max is a round number? : {round_max}")
    n_at_max = (price == price_max).sum()
    n_at_min = (price == price_min).sum()
    rpt.row(f"  Rows exactly at max (Rs {price_max:.0f}L) : {n_at_max:,}  "
            f"(suggests a hard cap)")
    rpt.row(f"  Rows exactly at min (Rs {price_min:.0f}L) : {n_at_min:,}  "
            f"(suggests a hard floor)")

    # ── Size distribution ─────────────────────────────────────────────────────
    rpt.h2("(b) Size_in_SqFt distribution")
    rpt.blank()
    desc_s = size.describe(percentiles=[0.25, 0.5, 0.75])
    for stat, val in desc_s.items():
        rpt.row(f"    {stat:<6}: {val:>8,.1f} sq-ft")

    size_min = size.min()
    size_max = size.max()
    rpt.blank()
    rpt.row(f"  Min size : {size_min:,.0f} sq-ft")
    rpt.row(f"  Max size : {size_max:,.0f} sq-ft")
    n_at_size_max = (size == size_max).sum()
    n_at_size_min = (size == size_min).sum()
    rpt.row(f"  Rows at max ({size_max:,.0f} sqft) : {n_at_size_max:,}  (cap?)")
    rpt.row(f"  Rows at min ({size_min:,.0f} sqft) : {n_at_size_min:,}  (floor?)")

    # ── BHK uniformity ────────────────────────────────────────────────────────
    rpt.h2("(c) BHK distribution — checking for suspicious uniformity")
    rpt.blank()
    bhk_counts = df["BHK"].value_counts().sort_index()
    total = len(df)
    for val, cnt in bhk_counts.items():
        pct = 100 * cnt / total
        rpt.row(f"    BHK {val} : {cnt:>7,} rows  ({pct:.2f}%)")
    bhk_pcts = [100 * c / total for c in bhk_counts]
    spread = max(bhk_pcts) - min(bhk_pcts)
    rpt.blank()
    rpt.row(f"  Spread between highest and lowest %: {spread:.2f} percentage points")
    rpt.row("  (Real datasets: spread typically > 20 pp due to natural demand;")
    rpt.row("   Synthetic datasets: spread often < 1 pp when category is uniform)")

    # ── State / City / Property_Type ─────────────────────────────────────────
    rpt.h2("(d) State and City distributions")
    rpt.blank()
    for col in ["State", "Property_Type"]:
        if col not in df.columns:
            continue
        counts = df[col].value_counts()
        n_unique = counts.nunique()
        rpt.row(f"  {col} ({n_unique} unique):")
        for val, cnt in counts.items():
            pct = 100 * cnt / total
            rpt.row(f"    {str(val):<35} {cnt:>8,}  ({pct:5.2f}%)")
        pcts = [100 * c / total for c in counts]
        sp = max(pcts) - min(pcts)
        rpt.row(f"    Spread: {sp:.2f} pp")
        rpt.blank()

    # ── Locality uniqueness ───────────────────────────────────────────────────
    rpt.h2("(e) Locality names — real or generic?")
    rpt.blank()
    locality_sample = df["Locality"].unique()[:20]
    rpt.row("  Sample of 20 unique locality names:")
    for loc in locality_sample:
        rpt.row(f"    {loc}")
    rpt.blank()
    n_loc = df["Locality"].nunique()
    rpt.row(f"  Total unique localities : {n_loc:,}")
    rpt.row("  Note: names like 'Locality_84' are placeholders, not real area names.")
    rpt.row("  This is a strong indicator of a synthetically generated dataset.")

    # ── Nearby facilities uniformity ──────────────────────────────────────────
    rpt.h2("(f) Nearby_Schools and Nearby_Hospitals — distribution check")
    rpt.blank()
    for col in ["Nearby_Schools", "Nearby_Hospitals"]:
        if col not in df.columns:
            continue
        counts = pd.to_numeric(df[col], errors="coerce").value_counts().sort_index()
        rpt.row(f"  {col}:")
        for val, cnt in counts.items():
            pct = 100 * cnt / total
            rpt.row(f"    {int(val):>3} : {cnt:>7,} rows ({pct:.2f}%)")
        pcts = [100 * c / total for c in counts]
        rpt.row(f"  Spread: {max(pcts) - min(pcts):.2f} pp  "
                f"({'Suspiciously uniform — likely random-sampled' if max(pcts) - min(pcts) < 1.5 else 'Some variation'} )")
        rpt.blank()

    # ── Repeated combinations ────────────────────────────────────────────────
    rpt.h2("(g) Repeated (City, BHK, Size_in_SqFt, Price_in_Lakhs) combinations")
    rpt.blank()
    combo_cols = ["City", "BHK", "Size_in_SqFt", "Price_in_Lakhs"]
    if all(c in df.columns for c in combo_cols):
        combo_dupes = df.duplicated(subset=combo_cols).sum()
        rpt.row(f"  Duplicate (City, BHK, Size, Price) combos : {combo_dupes:,}")
        if combo_dupes == 0:
            rpt.row("  No exact combination repeats — good.")
        else:
            rpt.row("  Some property specs repeat exactly even across different rows.")

    rpt.h2("(h) Summary of realism evidence")
    rpt.blank()

    # Build signals list dynamically from the data so we do not hard-code counts
    total = len(df)
    price = pd.to_numeric(df.get("Price_in_Lakhs", pd.Series(dtype=float)), errors="coerce")
    synth_signals = []

    # Signal 1: generic locality codes
    if "Locality" in df.columns:
        sample_locs = df["Locality"].dropna().unique()[:5]
        if all(str(loc).startswith("Locality_") for loc in sample_locs):
            synth_signals.append("locality names are generic codes (e.g. 'Locality_84')")

    # Signal 2: zero missing values
    if df.isnull().sum().sum() == 0:
        synth_signals.append(f"zero missing values across {total:,} rows")

    # Signal 3: BHK spread
    if "BHK" in df.columns:
        bhk_pcts = [100 * c / total for c in df["BHK"].value_counts()]
        bhk_spread = max(bhk_pcts) - min(bhk_pcts)
        if bhk_spread < 1.0:
            synth_signals.append(f"BHK categories nearly uniform (spread {bhk_spread:.2f} pp)")

    # Signal 4: hard price ceiling
    if price.notna().any():
        pmax = price.max()
        n_at_max = (price == pmax).sum()
        if n_at_max > 100 and pmax == round(pmax, -1):
            synth_signals.append(
                f"hard price ceiling at Rs {pmax:.0f}L ({n_at_max:,} rows exactly at max)"
            )

    # Signal 5: nearby facilities uniformity
    for fac_col in ["Nearby_Schools", "Nearby_Hospitals"]:
        if fac_col in df.columns:
            fac_pcts = [100 * c / total
                        for c in pd.to_numeric(df[fac_col], errors="coerce").value_counts()]
            if fac_pcts and (max(fac_pcts) - min(fac_pcts)) < 1.0:
                synth_signals.append(f"{fac_col} values are uniformly distributed")
                break   # report once to avoid duplication

    # Signal 6: Age deterministic
    if "Age_of_Property" in df.columns and "Year_Built" in df.columns:
        age_s  = pd.to_numeric(df["Age_of_Property"], errors="coerce")
        year_s = pd.to_numeric(df["Year_Built"],       errors="coerce")
        implied_s = (age_s + year_s).dropna()
        if implied_s.nunique() == 1:
            synth_signals.append(
                f"Age_of_Property = {int(implied_s.iloc[0])} - Year_Built for every row"
            )

    rpt.row(f"  Indicators consistent with a synthetically generated dataset ({len(synth_signals)} found):")
    for sig in synth_signals:
        rpt.row(f"    - {sig}")
    rpt.blank()
    rpt.row("  Indicators that need further investigation:")
    rpt.row("    - State/City distributions show variation (not perfectly flat)")
    rpt.row("    - Price_in_Lakhs contains realistic decimal values")
    # Evidence-based conclusion: strong indicators of synthetic data, not confirmed
    if len(synth_signals) >= 4:
        rpt.row("  ASSESSMENT: There are strong indicators of synthetic data.")
        rpt.row("  Multiple empirical characteristics (e.g. uniform distributions, round price caps,")
        rpt.row("  zero missing values, deterministic age formula) are consistent with")
        rpt.row("  synthetic dataset generation rather than authentic market transactions.")
        rpt.row("  However, synthetic provenance cannot be claimed as confirmed unless established")
        rpt.row("  by official source documentation.")
        rpt.row("  Models trained on it may not generalise to real-world property data.")
    elif len(synth_signals) >= 2:
        rpt.row("  ASSESSMENT: Some indicators consistent with synthetic data were found,")
        rpt.row("  but the evidence is not conclusive without official source documentation.")
    else:
        rpt.row("  ASSESSMENT: Few or no strong indicators of synthetic data found.")
        rpt.row("  The dataset may be real or partially real.")

    # Return the signals list so main() can use it
    return {"synth_signals": synth_signals}


# =============================================================================
# INVESTIGATION 5 — TARGET AND IDENTIFIER
# =============================================================================

def investigate_target_and_id(df, rpt, n_floor_inconsistent=None):
    """
    ISSUE: Confirm Price_in_Lakhs as regression target, check ID column,
    and produce a feature-exclusion list with reasons.

    We investigate:
      (a) Is Price_in_Lakhs a good regression target?
      (b) Is ID sequential?  Can it leak information?
      (c) Which columns should be excluded before modelling?
    """
    rpt.h1("INVESTIGATION 5 — Target Variable, ID Column & Feature Exclusion List")

    price = pd.to_numeric(df["Price_in_Lakhs"], errors="coerce")
    ids   = pd.to_numeric(df["ID"],             errors="coerce")

    # ── Target suitability ───────────────────────────────────────────────────
    rpt.h2("(a) Price_in_Lakhs as regression target")
    rpt.blank()
    rpt.row(f"  Non-null values   : {price.notna().sum():,}")
    rpt.row(f"  Min               : Rs {price.min():.2f} Lakhs")
    rpt.row(f"  Max               : Rs {price.max():.2f} Lakhs")
    rpt.row(f"  Mean              : Rs {price.mean():.2f} Lakhs")
    rpt.row(f"  Median            : Rs {price.median():.2f} Lakhs")
    rpt.row(f"  Std deviation     : Rs {price.std():.2f} Lakhs")
    skew = price.skew()
    rpt.row(f"  Skewness          : {skew:.4f}")
    rpt.blank()
    rpt.row("  Skewness interpretation:")
    if abs(skew) < 0.5:
        rpt.row("    Near-symmetric distribution — good for linear models as-is.")
    elif abs(skew) < 1.0:
        rpt.row("    Moderate skew — consider log-transforming Price_in_Lakhs")
        rpt.row("    before training to help linear models.")
    else:
        rpt.row("    Strong skew — log-transform is strongly recommended.")
    rpt.blank()
    rpt.row("  SUITABILITY: Price_in_Lakhs is appropriate as the regression")
    rpt.row("  target.  It is continuous, numeric, and represents a real-world")
    rpt.row("  quantity we want to predict.")

    # ── ID column ────────────────────────────────────────────────────────────
    rpt.h2("(b) Is the ID column sequential?")
    rpt.blank()
    expected_ids = pd.Series(range(1, len(df) + 1))
    is_sequential = ids.reset_index(drop=True).equals(
        expected_ids.astype(float)
    )
    rpt.row(f"  ID range   : {ids.min():.0f} to {ids.max():.0f}")
    rpt.row(f"  Row count  : {len(df):,}")
    rpt.row(f"  Sequential : {is_sequential}")
    rpt.row(f"  Gaps       : {len(df) - ids.nunique()} (expected 0 if perfectly sequential)")
    rpt.blank()
    rpt.row("  A sequential integer ID carries zero information about the property.")
    rpt.row("  It must be excluded from model features (it is just a row number).")
    rpt.row("  However, keep it in the DataFrame for traceability and debugging.")

    # ── Feature exclusion list ───────────────────────────────────────────────
    rpt.h2("(c) Provisional feature-exclusion list")
    rpt.blank()
    rpt.row("  The following columns should be EXCLUDED from ML features at this stage.")
    rpt.row("  Decisions may be revised after data-cleaning and domain review.")
    rpt.blank()

    floor_reason = (
        f"{n_floor_inconsistent:,} rows have Floor_No > Total_Floors. Column may be mislabelled."
        if n_floor_inconsistent is not None else
        "Many rows have Floor_No > Total_Floors. Column may be mislabelled."
    )

    exclusions = [
        ("ID",
         "EXCLUDE",
         "Sequential row number — no predictive information about price."),
        ("Price_per_SqFt",
         "EXCLUDE",
         "Derived from the target (Price_in_Lakhs). Using it causes data leakage."),
        ("Age_of_Property",
         "EXCLUDE (if Year_Built is kept)",
         "Perfectly redundant: Age = 2025 - Year_Built. Keep Year_Built instead."),
        ("Floor_No",
         "HOLD — investigate further",
         floor_reason),
        ("Total_Floors",
         "HOLD — investigate further",
         "Same mislabelling issue as Floor_No. Review with data owner first."),
        ("Locality",
         "USE WITH CAUTION",
         "Generic codes ('Locality_84'), not real place names. Low predictive value "
         "without real geo data.  Consider grouping by City instead."),
    ]

    rpt.row(f"  {'Column':<32} {'Decision':<32} Reason")
    rpt.row("  " + "-" * 100)
    for col, decision, reason in exclusions:
        rpt.row(f"  {col:<32} {decision:<32} {reason}")

    rpt.blank()
    rpt.h2("(d) Columns provisionally retained as features")
    rpt.blank()
    retained = [
        ("City",                   "Location signal; key driver of price."),
        ("State",                  "Broader location context."),
        ("Property_Type",          "Apartment vs villa affects price."),
        ("BHK",                    "Size proxy; strong predictor."),
        ("Size_in_SqFt",           "Direct area measurement; strong predictor."),
        ("Year_Built",             "Captures property age without the 2025-dependency issue."),
        ("Furnished_Status",       "Furnishing affects price; will need encoding."),
        ("Nearby_Schools",         "Amenity score; investigate uniform distribution."),
        ("Nearby_Hospitals",       "Amenity score; investigate uniform distribution."),
        ("Public_Transport_Accessibility", "Accessibility rating."),
        ("Parking_Space",          "Binary feature."),
        ("Security",               "Binary feature."),
        ("Amenities",              "Text list; may need parsing or encoding."),
        ("Facing",                 "Directional feature; cultural value in India."),
        ("Owner_Type",             "Owner vs builder; affects negotiation."),
        ("Availability_Status",    "Ready vs under-construction affects price."),
    ]
    rpt.row(f"  {'Column':<36} Reason to retain")
    rpt.row("  " + "-" * 80)
    for col, reason in retained:
        rpt.row(f"  {col:<36} {reason}")

    # Return computed values for the dynamic summary
    n_gaps = len(df) - ids.nunique()
    return {
        "price_skew"    : float(price.skew()) if price.notna().any() else float("nan"),
        "id_sequential" : bool(is_sequential),
        "id_gaps"       : int(n_gaps),
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("\n" + "=" * 72)
    print("  Smart Estate AI -- Investigation Script")
    print("=" * 72)

    df = load_csv(CSV_PATH)

    rpt = ReportWriter()
    rpt.h1("Smart Estate AI -- Data Investigation Report")
    rpt.row(f"  Dataset  : {os.path.abspath(CSV_PATH)}")
    rpt.row(f"  Rows     : {df.shape[0]:,}")
    rpt.row(f"  Columns  : {df.shape[1]}")
    rpt.row("  This script is READ-ONLY -- the CSV has NOT been modified.")

    # ── Run every investigation and collect results for the dynamic summary ──
    floor_results   = investigate_floors(df,         rpt)
    investigate_price_per_sqft(df,                   rpt)
    age_results     = investigate_age_year(df,         rpt)
    realism_results = investigate_realism(df,        rpt)
    target_results  = investigate_target_and_id(df, rpt, n_floor_inconsistent=floor_results.get("n_orig_bad"))

    # ── Build the summary DYNAMICALLY from computed values ──────────────────
    rpt.h1("INVESTIGATION COMPLETE — Key Findings Summary")
    rpt.blank()

    # Finding 1: floors
    if floor_results.get("n_orig_bad") is not None:
        n_bad          = floor_results["n_orig_bad"]
        pct_bad        = floor_results["pct_orig_bad"]
        n_swap_bad     = floor_results["n_swap_violating"]
        pct_swap_bad   = floor_results["pct_swap_violating"]
        n_swap_valid   = floor_results["n_swap_valid"]
        pct_swap_valid = floor_results["pct_swap_valid"]

        if n_bad == 0:
            f1 = "Floor_No and Total_Floors are consistent in all rows — no issue."
        elif floor_results.get("swap_fixes_whole_dataset"):
            f1 = (f"Floor_No > Total_Floors in {n_bad:,} rows ({pct_bad:.1f}%). "
                  f"A hypothetical column swap resolves all inconsistencies dataset-wide with 0 violations remaining. "
                  "This strongly indicates reversed column labels; verify with data source.")
        else:
            f1 = (f"Original rows where Floor_No > Total_Floors: {n_bad:,} ({pct_bad:.1f}%). "
                  f"A hypothetical swap resolves all {n_bad:,} original inconsistencies (100.0%), "
                  f"but if applied as a column swap across the dataset, {n_swap_bad:,} originally valid rows "
                  f"({pct_swap_bad:.1f}%) violate Floor_No <= Total_Floors, leaving only {n_swap_valid:,} "
                  f"valid rows ({pct_swap_valid:.1f}%). Therefore, swapping columns does not resolve inconsistencies "
                  "dataset-wide; the issue cannot be explained by a simple column-header reversal.")
    else:
        f1 = "Floor column check could not run (columns missing)."

    rpt.row(f"  1. {f1}")
    rpt.blank()

    # Finding 2: Price_per_SqFt
    price = pd.to_numeric(df.get("Price_in_Lakhs", pd.Series(dtype=float)), errors="coerce")
    size  = pd.to_numeric(df.get("Size_in_SqFt",   pd.Series(dtype=float)), errors="coerce")
    pps   = pd.to_numeric(df.get("Price_per_SqFt", pd.Series(dtype=float)), errors="coerce")
    if pps.notna().any():
        stored_max = pps.max()
        valid_mask = price.notna() & size.notna() & (size > 0) & (price > 0)
        if valid_mask.any():
            computed   = (price[valid_mask] * 100_000) / size[valid_mask]
            comp_med   = computed.median()
            f2 = (f"Price_per_SqFt is stored in the range "
                  f"{pps.min():.4f}–{stored_max:.4f} (unknown scale). "
                  f"The correct formula gives a median of "
                  f"Rs {comp_med:,.0f}/sq-ft, confirming the stored column "
                  "is on a different scale. It directly encodes the target "
                  "(data leakage) and must be excluded from ML features.")
        else:
            f2 = "Price_per_SqFt check could not compute recomputed values."
    else:
        f2 = "Price_per_SqFt column not found or entirely null."

    rpt.row(f"  2. {f2}")
    rpt.blank()

    # Finding 3: Age vs Year
    age_col  = pd.to_numeric(df.get("Age_of_Property", pd.Series(dtype=float)), errors="coerce")
    year_col = pd.to_numeric(df.get("Year_Built",       pd.Series(dtype=float)), errors="coerce")
    valid_ay = age_col.notna() & year_col.notna()
    if valid_ay.any():
        implied   = year_col[valid_ay] + age_col[valid_ay]
        n_unique  = implied.nunique()
        ref_year  = int(implied.median())
        spread    = int(implied.max() - implied.min())
        if n_unique == 1:
            f3 = (f"Year_Built + Age_of_Property = {ref_year} for every row "
                  f"(spread = 0). Age_of_Property is entirely derived from "
                  f"Year_Built and is redundant. Keep only one.")
        else:
            f3 = (f"Year_Built + Age_of_Property is NOT perfectly constant "
                  f"(spread = {spread} years, {n_unique} unique values). "
                  "The two columns are closely but not perfectly related.")
    else:
        f3 = "Age_of_Property or Year_Built columns missing or all null."

    rpt.row(f"  3. {f3}")
    rpt.blank()

    # Finding 4: Realism — evidence-based language, never 'confirmed' without documentation
    synth_signals = realism_results.get("synth_signals", []) if realism_results else []
    n_signals = len(synth_signals)
    if n_signals == 0:
        f4 = "No strong indicators of synthetic data were found."
    else:
        joined = "; ".join(synth_signals)
        f4 = (f"There are strong indicators of synthetic data ({n_signals} observed: {joined}). "
              "Synthetic provenance should not be claimed as confirmed unless source documentation "
              "establishes it, but these empirical findings strongly suggest algorithmic generation, "
              "which may limit generalization to real-world housing markets.")

    rpt.row(f"  4. {f4}")
    rpt.blank()

    # Finding 5: Target and ID
    if target_results:
        skew_val   = target_results.get("price_skew", float("nan"))
        is_seq     = target_results.get("id_sequential", None)
        id_gaps    = target_results.get("id_gaps", None)
        f5_parts   = []
        if not np.isnan(skew_val):
            f5_parts.append(
                f"Price_in_Lakhs has skewness {skew_val:.4f} "
                f"({'near-symmetric' if abs(skew_val) < 0.5 else 'skewed'}) "
                "and is suitable as the regression target."
            )
        if is_seq is not None:
            seq_txt = "is perfectly sequential" if is_seq else "is NOT perfectly sequential"
            gap_txt = f" with {id_gaps} gaps" if id_gaps else ""
            f5_parts.append(
                f"The ID column {seq_txt}{gap_txt} and carries "
                "no property information — exclude from features."
            )
        f5 = " ".join(f5_parts) if f5_parts else "Target/ID check did not return results."
    else:
        f5 = "Target/ID investigation did not return results."

    rpt.row(f"  5. {f5}")
    rpt.blank()

    rpt.row("  Next step: STOP. Review this report and the detailed sections above.")
    rpt.row("  Do NOT proceed to data cleaning until you have reviewed these findings.")
    rpt.row("")
    rpt.row("  Output written to: reports/data_investigation.txt")

    rpt.save(REPORT_PATH)


if __name__ == "__main__":
    main()
