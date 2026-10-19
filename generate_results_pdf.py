"""
Generate results_comparison.pdf with three polished comparison tables:
  1. Comparison with Related Work
  2. DocuGuard full-system results (ViT + DiT, 13 models)
  3. ViT-Small vs DiT-Base head-to-head on forgery tasks

Run:
    python generate_results_pdf.py
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle


# ── Color palette ────────────────────────────────────────────────────────
HEADER_BG = "#1F3A68"        # deep navy
HEADER_FG = "#FFFFFF"
SECTION_BG = "#DCE4F2"       # section-header band inside a table
ROW_WHITE = "#FFFFFF"
ROW_ZEBRA = "#F5F8FD"        # very soft blue-gray
BORDER = "#C8D1E0"

WINNER_BG = "#DFF5E1"        # pale green — better model
LOSER_BG = "#FCE4E4"         # pale red   — worse model
NEUTRAL_BG = "#EEF3FB"

AVG_BG = "#E4ECFB"           # averages/highlight rows
DELTA_NEG_FG = "#B22222"     # red text for negative deltas

TITLE_FG = "#1F3A68"


def _style_cell(cell, *, fill=None, bold=False, fg="black", align="center",
                height=None, pad=None):
    cell.set_facecolor(fill if fill else ROW_WHITE)
    cell.set_edgecolor(BORDER)
    cell.set_linewidth(0.6)
    props = {"ha": align, "va": "center", "color": fg}
    if bold:
        props["fontweight"] = "bold"
    cell.set_text_props(**props)
    if height is not None:
        cell.set_height(height)
    if pad is not None:
        cell.PAD = pad


def draw_table(
    ax, title, columns, rows, col_widths,
    header_height=0.085, row_height=0.055, font_size=10,
    row_styles=None,        # dict: row_index -> {"fill": ..., "bold": True}
    cell_styles=None,       # dict: (row_index, col_index) -> {"fill": ..., "fg": ..., "bold": True}
    subtitle=None,
):
    """Draw a polished titled table on the given Axes."""
    ax.axis("off")

    # Title
    ax.text(
        0.0, 1.05, title,
        transform=ax.transAxes, fontsize=14, fontweight="bold",
        ha="left", va="bottom", color=TITLE_FG,
    )
    if subtitle:
        ax.text(
            0.0, 1.01, subtitle,
            transform=ax.transAxes, fontsize=9.5, style="italic",
            ha="left", va="bottom", color="#4A5568",
        )

    table = ax.table(
        cellText=[list(r) for r in rows],
        colLabels=columns,
        colWidths=col_widths,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(font_size)
    table.scale(1.0, 1.0)

    row_styles = row_styles or {}
    cell_styles = cell_styles or {}

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            _style_cell(cell, fill=HEADER_BG, fg=HEADER_FG, bold=True,
                        height=header_height)
        else:
            data_row = r - 1
            style = row_styles.get(data_row, {})
            fill = style.get("fill", ROW_ZEBRA if data_row % 2 else ROW_WHITE)
            bold = style.get("bold", False)
            fg = style.get("fg", "black")

            # per-cell override
            cstyle = cell_styles.get((data_row, c), {})
            if cstyle:
                fill = cstyle.get("fill", fill)
                bold = cstyle.get("bold", bold)
                fg = cstyle.get("fg", fg)

            _style_cell(cell, fill=fill, bold=bold, fg=fg,
                        height=row_height)


# ═════════════════════════════════════════════════════════════════════════
# Page 1 — Related Work
# ═════════════════════════════════════════════════════════════════════════
def page_related_work(pdf):
    fig = plt.figure(figsize=(12, 4.8))
    ax = fig.add_axes([0.05, 0.08, 0.90, 0.80])

    columns = ["Task", "Reference", "Dataset", "Prior Acc.", "Our Model", "Our Acc."]
    rows = [
        ["Face Forgery Detection",     "Guan et al. (2024)",  "IDNet", "95%",  "ViT-Small (Fraud Type)",  "95.86%"],
        ["General Forgery Detection",  "Boned et al. (2024)", "SIDTD", ">99%", "ViT-Small (Real vs Fake)", "93.92%"],
        ["Few-shot Forgery Detection", "Boned et al. (2024)", "SIDTD", "~82%", "ViT-Small (Real vs Fake)", "93.92%"],
    ]

    # Highlight "our accuracy" cells when we beat/tie prior work
    cell_styles = {
        (0, 5): {"fill": WINNER_BG, "bold": True},   # 95.86 > 95
        (1, 5): {"fill": LOSER_BG,  "bold": True},   # 93.92 < 99
        (2, 5): {"fill": WINNER_BG, "bold": True},   # 93.92 > 82
    }

    draw_table(
        ax,
        "Table 1 — Comparison with Related Work",
        columns, rows,
        col_widths=[0.22, 0.17, 0.10, 0.12, 0.24, 0.15],
        header_height=0.12, row_height=0.12, font_size=10,
        cell_styles=cell_styles,
        subtitle="Green = DocuGuard outperforms prior work · Red = below prior work",
    )
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═════════════════════════════════════════════════════════════════════════
# Page 2 — Full system (all 13 models, side-by-side ViT vs DiT)
# ═════════════════════════════════════════════════════════════════════════
def page_full_results(pdf):
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_axes([0.05, 0.06, 0.90, 0.85])

    columns = ["Stage", "Task", "Document Type", "Primary model", "Alternative model"]
    rows = [
        ["Stage 1", "Document Type (3 classes)", "—",               "ViT-Tiny  91.63%",   "ResNet-18  88.96%"],

        ["Stage 2", "Binary (Real vs Fake)",     "Driver's License", "ViT-Small  93.07%", "DiT-Base  85.73%"],
        ["Stage 2", "Binary (Real vs Fake)",     "ID Card",          "ViT-Small  93.60%", "DiT-Base  77.30%"],
        ["Stage 2", "Binary (Real vs Fake)",     "Passport",         "ViT-Small  95.10%", "DiT-Base  83.00%"],

        ["Stage 3", "Fraud Type (Morph/Repl.)",  "Driver's License", "ViT-Small  94.67%", "DiT-Base  94.40%"],
        ["Stage 3", "Fraud Type (Morph/Repl.)",  "ID Card",          "ViT-Small  96.50%", "DiT-Base  93.60%"],
        ["Stage 3", "Fraud Type (Morph/Repl.)",  "Passport",         "ViT-Small  96.40%", "DiT-Base  93.60%"],

        ["Average", "Stage 1 — primary vs baseline",        "", "91.63%", "88.96%"],
        ["Average", "Stages 2–3 — ViT-Small vs DiT-Base",    "", "94.89%", "87.94%"],
    ]

    cell_styles = {}

    # All 7 primary-vs-alternative rows: primary wins every time → green/red
    for r in range(7):
        cell_styles[(r, 3)] = {"fill": WINNER_BG, "bold": True}
        cell_styles[(r, 4)] = {"fill": LOSER_BG}

    # Averages
    row_styles = {
        7: {"fill": AVG_BG, "bold": True},
        8: {"fill": AVG_BG, "bold": True},
    }
    cell_styles[(7, 3)] = {"fill": WINNER_BG, "bold": True}
    cell_styles[(7, 4)] = {"fill": LOSER_BG, "bold": True}
    cell_styles[(8, 3)] = {"fill": WINNER_BG, "bold": True}
    cell_styles[(8, 4)] = {"fill": LOSER_BG, "bold": True}

    draw_table(
        ax,
        "Table 2 — DocuGuard Full System Results (Primary vs Alternative)",
        columns, rows,
        col_widths=[0.10, 0.28, 0.18, 0.22, 0.22],
        header_height=0.085, row_height=0.085, font_size=10.5,
        row_styles=row_styles,
        cell_styles=cell_styles,
        subtitle="Stage 1: ViT-Tiny vs ResNet-18 · Stages 2–3: ViT-Small vs DiT-Base · Green = primary wins (7/7)",
    )
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ═════════════════════════════════════════════════════════════════════════
# Page 3 — Head-to-head ViT-Small vs DiT-Base
# ═════════════════════════════════════════════════════════════════════════
def page_head_to_head(pdf):
    fig = plt.figure(figsize=(12, 6.5))
    ax = fig.add_axes([0.05, 0.08, 0.90, 0.80])

    columns = ["Task", "Document Type", "ViT-Small", "DiT-Base", "Δ (DiT − ViT)"]
    rows = [
        ["Binary (Real vs Fake)",    "Driver's License", "93.07%", "85.73%", "−7.34"],
        ["Binary (Real vs Fake)",    "ID Card",          "93.60%", "77.30%", "−16.30"],
        ["Binary (Real vs Fake)",    "Passport",         "95.10%", "83.00%", "−12.10"],

        ["Fraud Type (Morph/Repl.)", "Driver's License", "94.67%", "94.40%", "−0.27"],
        ["Fraud Type (Morph/Repl.)", "ID Card",          "96.50%", "93.60%", "−2.90"],
        ["Fraud Type (Morph/Repl.)", "Passport",         "96.40%", "93.60%", "−2.80"],

        ["Mean",                     "—",                "94.89%", "87.94%", "−6.95"],
    ]

    cell_styles = {}
    # Winner highlight on every data row (ViT beats DiT in all 6)
    for r in range(6):
        cell_styles[(r, 2)] = {"fill": WINNER_BG, "bold": True}
        cell_styles[(r, 3)] = {"fill": LOSER_BG}
        cell_styles[(r, 4)] = {"fg": DELTA_NEG_FG, "bold": True}

    # Mean row — emphasize
    row_styles = {6: {"fill": AVG_BG, "bold": True}}
    cell_styles[(6, 2)] = {"fill": WINNER_BG, "bold": True}
    cell_styles[(6, 3)] = {"fill": LOSER_BG,  "bold": True}
    cell_styles[(6, 4)] = {"fg": DELTA_NEG_FG, "bold": True, "fill": AVG_BG}

    draw_table(
        ax,
        "Table 3 — ViT-Small vs DiT-Base (Head-to-Head on Forgery Tasks)",
        columns, rows,
        col_widths=[0.24, 0.22, 0.16, 0.16, 0.18],
        header_height=0.10, row_height=0.10, font_size=11,
        row_styles=row_styles,
        cell_styles=cell_styles,
        subtitle="ViT-Small wins on all 6 forgery tasks · Largest gap: ID Card Binary (−16.3) · Smallest: DL Fraud (−0.3)",
    )
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main():
    out_path = "results_comparison.pdf"
    with PdfPages(out_path) as pdf:
        page_related_work(pdf)
        page_full_results(pdf)
        page_head_to_head(pdf)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
