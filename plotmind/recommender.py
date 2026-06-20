"""
recommender.py – Recommends the best chart type based on column type analysis.
"""

from typing import Dict, Tuple, Optional
import pandas as pd

from .detector import detect_columns

CHART_TYPES = ["histogram", "bar", "scatter", "line", "pie", "heatmap", "box"]


def recommend_chart(
    df: pd.DataFrame,
    x: Optional[str] = None,
    y: Optional[str] = None,
) -> Tuple[str, str, str]:
    """
    Recommend the best chart type for the given DataFrame.

    Args:
        df: Input DataFrame.
        x: Optional column to use as the x-axis.
        y: Optional column to use as the y-axis.

    Returns:
        A tuple of (chart_type, x_col, y_col) where chart_type is one of the
        CHART_TYPES strings. x_col / y_col may be None for single-variable charts.
    """
    col_types = detect_columns(df)

    numerical_cols = [c for c, t in col_types.items() if t == "numerical"]
    categorical_cols = [c for c, t in col_types.items() if t == "categorical"]
    datetime_cols = [c for c, t in col_types.items() if t == "datetime"]
    boolean_cols = [c for c, t in col_types.items() if t == "boolean"]

    # --- If specific x/y provided, use them ---
    if x and y:
        xt = col_types.get(x, "unknown")
        yt = col_types.get(y, "unknown")

        if xt == "datetime" and yt == "numerical":
            return "line", x, y
        if xt == "categorical" and yt == "numerical":
            return "bar", x, y
        if xt == "numerical" and yt == "numerical":
            return "scatter", x, y
        if xt == "categorical" and yt == "categorical":
            return "heatmap", x, y
        return "bar", x, y

    if x and not y:
        xt = col_types.get(x, "unknown")
        if xt == "numerical":
            return "histogram", x, None
        if xt == "categorical":
            return "bar", x, None
        return "bar", x, None

    # --- Auto-select best chart ---

    # Time series: datetime + numerical
    if datetime_cols and numerical_cols:
        return "line", datetime_cols[0], numerical_cols[0]

    # Two numerical columns → scatter
    if len(numerical_cols) >= 2:
        return "scatter", numerical_cols[0], numerical_cols[1]

    # Categorical + numerical → bar
    if categorical_cols and numerical_cols:
        cat = categorical_cols[0]
        # If few unique values → pie, else bar
        if df[cat].nunique() <= 6:
            return "pie", cat, numerical_cols[0]
        return "bar", cat, numerical_cols[0]

    # Only one numerical → histogram
    if len(numerical_cols) == 1:
        return "histogram", numerical_cols[0], None

    # Multiple numerical columns → heatmap (correlation)
    if len(numerical_cols) > 2:
        return "heatmap", None, None

    # Boolean + numerical → bar
    if boolean_cols and numerical_cols:
        return "bar", boolean_cols[0], numerical_cols[0]

    # Fallback: bar on first two columns
    cols = list(df.columns)
    if len(cols) >= 2:
        return "bar", cols[0], cols[1]
    return "histogram", cols[0], None


def explain_recommendation(df: pd.DataFrame) -> None:
    """Print a human-readable explanation of the chart recommendation."""
    chart, x, y = recommend_chart(df)
    col_types = detect_columns(df)
    print(f"[PlotMind Recommender]")
    print(f"  Recommended chart : {chart.upper()}")
    if x:
        print(f"  X axis            : {x}  ({col_types.get(x, 'unknown')})")
    if y:
        print(f"  Y axis            : {y}  ({col_types.get(y, 'unknown')})")
