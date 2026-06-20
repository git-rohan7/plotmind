"""
detector.py – Detects column types: numerical, categorical, datetime, boolean.
"""

from typing import Dict
import pandas as pd


COLUMN_TYPES = ["numerical", "categorical", "datetime", "boolean", "unknown"]


def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect the semantic type of each column in a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        A dict mapping column name -> type string.
        Type is one of: 'numerical', 'categorical', 'datetime', 'boolean', 'unknown'
    """
    col_types: Dict[str, str] = {}

    for col in df.columns:
        series = df[col]
        dtype = series.dtype

        # Boolean
        if dtype == bool or set(series.dropna().unique()).issubset({0, 1, True, False, "True", "False", "true", "false", "yes", "no", "Yes", "No"}):
            col_types[col] = "boolean"

        # Datetime
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_types[col] = "datetime"

        # Numerical
        elif pd.api.types.is_numeric_dtype(series):
            col_types[col] = "numerical"

        # Categorical (object / string with low cardinality) or pandas Categorical dtype
        elif (
            pd.api.types.is_object_dtype(series)
            or isinstance(series.dtype, pd.CategoricalDtype)
            or pd.api.types.is_string_dtype(series)
        ):
            n_unique = series.nunique()
            n_total = max(len(series), 1)
            unique_ratio = n_unique / n_total
            # Treat as categorical when few unique values OR cardinality is low relative to size
            if n_unique <= 50 or unique_ratio < 0.5:
                col_types[col] = "categorical"
            else:
                col_types[col] = "unknown"

        else:
            col_types[col] = "unknown"

    return col_types


def summarize_columns(df: pd.DataFrame) -> None:
    """Print a human-readable summary of detected column types."""
    col_types = detect_columns(df)
    print("[PlotMind Detector] Column Types:")
    for col, ctype in col_types.items():
        print(f"  {col:<30} → {ctype}")
