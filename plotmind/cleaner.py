"""
cleaner.py – Handles missing values, duplicates, and data type fixes.
"""

import pandas as pd


def clean_dataframe(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """
    Clean a DataFrame by handling missing values, duplicates, and data types.

    Args:
        df: Input DataFrame.
        verbose: If True, prints a cleaning summary.

    Returns:
        A cleaned copy of the DataFrame.
    """
    df = df.copy()
    report = {}

    # --- Remove duplicate rows ---
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = before - len(df)

    # --- Fix data types: try numeric coercion on object columns ---
    for col in df.select_dtypes(include=["object", "string"]).columns:
        # Try parsing as datetime first
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True)
            if parsed.notna().sum() > len(df) * 0.5:
                df[col] = parsed
                continue
        except Exception:
            pass

        # Try parsing as numeric
        coerced = pd.to_numeric(df[col], errors="coerce")
        if coerced.notna().sum() > len(df) * 0.5:
            df[col] = coerced
            continue

    # --- Handle missing values ---
    missing_before = df.isnull().sum().sum()

    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].fillna(method="ffill").fillna(method="bfill")
        else:
            mode = df[col].mode()
            fill_val = mode[0] if not mode.empty else "Unknown"
            df[col] = df[col].fillna(fill_val)

    report["missing_filled"] = missing_before

    if verbose:
        print("[PlotMind Cleaner]")
        print(f"  Duplicates removed : {report['duplicates_removed']}")
        print(f"  Missing values filled : {report['missing_filled']}")
        print(f"  Final shape : {df.shape}")

    return df
