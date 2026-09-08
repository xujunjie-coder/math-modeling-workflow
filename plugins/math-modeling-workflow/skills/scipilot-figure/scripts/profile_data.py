"""
scipilot-figure: Data Profiling Module (Think First, Plot Second)
Inspects distributions, sample sizes, skewness, missing values, and outliers before plotting.
"""

import pandas as pd
import numpy as np
import sys

def profile_data(df, target_cols=None):
    """
    Profile dataframe characteristics for scientific figure design.
    """
    if isinstance(df, str):
        df = pd.read_csv(df)
        
    print("=" * 65)
    print(" [SciPilot Figure] Data Profiling & Pre-plotting Audit Report")
    print("=" * 65)
    print(f"Total Rows: {len(df)}, Total Columns: {df.shape[1]}")
    
    cols = target_cols if target_cols else df.columns
    
    for col in cols:
        if col not in df.columns:
            continue
        series = df[col]
        dtype = series.dtype
        n_missing = series.isna().sum()
        n_unique = series.nunique()
        
        print(f"\n--- Feature: [{col}] (dtype: {dtype}) ---")
        print(f"  Missing: {n_missing} ({n_missing / len(df) * 100:.1f}%), Unique: {n_unique}")
        
        if np.issubdtype(dtype, np.number):
            valid_vals = series.dropna()
            mean = valid_vals.mean()
            std = valid_vals.std()
            median = valid_vals.median()
            q25, q75 = valid_vals.quantile(0.25), valid_vals.quantile(0.75)
            skew = valid_vals.skew()
            min_val, max_val = valid_vals.min(), valid_vals.max()
            
            print(f"  Range: [{min_val:.4g}, {max_val:.4g}], Mean: {mean:.4g} ± {std:.4g}, Median: {median:.4g} (IQR: [{q25:.4g}, {q75:.4g}])")
            print(f"  Skewness: {skew:.2f} ({'Symmetric' if abs(skew) < 0.5 else 'Moderately Skewed' if abs(skew) < 1.0 else 'Highly Skewed'})")
            
            # Recommendation
            if len(valid_vals) < 20:
                print("  [ALERT] Sample size n < 20! Prohibit plain bar charts; MUST overlay jittered scatter or raincloud points.")
            if abs(skew) > 1.5:
                print("  [RECOMMENDATION] High skewness! Consider log-transformation or violin/box representation instead of mean-std.")
        else:
            top_cats = series.value_counts().head(5).to_dict()
            print(f"  Top categories: {top_cats}")
            
    print("=" * 65)
    print(" Data profiling completed. Proceed with chart selection.")
    print("=" * 65)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        profile_data(sys.argv[1])
    else:
        # Example on catalyst_clean.csv
        sample_path = "workspace/data_clean/catalyst_clean.csv"
        try:
            profile_data(sample_path, target_cols=['temperature', 'ethanol_conversion', 'c4_selectivity', 'c4_yield'])
        except Exception as e:
            print(f"Run profile_data(df) in your script.")
