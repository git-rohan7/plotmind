"""
cli.py – Command-line interface for PlotMind.

Usage:
    plotmind data.csv
    plotmind data.csv --chart bar
    plotmind data.csv --chart scatter --x col1 --y col2
    plotmind data.csv --chart line --export output.html
    plotmind data.csv --backend matplotlib --export chart.png
"""

import argparse
import sys

from ..plotmind.loader import load_csv
from ..plotmind.cleaner import clean_dataframe
from ..plotmind.recommender import recommend_chart, CHART_TYPES
from ..plotmind.plotter import plot
from .exporter import export
from ..plotmind.detector import summarize_columns


def main():
    parser = argparse.ArgumentParser(
        prog="plotmind",
        description="PlotMind – Convert any CSV into meaningful graphs automatically.",
    )
    parser.add_argument("csv", help="Path to the CSV file")
    parser.add_argument(
        "--chart", "-c",
        choices=CHART_TYPES,
        default=None,
        help="Chart type (default: auto-recommended)",
    )
    parser.add_argument("--x", default=None, help="Column for x-axis")
    parser.add_argument("--y", default=None, help="Column for y-axis")
    parser.add_argument(
        "--export", "-e",
        default=None,
        metavar="FILE",
        help="Export path (e.g. chart.png, chart.html, chart.pdf)",
    )
    parser.add_argument(
        "--backend",
        choices=["plotly", "matplotlib"],
        default="plotly",
        help="Rendering backend (default: plotly)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Skip data cleaning step",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show column type info and exit",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Custom chart title",
    )

    args = parser.parse_args()

    # Load
    try:
        df = load_csv(args.csv)
        print(f"[PlotMind] Loaded {args.csv}  ({df.shape[0]} rows × {df.shape[1]} cols)")
    except (FileNotFoundError, ValueError) as e:
        print(f"[PlotMind] Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Info mode
    if args.info:
        summarize_columns(df)
        chart, x, y = recommend_chart(df, x=args.x, y=args.y)
        print(f"\n[PlotMind] Recommended: {chart.upper()}  x={x}  y={y}")
        return

    # Clean
    if not args.no_clean:
        df = clean_dataframe(df, verbose=True)

    # Plot
    show = args.export is None  # Only show interactively if not exporting
    try:
        fig = plot(
            df,
            chart=args.chart,
            x=args.x,
            y=args.y,
            title=args.title,
            backend=args.backend,
            show=show,
        )
    except Exception as e:
        print(f"[PlotMind] Plot error: {e}", file=sys.stderr)
        sys.exit(1)

    # Export
    if args.export:
        try:
            export(fig, args.export)
        except Exception as e:
            print(f"[PlotMind] Export error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
