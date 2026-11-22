# -*- coding: utf-8 -*-
"""
Single source of truth for all report layout rules and visual attributes
(scope item #6: Centralized Formatting & Style System).

STRICT RULES (refactor contract):
  * Every value in this file is a VERBATIM copy of the value that existed in the
    consumer script before the refactor. Do NOT change, tune, "improve", merge
    or deduplicate any value here without asking first.
  * This module is LEAF-ONLY: it must not import anything from other
    ``reports/*`` modules (no circular imports).
  * Consumers (preamble, executive_summary, chap*.py, report_utils) must import
    formatting from here instead of re-typing it — and must not keep private
    copies.

Source of truth for extraction (pre-refactor locations):
  report_generator.py:150-277 (preamble), 346-376 (toc_section), 317 (title page)
  executive_summary.py:143-144 (column math), 250-251 (chapter title restore)
  chap1/2/3/4/5/7/8.py (table specs & local padding overrides)
  report_utils.py:76-111 (figure widths/padding)
"""

# ═══════════════════════════════════════════════════════════════════════
# 1. PAGE & DOCUMENT SETTINGS
#    (was: report_generator.preamble — geometry, docclass, spacing, captions)
# ═══════════════════════════════════════════════════════════════════════

DOCCLASS = r"\documentclass[12pt,a4paper]{report}"
GEOMETRY_PACKAGE = r"\usepackage[a4paper, margin=1in]{geometry}"
LINE_SPACING = r"\setstretch{1.15}"

# task2 — reserve explicit room for the fancy footer and stop the report class's
# default \flushbottom from stretching glue into it. Without these, table rows
# (e.g. a "G3" row) land below the 72pt body margin, in the footer zone.
FOOTSKIP = r"\setlength{\footskip}{45pt}"
RAGGED_BOTTOM = r"\raggedbottom"

CAPTION_SETUP = r"""\captionsetup{
    labelfont=bf,
    justification=raggedright,
    singlelinecheck=false,
    format=plain
}"""

# ═══════════════════════════════════════════════════════════════════════
# 2. COLOR PALETTE
#    (was: report_generator.py:209 — only color defined pre-refactor;
#      failRed reserved for scope item #4 UR threshold line, NOT yet used)
# ═══════════════════════════════════════════════════════════════════════

COLOR_OSDAG_GREEN = r"\definecolor{osdagGreen}{HTML}{91B014}"
OSDAG_GREEN_HEX = "91B014"

# Reserved in task6 for scope item #4: red dashed UR = 1.0 threshold / failing bars.
FAIL_RED_HEX = "C00000"

# ═══════════════════════════════════════════════════════════════════════
# 3. TABLE STYLE RULES — GLOBAL (was: report_generator.py:193-207)
# ═══════════════════════════════════════════════════════════════════════

TABLE_LENGTHS = r"""\numberwithin{table}{chapter}
\numberwithin{figure}{chapter}
% Table layout and spacing: consistent padding, row height, and longtable pre/post skips
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.12}
\setlength{\LTpre}{0pt}
\setlength{\LTpost}{6pt}
% Table rules (outline thickness) and small extra row height for clarity
\setlength{\arrayrulewidth}{0.5pt}
\setlength{\extrarowheight}{0.6pt}"""

# Prevent tables from overflowing past the page bottom:
# if fewer than 5 baseline-skips remain, break to the next page first.
TABLE_NEEDSPACE = r"""\BeforeBeginEnvironment{table}{\needspace{5\baselineskip}}"""

# Longtable alignment defaults (was: report_generator.py:184-185)
LT_ALIGN = r"""\setlength{\LTleft}{\fill}
\setlength{\LTright}{\fill}"""

# ── Local table-padding overrides found in chapter scripts ──────────────
# These are EXCEPTIONS that already existed in the code. They are kept
# exactly as-is and are NOT merged into the global values above.
TABLE_OVERRIDE_TABCOLSEP_4PT = r"\setlength{\tabcolsep}{4pt}"
#   used at: chap2.py:387,402  chap5.py:1411,1455
TABLE_OVERRIDE_TABCOLSEP_3_5PT = r"\setlength{\tabcolsep}{3.5pt}"
#   used at: chap7.py:9  chap8.py:59,82
TABLE_OVERRIDE_TABCOLSEP_3PT = r"\setlength{\tabcolsep}{3pt}"
#   used at: chap4.py:86
TABLE_OVERRIDE_ARRAYSTRETCH_1_25 = r"\renewcommand{\arraystretch}{1.25}"
#   used at: chap4.py:87
TABLE_OVERRIDE_LTLEFT_0 = r"""\setlength\LTleft{0pt}
\setlength\LTright{\fill}"""
#   used at: chap2.py:388-389,403-404  chap5.py:1205-1206,1412-1413

# Braced spelling at chap5.py:1456-1457 — verbatim copy, kept SEPARATE from the
# braceless TABLE_OVERRIDE_LTLEFT_0 above (never merge the two spellings).
TABLE_OVERRIDE_LTLEFT_0_BRACED = r"""\setlength{\LTleft}{0pt}
\setlength{\LTright}{\fill}"""

# ═══════════════════════════════════════════════════════════════════════
# 4. HEADER / FOOTER THEME
#    (was: report_generator.py:211-253 — three page styles, kept verbatim
#      and separate: main / plain / firstpage are NOT merged)
# ═══════════════════════════════════════════════════════════════════════

FOOT_LEFT = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
FOOT_RIGHT = r"Page \thepage\ of \pageref{LastPage}"
RULE_HEIGHT = "1pt"
HEAD_RULE_VSPACE = "2pt"
FOOT_RULE_VSPACE = "6pt"
SDNOTE_VSPACE_NEG = "-20pt"     # Software-default note, main/plain footrule
SDNOTE_VSPACE = "4pt"
FOOTRULE_VSPACE_NEG = "-8pt"

HEADLINE_1 = " $|$ "           # joins project name | job number
FOOTER_SEPARATOR = " $|$ "


def page_styles(project_name_tex, job_number_tex, report_date_tex, report_version_tex):
    """Verbatim copy of the fancy page-style block formerly in
    report_generator.preamble() (styles: main, plain, firstpage).
    Returns the exact same LaTeX string as before the refactor.
    """
    pn, jn, rd, rv = (project_name_tex, job_number_tex,
                      report_date_tex, report_version_tex)
    return (
        r"""\fancypagestyle{main}{
  \fancyhf{}
  \fancyhead[L]{""" + pn + r""" $|$ """ + jn + r"""}
  \fancyhead[R]{""" + rd + r""" $|$ """ + rv + r"""}
  \fancyfoot[L]{""" + FOOT_LEFT + r"""}
  \fancyfoot[R]{""" + FOOT_RIGHT + r"""}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height """ + RULE_HEIGHT + r""" \vspace{""" + HEAD_RULE_VSPACE + r"""}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{""" + SDNOTE_VSPACE_NEG + r"""}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{""" + SDNOTE_VSPACE + r"""}%
    }{%
      \vspace{""" + FOOTRULE_VSPACE_NEG + r"""}%
    }%
    \color{osdagGreen}\hrule width\headwidth height """ + RULE_HEIGHT + r""" \vspace{""" + FOOT_RULE_VSPACE + r"""}%
  }
}
\fancypagestyle{plain}{
  \fancyhf{}
  \fancyhead[L]{""" + pn + r""" $|$ """ + jn + r"""}
  \fancyhead[R]{""" + rd + r""" $|$ """ + rv + r"""}
  \fancyfoot[L]{""" + FOOT_LEFT + r"""}
  \fancyfoot[R]{""" + FOOT_RIGHT + r"""}
  \renewcommand{\headrule}{\color{osdagGreen}\hrule width\headwidth height """ + RULE_HEIGHT + r""" \vspace{""" + HEAD_RULE_VSPACE + r"""}}
  \renewcommand{\footrule}{%
    \ifbool{hasSDonPage}{%
      \vspace{""" + SDNOTE_VSPACE_NEG + r"""}%
      \hbox to \headwidth{\textcolor{black}{\footnotesize\textit{* Software default value}}\hfil}%
      \vspace{""" + SDNOTE_VSPACE + r"""}%
    }{%
      \vspace{""" + FOOTRULE_VSPACE_NEG + r"""}%
    }%
    \color{osdagGreen}\hrule width\headwidth height """ + RULE_HEIGHT + r""" \vspace{""" + FOOT_RULE_VSPACE + r"""}%
  }
}
\fancypagestyle{firstpage}{
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyfoot[L]{""" + FOOT_LEFT + r"""}
  \fancyfoot[R]{""" + FOOT_RIGHT + r"""}
  \renewcommand{\footrule}{\vspace{""" + FOOTRULE_VSPACE_NEG + r"""}\color{osdagGreen}\hrule width\headwidth height """ + RULE_HEIGHT + r""" \vspace{""" + FOOT_RULE_VSPACE + r"""}}
}
\pagestyle{main}"""
    )


# ═══════════════════════════════════════════════════════════════════════
# 5. HEADINGS, CHAPTER TITLES & TOC
# ═══════════════════════════════════════════════════════════════════════

# Was: report_generator.py:349-351 (toc_section)
CHAPTER_TITLE_FORMAT = r"""\titleformat{\chapter}[block]
  {\normalfont\Large\bfseries\centering}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{0pt}{10pt}"""

# Was: executive_summary.py:250-251 ("Restore numbered chapter format").
# Deliberately SEPARATE from CHAPTER_TITLE_FORMAT — different \titlespacing*
# (-30pt vs 0pt). Do NOT merge the two without asking.
CHAPTER_TITLE_RESTORE = r"""\titleformat{\chapter}[block]{\normalfont\Large\bfseries\centering}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{-30pt}{10pt}"""

# Was: report_generator.py:348-371 (toc_section — chapter/section/subsection)
TOC_CONTENTS_STYLES = r"""% Chapter / TOC Formatting
\titleformat{\chapter}[block]
  {\normalfont\Large\bfseries\centering}{\thechapter}{1em}{}
\titlespacing*{\chapter}{0pt}{0pt}{10pt}
\setcounter{tocdepth}{2}

% TOC styling using titletoc
\titlecontents{chapter}[1.5em]
  {\normalfont\vspace{2pt}}
  {\contentslabel{1.5em}}
  {\hspace*{-1.5em}}
  {\hfill\contentspage}

\titlecontents{section}[3.8em]
  {\normalfont}
  {\contentslabel{2.3em}}
  {\hspace*{-2.3em}}
  {\hfill\contentspage}

\titlecontents{subsection}[7.0em]
  {\normalfont}
  {\contentslabel{3.2em}}
  {\hspace*{-3.2em}}
  {\hfill\contentspage}"""

# Was: report_generator.py:374
TOC_HEADING = r"\renewcommand{\contentsname}{\centering\Large\bfseries Table of Contents}"

# Was: report_generator.py:257-262 (custom commands + column types)
COLUMN_TYPES = r"""\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}"""

# ═══════════════════════════════════════════════════════════════════════
# 6. SHARED TABLE COLUMN SPECS (repeated verbatim in many files)
# ═══════════════════════════════════════════════════════════════════════

# 2-column key/value table — was retyped at:
#   chap1.py:13, chap2.py:102,123,146, executive_summary.py:193
STD_COLSPEC_2COL = r"|L{5.5cm}|L{8.5cm}|"

# 2-column longtable (label + value) — was retyped at:
#   chap2.py:170,193,426,454, chap3.py:275,289,303,319,343,369,
#   chap5.py:1235
STD_COLSPEC_LONG_2COL = r"|L{5.5cm}|p{10.0cm}|"

# Title-page key/value table — was at report_generator.py:317
TITLEPAGE_COLSPEC = r"|L{4cm}|L{10cm}|"

# NOTE: all other table specs (the ~40 unique longtable specs in chap2/3/4/5/7/8)
# are one-off, table-specific structures — left in place for now (see working/
# notes: pending user decision whether to also centralize them).

# ── Longtable repeated headers (task1) ──────────────────────────────────────

def longtable_head(header_rows: str) -> str:
    """Build the first-page and repeated header of a ``longtable``.

    The caller emits ``\\caption{...}\\\\`` immediately before the helper call and
    writes the table body immediately after it. The header row block is given
    ONCE (written between ``\\hline`` markers) and emitted twice: once as the
    first-page head and once as the head repeated on every continuation page.
    Keeping the block in one place avoids the copy/paste bug where the repeated
    head was left empty.

    Tables that have no column-header row (simple key/value 2-column tables)
    are deliberately NOT wrapped — see working/01_repeated_table_headers.md.
    """
    return (header_rows + "\n\\endfirsthead\n\n"
            + header_rows + "\n\\endhead")

# ═══════════════════════════════════════════════════════════════════════
# 7. FIGURE SETTINGS
#    (was: report_utils.py:76-111, chap6.py:31-62, chap4.py:179-181)
# ═══════════════════════════════════════════════════════════════════════

FIGURE_WIDTH_DEFAULT = r"0.9\textwidth"       # report_utils._fig_or_placeholder
FIGURE_WIDTH_EMBED = r"\textwidth"            # report_utils._fig_embed
FIGURE_PLACEHOLDER_BOX = r"0.97\textwidth"    # report_utils:89,111  chap6.py:39
FIGURE_VSPACE_BEFORE = r"\vspace{-0.5em}"     # report_utils:103,108
FIGURE_VSPACE_AFTER = r"\vspace{0.5em}"       # report_utils:106
FIGURE_WIDTH_CHAP6 = r"0.85\textwidth"        # chap6.py:32
FIGURE_MINIPAGE_CHAP6 = r"0.31\textwidth"     # chap6.py:62
FIGURE_WIDTH_ENVELOPES = r"0.75\textwidth"    # chap4.py:179,180,181
FIGURE_WIDTH_UR_SUMMARY = r"0.80\textwidth"   # chap5.py: UR summary bar chart (task4)

# ═══════════════════════════════════════════════════════════════════════
# 8. EXECUTIVE SUMMARY COLUMN MATH
#    (was: executive_summary.py:142-144 — the 15.0cm "available width"
#      is coupled to GEOMETRY margin=1in; keep the literal value)
# ═══════════════════════════════════════════════════════════════════════

EXEC_LABEL_COL_CM = 2.8
EXEC_AVAILABLE_WIDTH_CM = 15.0   # "Available width ≈ 15.0cm for A4 with 1in margins"
EXEC_MIN_GIRDER_COL_CM = 1.5
