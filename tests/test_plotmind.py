"""
tests/test_plotmind.py – Test suite for PlotMind.
"""

import os
import tempfile
import pytest
import pandas as pd

from plotmind.loader import load_csv
from plotmind.cleaner import clean_dataframe
from plotmind.detector import detect_columns
from plotmind.recommender import recommend_chart
from plotmind.utils import column_stats, filter_columns


# ──────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────

@pytest.fixture
def sample_csv(tmp_path):
    """A simple CSV with numerical + categorical columns."""
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "name,age,score,city\n"
        "Alice,30,88.5,NYC\n"
        "Bob,25,72.0,LA\n"
        "Charlie,35,91.0,NYC\n"
        "Dave,28,65.5,Chicago\n"
        "Eve,22,78.0,LA\n"
    )
    return str(csv_path)


@pytest.fixture
def messy_csv(tmp_path):
    """A CSV with missing values and duplicates."""
    csv_path = tmp_path / "messy.csv"
    csv_path.write_text(
        "name,age,score\n"
        "Alice,30,88.5\n"
        "Bob,,72.0\n"
        "Charlie,35,\n"
        "Alice,30,88.5\n"  # duplicate
    )
    return str(csv_path)


@pytest.fixture
def empty_csv(tmp_path):
    """An empty CSV file."""
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("")
    return str(csv_path)


@pytest.fixture
def header_only_csv(tmp_path):
    """A CSV with headers but no data rows."""
    csv_path = tmp_path / "header.csv"
    csv_path.write_text("name,age,score\n")
    return str(csv_path)


# ──────────────────────────────────────────────────────────
# Loader tests
# ──────────────────────────────────────────────────────────

class TestLoader:
    def test_load_valid_csv(self, sample_csv):
        df = load_csv(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == ["name", "age", "score", "city"]

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_csv("/nonexistent/path/data.csv")

    def test_non_csv_extension(self, tmp_path):
        f = tmp_path / "data.txt"
        f.write_text("a,b\n1,2\n")
        with pytest.raises(ValueError, match="Expected a .csv file"):
            load_csv(str(f))

    def test_empty_csv(self, empty_csv):
        with pytest.raises(ValueError):
            load_csv(empty_csv)

    def test_header_only_csv(self, header_only_csv):
        with pytest.raises(ValueError, match="no data rows"):
            load_csv(header_only_csv)


# ──────────────────────────────────────────────────────────
# Cleaner tests
# ──────────────────────────────────────────────────────────

class TestCleaner:
    def test_removes_duplicates(self, messy_csv):
        df = load_csv(messy_csv)
        cleaned = clean_dataframe(df)
        assert len(cleaned) < len(df)

    def test_fills_missing_numerical(self, messy_csv):
        df = load_csv(messy_csv)
        cleaned = clean_dataframe(df)
        assert cleaned["age"].isnull().sum() == 0
        assert cleaned["score"].isnull().sum() == 0

    def test_returns_copy(self):
        df = pd.DataFrame({"a": [1, None, 3]})
        cleaned = clean_dataframe(df)
        assert df["a"].isnull().sum() == 1  # original unchanged
        assert cleaned["a"].isnull().sum() == 0


# ──────────────────────────────────────────────────────────
# Detector tests
# ──────────────────────────────────────────────────────────

class TestDetector:
    def test_detect_numerical(self):
        df = pd.DataFrame({"score": [1.0, 2.0, 3.0]})
        types = detect_columns(df)
        assert types["score"] == "numerical"

    def test_detect_categorical(self):
        df = pd.DataFrame({"city": ["NYC", "LA", "NYC", "Chicago"]})
        types = detect_columns(df)
        assert types["city"] == "categorical"

    def test_detect_datetime(self):
        df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-02-01"])})
        types = detect_columns(df)
        assert types["date"] == "datetime"

    def test_detect_boolean(self):
        df = pd.DataFrame({"flag": [True, False, True]})
        types = detect_columns(df)
        assert types["flag"] == "boolean"

    def test_mixed_dataframe(self, sample_csv):
        df = load_csv(sample_csv)
        types = detect_columns(df)
        assert types["age"] == "numerical"
        assert types["score"] == "numerical"
        assert types["city"] == "categorical"


# ──────────────────────────────────────────────────────────
# Recommender tests
# ──────────────────────────────────────────────────────────

class TestRecommender:
    def test_two_numerical_gives_scatter(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        chart, x, y = recommend_chart(df)
        assert chart == "scatter"

    def test_one_numerical_gives_histogram(self):
        df = pd.DataFrame({"score": [1, 2, 3, 4, 5]})
        chart, x, y = recommend_chart(df)
        assert chart == "histogram"

    def test_categorical_numerical_gives_bar_or_pie(self):
        df = pd.DataFrame({"city": ["NYC", "LA", "NYC"], "sales": [100, 200, 150]})
        chart, x, y = recommend_chart(df)
        assert chart in ("bar", "pie")

    def test_datetime_numerical_gives_line(self):
        df = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
            "value": [10, 20, 30],
        })
        chart, x, y = recommend_chart(df)
        assert chart == "line"

    def test_explicit_chart_override(self):
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        chart, x, y = recommend_chart(df, x="x", y="y")
        assert chart == "scatter"

    def test_explicit_x_only(self):
        df = pd.DataFrame({"score": [1, 2, 3]})
        chart, x, y = recommend_chart(df, x="score")
        assert chart == "histogram"
        assert x == "score"


# ──────────────────────────────────────────────────────────
# Utils tests
# ──────────────────────────────────────────────────────────

class TestUtils:
    def test_column_stats(self, sample_csv):
        df = load_csv(sample_csv)
        stats = column_stats(df)
        assert "null_count" in stats.columns
        assert "unique" in stats.columns
        assert len(stats) == len(df.columns)

    def test_filter_columns_number(self, sample_csv):
        df = load_csv(sample_csv)
        cols = filter_columns(df, types=["number"])
        assert "age" in cols
        assert "score" in cols
        assert "name" not in cols

    def test_filter_columns_none(self, sample_csv):
        df = load_csv(sample_csv)
        cols = filter_columns(df, types=None)
        assert cols == list(df.columns)


# ──────────────────────────────────────────────────────────
# Integration test
# ──────────────────────────────────────────────────────────

class TestIntegration:
    def test_full_pipeline_plotly(self, sample_csv, tmp_path):
        """Load → clean → detect → recommend → plot → export (HTML)."""
        from plotmind.plotter import plot
        from plotmind.exporter import export

        df = load_csv(sample_csv)
        df = clean_dataframe(df)
        chart, x, y = recommend_chart(df)

        fig = plot(df, chart=chart, x=x, y=y, show=False)
        assert fig is not None

        out = str(tmp_path / "chart.html")
        export(fig, out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_full_pipeline_matplotlib(self, sample_csv, tmp_path):
        """Load → clean → plot (matplotlib) → export PNG."""
        from plotmind.plotter import plot
        from plotmind.exporter import export

        df = load_csv(sample_csv)
        df = clean_dataframe(df)

        fig = plot(df, chart="bar", x="city", y="score", backend="matplotlib", show=False)
        assert fig is not None

        out = str(tmp_path / "chart.png")
        export(fig, out)
        assert os.path.exists(out)
