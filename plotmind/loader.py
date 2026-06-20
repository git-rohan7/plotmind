"""
loader.py – Reads CSV files and validates their structure.
"""

import os
import pandas as pd


def load_csv(filepath: str, **kwargs) -> pd.DataFrame:
    """
    Load a CSV file and return a pandas DataFrame.

    Args:
        filepath: Path to the CSV file.
        **kwargs: Additional arguments passed to pd.read_csv().

    Returns:
        A pandas DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty or not a valid CSV.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if not filepath.lower().endswith(".csv"):
        raise ValueError(f"Expected a .csv file, got: {filepath}")

    try:
        df = pd.read_csv(filepath, **kwargs)
    except pd.errors.EmptyDataError:
        raise ValueError(f"The file is empty: {filepath}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Could not parse CSV file: {e}")

    if df.empty:
        raise ValueError("The CSV file contains no data rows.")

    if len(df.columns) == 0:
        raise ValueError("The CSV file has no columns.")

    return df
