# PlotMind 📊

> **Convert any CSV into meaningful graphs automatically.**

PlotMind analyses your CSV, detects column types, recommends the best chart, and generates it — with zero manual configuration. It supports interactive charts via Plotly and static charts via Matplotlib, and can export to PNG, PDF, or HTML.

---

## Installation

```bash
pip install plotmind
```

Or install from source:

```bash
git clone https://github.com/git-rohan7/plotmind
cd plotmind
pip install -e .
```

---

## Quick Start

### Python API

```python
from plotmind import load_csv, clean_dataframe, plot, export

# 1. Load
df = load_csv("sales.csv")

# 2. Clean (handles missing values, duplicates, type coercion)
df = clean_dataframe(df, verbose=True)

# 3. Plot – auto-detects best chart
fig = plot(df)

# 4. Export
export(fig, "sales_chart.html")
export(fig, "sales_chart.png")
```

### Command-Line Interface

```bash
# Auto-detect best chart and display
plotmind sales.csv

# Choose a specific chart type
plotmind sales.csv --chart bar

# Specify axes
plotmind sales.csv --chart scatter --x revenue --y profit

# Export to file without displaying
plotmind sales.csv --chart line --export output.html

# Use matplotlib backend
plotmind sales.csv --backend matplotlib --export chart.png

# Show column info and recommendation
plotmind sales.csv --info
```

---

## Features

| Feature                   | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| **Auto-chart selection**  | Detects the best chart based on column types                 |
| **Column type detection** | Identifies numerical, categorical, datetime, boolean columns |
| **Data cleaning**         | Fills missing values, removes duplicates, fixes types        |
| **Interactive charts**    | Plotly backend for zoom/hover/pan                            |
| **Static charts**         | Matplotlib backend for PNG/PDF output                        |
| **Export**                | PNG, PDF, HTML, SVG                                          |
| **CLI**                   | Full command-line interface                                  |

---

## Chart Types

PlotMind supports these chart types (auto-selected or manually chosen):

| Chart       | When auto-selected                             |
| ----------- | ---------------------------------------------- |
| `histogram` | Single numerical column                        |
| `bar`       | Categorical + numerical (high cardinality)     |
| `pie`       | Categorical + numerical (≤6 unique categories) |
| `scatter`   | Two numerical columns                          |
| `line`      | Datetime + numerical                           |
| `heatmap`   | Many numerical columns (correlation matrix)    |
| `box`       | Box plot for distribution                      |

---

## API Reference

### `load_csv(filepath, **kwargs) → DataFrame`

Load a CSV and validate it.

```python
df = load_csv("data.csv")
```

---

### `clean_dataframe(df, verbose=False) → DataFrame`

Clean: fill missing values, remove duplicates, coerce types.

```python
df = clean_dataframe(df, verbose=True)
```

---

### `detect_columns(df) → dict`

Return a dict of `{column_name: type}` for each column.
Types: `numerical`, `categorical`, `datetime`, `boolean`, `unknown`.

```python
from plotmind import detect_columns
types = detect_columns(df)
# {'age': 'numerical', 'city': 'categorical', ...}
```

---

### `recommend_chart(df, x=None, y=None) → (chart, x_col, y_col)`

Recommend the best chart. Returns a tuple.

```python
from plotmind import recommend_chart
chart, x, y = recommend_chart(df)
print(chart)  # e.g. 'scatter'
```

---

### `plot(df, chart=None, x=None, y=None, title=None, backend='plotly', show=True) → Figure`

Generate a chart. Returns the figure object.

```python
fig = plot(df, chart="bar", x="city", y="sales", title="Sales by City")
fig = plot(df, backend="matplotlib", show=False)  # static, no display
```

---

### `export(fig, path, fmt=None) → str`

Export the figure. Format is inferred from the file extension.

```python
export(fig, "chart.png")    # PNG (requires kaleido for Plotly)
export(fig, "chart.pdf")    # PDF
export(fig, "chart.html")   # Interactive HTML (Plotly) or embedded HTML (Matplotlib)
export(fig, "chart.svg")    # SVG
```

---

## Utils

```python
from plotmind.utils import preview, column_stats, filter_columns

preview(df)               # Print head
column_stats(df)          # Summary DataFrame with null counts, unique values, etc.
filter_columns(df, types=["number"])  # Get only numeric column names
```

---

## Testing

```bash
pip install plotmind[dev]
pytest tests/ -v
```

---

## Requirements

- Python ≥ 3.8
- pandas ≥ 1.3
- plotly ≥ 5.0
- matplotlib ≥ 3.4
- kaleido ≥ 0.2.1 _(for Plotly static image export)_

Optional:

- seaborn _(for nicer heatmaps with `pip install plotmind[seaborn]`)_

---

## License

MIT
