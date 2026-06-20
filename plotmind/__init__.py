"""
PlotMind – Convert any CSV into meaningful graphs automatically.
"""

from .loader import load_csv
from .cleaner import clean_dataframe
from .detector import detect_columns
from .recommender import recommend_chart
from .plotter import plot
from .exporter import export

__version__ = "0.1.0"
__all__ = ["load_csv", "clean_dataframe", "detect_columns", "recommend_chart", "plot", "export"]
