"""
utils.py – Utility helpers for PlotMind.
"""

from typing import List, Optional
import pandas as pd


def preview(df: pd.DataFrame, n: int = 5) -> None:
    """Print a quick preview of the DataFrame."""
    print(f"[PlotMind] DataFrame Preview  ({df.shape[0]} rows × {df.shape[1]} cols)")
    print(df.head(n).to_string())
    print()


def column_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        series = df[col]
        null_count = series.isnull().sum()
        rows.append({
            "column": col,
            "dtype": str(series.dtype),
            "null_count": null_count,
            "null_pct": round(null_count / max(len(series), 1) * 100, 1),
            "unique": series.nunique(),
            "sample_values": str(series.dropna().unique()[:3].tolist()),
        })
    return pd.DataFrame(rows).set_index("column")


def filter_columns(df: pd.DataFrame, types: Optional[List[str]] = None) -> List[str]:

    if types is None:
        return list(df.columns)

    result = []
    for t in types:
        result.extend(df.select_dtypes(include=[t]).columns.tolist())
    return list(dict.fromkeys(result))  # deduplicate while preserving order
