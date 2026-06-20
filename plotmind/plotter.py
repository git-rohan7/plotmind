"""
plotter.py – Generates charts using Matplotlib / Plotly.
"""

from typing import Optional
import pandas as pd

from .recommender import recommend_chart


def plot(
    df: pd.DataFrame,
    chart: Optional[str] = None,
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: Optional[str] = None,
    backend: str = "plotly",
    show: bool = True,
):
    """
    Generate a chart for the given DataFrame.

    Args:
        df: Input DataFrame.
        chart: Chart type override. One of: histogram, bar, scatter, line, pie, heatmap, box.
               If None, the best chart is auto-recommended.
        x: Column name for the x-axis (auto-detected if None).
        y: Column name for the y-axis (auto-detected if None).
        title: Optional chart title.
        backend: 'plotly' (default, interactive) or 'matplotlib' (static).
        show: If True, display the chart immediately.

    Returns:
        The figure object (plotly Figure or matplotlib Figure).
    """
    # Auto-recommend if not specified
    if chart is None:
        chart, x, y = recommend_chart(df, x=x, y=y)
    else:
        if x is None and y is None:
            _, x, y = recommend_chart(df, x=x, y=y)

    chart = chart.lower()

    if backend == "plotly":
        return _plot_plotly(df, chart, x, y, title, show)
    elif backend == "matplotlib":
        return _plot_matplotlib(df, chart, x, y, title, show)
    else:
        raise ValueError(f"Unknown backend '{backend}'. Use 'plotly' or 'matplotlib'.")


# ─────────────────────────────────────────────
# Plotly backend
# ─────────────────────────────────────────────

def _plot_plotly(df, chart, x, y, title, show):
    try:
        import plotly.express as px
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError("Plotly is required for the interactive backend. Run: pip install plotly")

    auto_title = title or f"{chart.capitalize()} Chart"

    if chart == "histogram":
        col = x or df.select_dtypes(include="number").columns[0]
        fig = px.histogram(df, x=col, title=auto_title)

    elif chart == "bar":
        if x is None:
            x = df.columns[0]
        if y and y in df.columns:
            fig = px.bar(df, x=x, y=y, title=auto_title)
        else:
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            fig = px.bar(counts, x=x, y="count", title=auto_title)

    elif chart == "scatter":
        if x is None or y is None:
            num_cols = df.select_dtypes(include="number").columns.tolist()
            x = x or num_cols[0]
            y = y or num_cols[1] if len(num_cols) > 1 else num_cols[0]
        fig = px.scatter(df, x=x, y=y, title=auto_title)

    elif chart == "line":
        if x is None or y is None:
            num_cols = df.select_dtypes(include="number").columns.tolist()
            x = x or df.columns[0]
            y = y or (num_cols[0] if num_cols else df.columns[1])
        fig = px.line(df, x=x, y=y, title=auto_title)

    elif chart == "pie":
        if x is None:
            x = df.select_dtypes(include="object").columns[0]
        if y and y in df.columns:
            fig = px.pie(df, names=x, values=y, title=auto_title)
        else:
            counts = df[x].value_counts().reset_index()
            counts.columns = [x, "count"]
            fig = px.pie(counts, names=x, values="count", title=auto_title)

    elif chart == "heatmap":
        num_df = df.select_dtypes(include="number")
        corr = num_df.corr()
        fig = px.imshow(
            corr, text_auto=True, color_continuous_scale="RdBu_r",
            title=auto_title or "Correlation Heatmap"
        )

    elif chart == "box":
        if y and y in df.columns:
            fig = px.box(df, x=x, y=y, title=auto_title)
        else:
            col = y or x or df.select_dtypes(include="number").columns[0]
            fig = px.box(df, y=col, title=auto_title)

    else:
        raise ValueError(f"Unknown chart type: '{chart}'. Valid: histogram, bar, scatter, line, pie, heatmap, box")

    if show:
        fig.show()

    return fig


# ─────────────────────────────────────────────
# Matplotlib backend
# ─────────────────────────────────────────────

def _plot_matplotlib(df, chart, x, y, title, show):
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive by default; caller can change
    except ImportError:
        raise ImportError("Matplotlib is required. Run: pip install matplotlib")

    fig, ax = plt.subplots(figsize=(10, 6))
    auto_title = title or f"{chart.capitalize()} Chart"

    if chart == "histogram":
        col = x or df.select_dtypes(include="number").columns[0]
        ax.hist(df[col].dropna(), bins=20, edgecolor="black", color="#4C72B0")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")

    elif chart == "bar":
        if x is None:
            x = df.columns[0]
        if y and y in df.columns:
            ax.bar(df[x].astype(str), df[y], color="#4C72B0")
            ax.set_ylabel(y)
        else:
            counts = df[x].value_counts()
            ax.bar(counts.index.astype(str), counts.values, color="#4C72B0")
            ax.set_ylabel("Count")
        ax.set_xlabel(x)
        plt.xticks(rotation=45, ha="right")

    elif chart == "scatter":
        num_cols = df.select_dtypes(include="number").columns.tolist()
        xc = x or num_cols[0]
        yc = y or (num_cols[1] if len(num_cols) > 1 else num_cols[0])
        ax.scatter(df[xc], df[yc], alpha=0.7, color="#4C72B0")
        ax.set_xlabel(xc)
        ax.set_ylabel(yc)

    elif chart == "line":
        xc = x or df.columns[0]
        yc = y or df.select_dtypes(include="number").columns[0]
        ax.plot(df[xc], df[yc], color="#4C72B0")
        ax.set_xlabel(xc)
        ax.set_ylabel(yc)
        plt.xticks(rotation=45, ha="right")

    elif chart == "pie":
        col = x or df.select_dtypes(include="object").columns[0]
        if y and y in df.columns:
            sizes = df.groupby(col)[y].sum()
        else:
            sizes = df[col].value_counts()
        ax.pie(sizes.values, labels=sizes.index.astype(str), autopct="%1.1f%%")

    elif chart == "heatmap":
        try:
            import seaborn as sns
            num_df = df.select_dtypes(include="number")
            corr = num_df.corr()
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", ax=ax)
        except ImportError:
            num_df = df.select_dtypes(include="number")
            corr = num_df.corr()
            im = ax.imshow(corr, cmap="RdBu_r", aspect="auto")
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45, ha="right")
            ax.set_yticklabels(corr.columns)
            fig.colorbar(im, ax=ax)

    elif chart == "box":
        col = y or x or df.select_dtypes(include="number").columns[0]
        ax.boxplot(df[col].dropna(), patch_artist=True,
                   boxprops=dict(facecolor="#4C72B0", color="black"))
        ax.set_ylabel(col)

    else:
        raise ValueError(f"Unknown chart type: '{chart}'.")

    ax.set_title(auto_title)
    plt.tight_layout()

    if show:
        plt.show()

    return fig
