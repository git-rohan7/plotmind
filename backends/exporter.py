"""
exporter.py – Saves chart outputs as PNG, PDF, or HTML.
"""

import os
from typing import Optional


def export(fig, path: str, fmt: Optional[str] = None) -> str:
    out_dir = os.path.dirname(os.path.abspath(path))
    os.makedirs(out_dir, exist_ok=True)

    # Determine format
    if fmt is None:
        ext = os.path.splitext(path)[-1].lower().lstrip(".")
        if not ext:
            raise ValueError("Cannot determine format from path. Provide fmt='png'|'pdf'|'html'.")
        fmt = ext

    fmt = fmt.lower()
    if fmt not in ("png", "pdf", "html", "svg"):
        raise ValueError(f"Unsupported format '{fmt}'. Use: png, pdf, html, svg.")

    # Detect figure type
    _type = _detect_fig_type(fig)

    if _type == "plotly":
        _export_plotly(fig, path, fmt)
    elif _type == "matplotlib":
        _export_matplotlib(fig, path, fmt)
    else:
        raise TypeError(f"Unrecognised figure object: {type(fig)}. Pass a Plotly or Matplotlib figure.")

    abs_path = os.path.abspath(path)
    print(f"[PlotMind] Saved → {abs_path}")
    return abs_path


def _detect_fig_type(fig) -> str:
    try:
        import plotly.graph_objects as go
        if isinstance(fig, go.Figure):
            return "plotly"
    except ImportError:
        pass

    try:
        import matplotlib.figure
        if isinstance(fig, matplotlib.figure.Figure):
            return "matplotlib"
    except ImportError:
        pass

    return "unknown"


def _export_plotly(fig, path: str, fmt: str) -> None:
    if fmt == "html":
        fig.write_html(path)
    else:
        # Requires kaleido for static exports
        try:
            fig.write_image(path, format=fmt)
        except Exception as e:
            raise RuntimeError(
                f"Plotly static export failed. Install kaleido: pip install kaleido\n"
                f"Original error: {e}"
            )


def _export_matplotlib(fig, path: str, fmt: str) -> None:
    if fmt == "html":
        # Matplotlib doesn't natively export HTML; save as PNG inside minimal HTML
        import base64
        import io

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()

        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>PlotMind Chart</title></head>
<body style="margin:0;background:#fff;display:flex;justify-content:center">
  <img src="data:image/png;base64,{img_b64}" style="max-width:100%;height:auto">
</body>
</html>"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
    else:
        fig.savefig(path, format=fmt, bbox_inches="tight", dpi=150)
