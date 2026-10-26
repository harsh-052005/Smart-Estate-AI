"""
=============================================================
 Smart Estate AI — Phase 3: Data Preparation (Bengaluru Real Estate)
 File  : scripts/prepare_data.py
 Stage : 3 — Feature Engineering, Quality Filtering, Train/Test Split,
             and Scikit-Learn Pipelines
 Run   : python3 scripts/prepare_data.py
=============================================================
"""

import os
import sys
import re
import json
import time

try:
    import pandas as pd
    import numpy as np
except ImportError:
    sys.exit("\n[ERROR] pandas or numpy not installed. Run: python3 -m pip install pandas numpy\n")

try:
    from sklearn.model_selection import train_test_split
    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    import joblib
except ImportError:
    sys.exit("\n[ERROR] scikit-learn or joblib not installed.\n")


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH     = os.path.join(PROJECT_ROOT, "bengaluru_house_prices.csv")
CLEAN_CSV    = os.path.join(PROJECT_ROOT, "data", "bengaluru_cleaned.csv")
REPORTS_DIR  = os.path.join(PROJECT_ROOT, "reports")
REPORT_PATH  = os.path.join(REPORTS_DIR, "Phase_1_Data_Preparation_and_Cleaning.txt")
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")

TARGET_COL = "price"

NUMERICAL_FEATURES = [
    "total_sqft",
    "bhk",
    "bath",
    "balcony",
]

CATEGORICAL_FEATURES = [
    "location",
    "area_type",
    "availability",
]

RETAINED_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


# =============================================================================
# DATA CLEANING UTILITIES
# =============================================================================

def parse_sqft(val):
    if pd.isnull(val):
        return None
    val_str = str(val).strip()
    if '-' in val_str:
        parts = val_str.split('-')
        try:
            return (float(parts[0].strip()) + float(parts[1].strip())) / 2.0
        except:
            return None
    try:
        return float(val_str)
    except:
        pass
    val_lower = val_str.lower()
    num = re.findall(r'[\d.]+', val_str)
    if not num:
        return None
    try:
        n = float(num[0])
    except:
        return None
    if 'sq. meter' in val_lower or 'sqm' in val_lower:
        return n * 10.7639
    elif 'sq. yard' in val_lower or 'sq yards' in val_lower:
        return n * 9.0
    elif 'acres' in val_lower or 'acre' in val_lower:
        return n * 43560.0
    elif 'cents' in val_lower or 'cent' in val_lower:
        return n * 435.56
    elif 'guntha' in val_lower:
        return n * 1089.0
    elif 'perch' in val_lower:
        return n * 272.25
    return n


def parse_bhk(val):
    if pd.isnull(val):
        return None
    matches = re.findall(r'\d+', str(val))
    return int(matches[0]) if matches else None


def clean_bengaluru_raw(df_raw):
    """
    Cleans raw Bengaluru dataset:
    - Parses total_sqft into numerical square feet.
    - Extracts BHK integer from size text.
    - Imputes bath with BHK and balcony with median.
    - Standardizes availability into 'Ready To Move' vs 'Under Construction'.
    - Removes physical anomalies: total_sqft / BHK >= 300 sq.ft., bath <= BHK + 2.
    - Removes unrealistic price per sqft outliers (< 1500 or > 35000 INR/sqft).
    - Clusters long-tail locations (< 10 occurrences) into 'Other'.
    """
    df = df_raw.copy()
    
    # 1. Location standardizing
    df['location'] = df['location'].apply(lambda x: str(x).strip() if pd.notnull(x) else 'Other')
    
    # 2. Parse sqft and bhk
    df['total_sqft'] = df['total_sqft'].apply(parse_sqft)
    df['bhk'] = df['size'].apply(parse_bhk)
    
    # 3. Clean target and drop invalid essentials
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['total_sqft', 'bhk', 'price'])
    
    # 4. Impute bath & balcony
    df['bath'] = df['bath'].fillna(df['bhk'])
    df['balcony'] = df['balcony'].fillna(1.0)
    
    # 5. Sanity thresholds
    df = df[df['total_sqft'] / df['bhk'] >= 300]
    df = df[df['bath'] <= df['bhk'] + 2]
    
    # 6. Price per sqft filter
    df['price_per_sqft'] = (df['price'] * 100000) / df['total_sqft']
    df = df[(df['price_per_sqft'] >= 1500) & (df['price_per_sqft'] <= 35000)]
    
    # 7. Availability simplify
    df['availability'] = df['availability'].apply(
        lambda x: 'Ready To Move' if str(x).strip() == 'Ready To Move' else 'Under Construction'
    )
    
    # 8. Location grouping
    loc_counts = df['location'].value_counts()
    df['location'] = df['location'].apply(lambda x: x if loc_counts[x] >= 10 else 'Other')
    
    # Clean area_type
    df['area_type'] = df['area_type'].apply(lambda x: str(x).strip() if pd.notnull(x) else 'Super built-up  Area')
    
    df = df.reset_index(drop=True)
    return df


# =============================================================================
# PREPROCESSORS & PIPELINE
# =============================================================================

def build_preprocessors(num_cols, cat_cols):
    """
    Build scikit-learn ColumnTransformers:
      1. linear_preprocessor: Standard scaling on numeric features + one-hot encoding on categoricals.
      2. tree_preprocessor: Passthrough on numeric features + one-hot encoding on categoricals.
    """
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

    linear_transformer = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", ohe, cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    try:
        ohe_tree = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        ohe_tree = OneHotEncoder(handle_unknown="ignore", sparse=False)

    tree_transformer = ColumnTransformer(
        transformers=[
            ("num", "passthrough", num_cols),
            ("cat", ohe_tree, cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )

    return linear_transformer, tree_transformer


def load_prepared_data(data_dir=DATA_DIR, csv_path=CSV_PATH):
    """
    Convenience loader for model training, evaluation, and explainability:
    Loads Bengaluru real estate data and applies the verified split indices and fitted transformers.
    """
    if os.path.exists(CLEAN_CSV):
        df = pd.read_csv(CLEAN_CSV)
    else:
        raw_df = pd.read_csv(csv_path)
        df = clean_bengaluru_raw(raw_df)
        os.makedirs(data_dir, exist_ok=True)
        df.to_csv(CLEAN_CSV, index=False)

    X = df[RETAINED_FEATURES].copy()
    y = df[TARGET_COL].copy()

    split_indices_path = os.path.join(data_dir, "split_indices.npz")
    if os.path.exists(split_indices_path):
        data = np.load(split_indices_path)
        train_idx = data["train_indices"]
        test_idx = data["test_indices"]
        X_train, y_train = X.iloc[train_idx].copy(), y.iloc[train_idx].copy()
        X_test, y_test = X.iloc[test_idx].copy(), y.iloc[test_idx].copy()
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    linear_prep_path = os.path.join(data_dir, "preprocessor_linear.joblib")
    tree_prep_path = os.path.join(data_dir, "preprocessor_tree.joblib")

    if os.path.exists(linear_prep_path) and os.path.exists(tree_prep_path):
        linear_prep = joblib.load(linear_prep_path)
        tree_prep = joblib.load(tree_prep_path)
    else:
        linear_prep, tree_prep = build_preprocessors(NUMERICAL_FEATURES, CATEGORICAL_FEATURES)
        linear_prep.fit(X_train)
        tree_prep.fit(X_train)

    return X_train, X_test, y_train, y_test, linear_prep, tree_prep


def main():
    print("\n=======================================================")
    print(" Smart Estate AI — Preparing Bengaluru Real Estate Data")
    print("=======================================================\n")
    t0 = time.time()
    
    if not os.path.exists(CSV_PATH):
        sys.exit(f"[ERROR] Source file not found: {CSV_PATH}")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print(f"[*] Loading raw dataset from: {CSV_PATH}")
    raw_df = pd.read_csv(CSV_PATH)
    print(f"    Raw records: {len(raw_df):,} | Columns: {len(raw_df.columns)}")

    print("[*] Applying domain cleaning and outlier filtering...")
    df = clean_bengaluru_raw(raw_df)
    print(f"    Cleaned records: {len(df):,} | Validated columns: {len(df.columns)}")
    
    # Save cleaned csv
    df.to_csv(CLEAN_CSV, index=False)
    print(f"    Saved cleaned dataset -> {CLEAN_CSV}")

    X = df[RETAINED_FEATURES].copy()
    y = df[TARGET_COL].copy()

    # Train / Test split
    print("[*] Performing 80/20 train/test split (random_state=42)...")
    indices = np.arange(len(df))
    train_idx, test_idx = train_test_split(indices, test_size=0.2, random_state=42)

    X_train, y_train = X.iloc[train_idx].copy(), y.iloc[train_idx].copy()
    X_test, y_test = X.iloc[test_idx].copy(), y.iloc[test_idx].copy()

    print(f"    Train partition: {len(X_train):,} rows ({len(X_train)/len(df)*100:.1f}%)")
    print(f"    Test partition : {len(X_test):,} rows ({len(X_test)/len(df)*100:.1f}%)")

    # Save split indices
    split_indices_path = os.path.join(DATA_DIR, "split_indices.npz")
    np.savez_compressed(
        split_indices_path,
        train_indices=train_idx,
        test_indices=test_idx
    )
    print(f"    Saved split indices -> {split_indices_path}")

    # Build and fit transformers
    print("[*] Building scikit-learn preprocessing pipelines...")
    linear_prep, tree_prep = build_preprocessors(NUMERICAL_FEATURES, CATEGORICAL_FEATURES)

    linear_prep.fit(X_train)
    tree_prep.fit(X_train)

    linear_prep_path = os.path.join(DATA_DIR, "preprocessor_linear.joblib")
    tree_prep_path = os.path.join(DATA_DIR, "preprocessor_tree.joblib")

    joblib.dump(linear_prep, linear_prep_path)
    joblib.dump(tree_prep, tree_prep_path)
    print(f"    Saved linear preprocessor -> {linear_prep_path}")
    print(f"    Saved tree preprocessor   -> {tree_prep_path}")

    # Inspect transformed dimensionality
    X_train_trans = tree_prep.transform(X_train)
    feature_names = tree_prep.get_feature_names_out()
    print(f"    Transformed feature space: {X_train_trans.shape[1]} features (from {len(RETAINED_FEATURES)} raw features)")

    # Write report
    with open(REPORT_PATH, "w") as f:
        f.write("SMART ESTATE AI — DATA PREPARATION REPORT (BENGALURU HOUSING)\n")
        f.write("=============================================================\n\n")
        f.write(f"Source Dataset: {CSV_PATH}\n")
        f.write(f"Raw Rows: {len(raw_df):,}\n")
        f.write(f"Cleaned Rows: {len(df):,}\n")
        f.write(f"Train Rows: {len(X_train):,}\n")
        f.write(f"Test Rows: {len(X_test):,}\n")
        f.write(f"Target: {TARGET_COL} (in Indian Lakhs)\n")
        f.write(f"Retained Input Features: {', '.join(RETAINED_FEATURES)}\n")
        f.write(f"Transformed Model Features: {len(feature_names)}\n\n")
        f.write("Target Statistics (Cleaned):\n")
        f.write(f"  Min: ₹ {y.min():.2f} Lakhs\n")
        f.write(f"  Mean: ₹ {y.mean():.2f} Lakhs\n")
        f.write(f"  Median: ₹ {y.median():.2f} Lakhs\n")
        f.write(f"  Max: ₹ {y.max():.2f} Lakhs\n")
        f.write(f"  Std: ₹ {y.std():.2f} Lakhs\n\n")
        f.write("Feature Correlations with Target (Price):\n")
        for num_c in NUMERICAL_FEATURES:
            r = df[num_c].corr(df[TARGET_COL])
            f.write(f"  - {num_c}: r = {r:+.4f}\n")

    print(f"    Saved data preparation report -> {REPORT_PATH}")
    print(f"\n[DONE] Preparation completed in {time.time() - t0:.2f}s\n")


if __name__ == "__main__":
    main()
