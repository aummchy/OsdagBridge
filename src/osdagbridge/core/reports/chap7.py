import os

from osdagbridge.core.reports import styles
from osdagbridge.core.reports.report_utils import (
    _fig_embed, steel_tonnage_chart, concrete_rebar_chart,
)


def _num(value):
    """Parse a BOQ numeric string; return None for 'N.A.'/placeholders/blank."""
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def collect_quantity_summary(input_dict):
    """Numeric values for the Chapter 7 charts, read from the same BOQ keys as
    Table 7.1.  Non-numeric placeholders are skipped, never zero-filled.
    """
    bracing = [_num(input_dict.get(k)) for k in (
        "bracing_top_wt_total", "bracing_bot_wt_total", "bracing_diag_wt_total")]
    bracing = sum(v for v in bracing if v is not None) if any(
        v is not None for v in bracing) else None
    # End diaphragms are computed by calculate_material_quantities() from the
    # design geometry (ED length derived from girder depth/spacing) and appear
    # as rows 7(a)-(c); sum the same three keys the table reads.
    ed = [_num(input_dict.get(k)) for k in (
        "ed_diag_wt_total", "ed_top_wt_total", "ed_bot_wt_total")]
    ed = sum(v for v in ed if v is not None) if any(
        v is not None for v in ed) else None
    return {
        "steel": {
            "Girders": _num(input_dict.get("steel_girders_wt_total")),
            "Cross Bracing": bracing,
            "End Diaphragms": ed,
        },
        "concrete_m3": _num(input_dict.get("concrete_deck_vol_total")),
        "rebar_mt": _num(input_dict.get("rebar_deck_wt_total")),
    }


def ch7_quantities(input_dict, fig_paths=None, tmp_images=None):
    summary = collect_quantity_summary(input_dict)

    # Task #5 — charts are written into the report's temporary image directory
    # and embedded with the same _fig_embed pipeline used by chapters 4 and 5.
    if fig_paths is not None and tmp_images:
        steel_png = steel_tonnage_chart(summary["steel"])
        if steel_png:
            p = os.path.join(tmp_images, "steel_tonnage.png")
            with open(p, "wb") as fh:
                fh.write(steel_png)
            fig_paths["steel_tonnage"] = p.replace("\\", "/")
        cr_png = concrete_rebar_chart(summary["concrete_m3"], summary["rebar_mt"])
        if cr_png:
            p = os.path.join(tmp_images, "concrete_rebar.png")
            with open(p, "wb") as fh:
                fh.write(cr_png)
            fig_paths["concrete_rebar"] = p.replace("\\", "/")

    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

\noindent\textbf{Table 7.1  Bill of Materials (Steel, Concrete, and Reinforcement Quantities)}

\begingroup
""" + styles.TABLE_OVERRIDE_TABCOLSEP_3_5PT + r"""
\begin{longtable}{|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|}
""" + styles.longtable_head(r"""\hline
\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)} \\
\hline""") + r"""
1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\hline
7(a) & End Diaphragm - Diagonals & """ + str(input_dict.get("ed_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("ed_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("ed_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("ed_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("ed_diag_wt_total", "N.A.")) + r""" \\
\hline
7(b) & End Diaphragm - Top Chord & """ + str(input_dict.get("ed_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("ed_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("ed_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("ed_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("ed_top_wt_total", "N.A.")) + r""" \\
\hline
7(c) & End Diaphragm - Bottom Chord & """ + str(input_dict.get("ed_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("ed_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("ed_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("ed_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("ed_bot_wt_total", "N.A.")) + r""" \\
\hline
\end{longtable}

""" + _fig_embed(
        fig_paths.get('steel_tonnage') if fig_paths else None,
        'Structural Steel Tonnage by Element (MT)',
        width=styles.FIGURE_WIDTH_QUANTITY,
    ) + r"""

""" + _fig_embed(
        fig_paths.get('concrete_rebar') if fig_paths else None,
        'Concrete Volume (m$^3$) and Reinforcement Steel Weight (MT) --- separate scales',
        width=styles.FIGURE_WIDTH_QUANTITY,
    ) + r"""
"""


