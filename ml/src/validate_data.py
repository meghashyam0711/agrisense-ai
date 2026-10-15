"""
AgriSense-AI: Data Validation and Pipeline Execution Script.
Executes the data generation, validation, and preprocessing pipeline,
and prints structured statistical audits.
"""

import os
import sys
import pandas as pd

from .dataset_schema import FEATURE_BOUNDS
from .generate_dataset import generate_synthetic_paddy_dataset
from .preprocessing import PaddyDataPreprocessor

def run_dataset_pipeline(
    raw_path: str = "ml/data/raw/synthetic_paddy_yield_tn.csv",
    processed_path: str = "ml/data/processed/paddy_yield_processed.csv"
):
    print("=" * 70)
    print("AGRISENSE-AI: AGRICULTURAL DATASET VALIDATION & PIPELINE")
    print("=" * 70)
    
    # 1. Generate or verify raw dataset
    if not os.path.exists(raw_path):
        print(f"[*] Raw dataset not found at {raw_path}. Generating synthetic dataset...")
        raw_df = generate_synthetic_paddy_dataset(n_samples=2000, inject_dirty_samples=True, output_path=raw_path)
    else:
        print(f"[+] Found raw dataset at: {raw_path}")
        raw_df = pd.read_csv(raw_path)
        
    print(f"[+] Loaded raw dataset: {raw_df.shape[0]} rows, {raw_df.shape[1]} columns")

    # 2. Raw Data Validation
    preprocessor = PaddyDataPreprocessor()
    raw_validation = preprocessor.validate_schema(raw_df)
    
    print("\n--- Raw Data Validation ---")
    print(f"Schema Valid: {raw_validation['is_valid']}")
    print(f"Total Rows: {raw_validation['total_rows']}")
    print(f"Duplicate Rows Detected: {raw_validation['duplicate_count']}")
    null_summary = {k: v for k, v in raw_validation['null_counts'].items() if v > 0}
    print(f"Columns with Nulls: {null_summary if null_summary else 'None'}")

    # 3. Preprocess Pipeline Execution
    print("\n[*] Executing Preprocessing Pipeline (Cleaning, Imputation, Feature Eng, Encoding)...")
    processed_df = preprocessor.process_pipeline(raw_df, is_train=True)
    
    # 4. Save Processed Dataset
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    processed_df.to_csv(processed_path, index=False)
    print(f"[+] Preprocessed dataset saved to: {processed_path}")
    print(f"[+] Processed shape: {processed_df.shape[0]} rows, {processed_df.shape[1]} features")

    # 5. Processed Validation Checks
    print("\n--- Processed Data Quality Audit ---")
    processed_nulls = processed_df.isnull().sum().sum()
    processed_dups = processed_df.duplicated().sum()
    print(f"Total Remaining Missing Values: {processed_nulls} (Expected: 0)")
    print(f"Total Remaining Duplicate Rows: {processed_dups} (Expected: 0)")
    
    # Verify target variable
    target = processed_df[preprocessor.target_column]
    print(f"\n--- Target Variable Distribution ({preprocessor.target_column}) ---")
    print(f"Min Yield:    {target.min():.2f} tonnes/ha ({(target.min() * 10):.1f} Q/ha)")
    print(f"Mean Yield:   {target.mean():.2f} tonnes/ha ({(target.mean() * 10):.1f} Q/ha)")
    print(f"Median Yield: {target.median():.2f} tonnes/ha ({(target.median() * 10):.1f} Q/ha)")
    print(f"Max Yield:    {target.max():.2f} tonnes/ha ({(target.max() * 10):.1f} Q/ha)")
    print(f"Std Dev:      {target.std():.2f} tonnes/ha")

    # 6. Feature Summary Table
    print("\n--- Core Feature Summary Statistics ---")
    summary = preprocessor.get_summary_statistics(raw_df)
    header = f"{'Feature':<30} | {'Mean':<8} | {'Std':<8} | {'Min':<8} | {'Median':<8} | {'Max':<8}"
    print(header)
    print("-" * len(header))
    for col, stats in summary.items():
        print(f"{col:<30} | {stats['mean']:<8} | {stats['std']:<8} | {stats['min']:<8} | {stats['median']:<8} | {stats['max']:<8}")

    print("\n" + "=" * 70)
    print("[SUCCESS] Phase 3 Dataset Preparation and Preprocessing is Complete!")
    print("=" * 70)

if __name__ == "__main__":
    run_dataset_pipeline()
