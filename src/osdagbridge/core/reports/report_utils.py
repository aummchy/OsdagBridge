from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS
)
from osdagbridge.core.reports import styles


def _tex(value):
    """Escape a Python value for safe LaTeX embedding."""
    s = str(value) if value is not None else ''
    if not s:
        return r''
    # Normalise non-ASCII glyphs from section designations (e.g. "∠ 100 ⅹ 100ⅹ 10")
    # that pdflatex cannot render.
    for uni, ascii_ in [('∠', 'L'), ('ⅹ', 'x'), ('×', 'x')]:
        s = s.replace(uni, ascii_)
    s = s.replace('\\', r'\textbackslash{}')
    for ch, esc in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
                    ('{', r'\{'), ('}', r'\}'),          
                    ('_', r'\_\allowbreak{}'),            
                    ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        s = s.replace(ch, esc)
    s = s.replace(':', r':\allowbreak{}')
    return s


def _render_value(source_dict, key, unit=""):
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    return _tex(val) + unit


def get_girder_entries(input_dict):
    """
    Retrieve all girder labels and member IDs from backend keys.

    Usage Example:
    --------------------------
    girder_entries = get_girder_entries(bridge.input_dict)
    
    # 1. Fallback handling (if backend hasn't populated keys yet)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1))
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
        
    # 2. Get total number of girders safely
    n_girders = len(girder_entries)
    
    # 3. Iterate over the girders to build table rows
    for lbl, mid in girder_entries:
        # lbl will be e.g., "G1", mid will be e.g., "G1M1"
        # Access girder specific keys dynamically:
        # val = input_dict.get(f"{KEY_MP_GIRDER_DEPTH}.{lbl}.{mid}")
        pass

    Returns:
        List[Tuple[str, str]]
    """
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))

    entries = []

    for i in range(1, n + 1):
        entries.append(
            (
                input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", ""),
                input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", ""),
            )
        )

    return entries


def _fig_or_placeholder(path, caption, width=styles.FIGURE_WIDTH_DEFAULT):
    """Embed figure if path is provided (file already copied to assets), else show placeholder box.
    path is the relative path as pdflatex will see it (e.g. 'assets/plan.png').
    """
    if path:
        p = path.replace('\\', '/')
        return (r'\begin{figure}[H]' + '\n'
                r'\centering' + '\n'
                r'\includegraphics[width=' + width + ']{' + p + '}\n'
                r'\caption*{' + caption + '}\n'
                r'\end{figure}')
    return (r'\begin{figure}[H]' + '\n'
            r'\centering' + '\n'
            r'\fbox{\parbox{' + styles.FIGURE_PLACEHOLDER_BOX + '}{' + '\n'
            r'\textit{[ PLACEHOLDER: ' + caption + r' ]}' + '\n'
            r'}}' + '\n'
            r'\caption*{' + caption + '}\n'
            r'\end{figure}')

def _fig_embed(path, caption, width=styles.FIGURE_WIDTH_EMBED, height=None):
    """Embed a real figure when path is provided (already copied); otherwise use an fbox placeholder."""
    if path:
        p = path.replace('\\', '/')
        opts = 'width=' + width
        if height:
            opts += ',height=' + height + ',keepaspectratio'
        return (r'\begin{figure}[H]' + '\n'
                + styles.FIGURE_VSPACE_BEFORE + '\n'
                r'\centering' + '\n'
                r'\includegraphics[' + opts + ']{' + p + '}\n'
                + styles.FIGURE_VSPACE_AFTER + '\n'
                r'\caption*{\small ' + caption + '}\n'
                + styles.FIGURE_VSPACE_BEFORE + '\n'
                r'\end{figure}')
    # fbox placeholder — matches template exactly
    return (r'\noindent\fbox{\parbox{' + styles.FIGURE_PLACEHOLDER_BOX + '}{' + '\n'
            r'\textit{[ PLACEHOLDER: ' + caption + r' ]}' + '\n'
            r'}}')


# Display labels for the four element categories in the UR summary chart.
_UR_CHART_LABELS = {
    "Steel Plate Girders": "Steel Plate\nGirders",
    "Concrete Deck Slab": "Concrete Deck\nSlab",
    "Cross Bracing": "Cross\nBracing",
    "End Diaphragms": "End\nDiaphragms",
}


def ur_summary_chart(values):
    """Render a bar chart of governing utilization ratios to PNG bytes.

    ``values`` is an ordered mapping ``{category: UR}`` (see
    ``chap5.collect_ur_summary``).  Bars are green for UR <= 1.0 and red for
    UR > 1.0; a red dashed reference line marks the UR = 1.0 limit.

    Rendered with Pillow (not matplotlib): matplotlib's compiled bezier
    extension crashes under the bundled osdagbridge-env on Windows, while
    Pillow is already a report dependency.  Fully deterministic — no fonts or
    colors are chosen randomly.  Returns ``None`` on failure so a missing
    chart degrades to the existing placeholder instead of breaking the report.
    """
    if not values:
        return None
    try:
        import io
        import logging
        import os

        from PIL import Image, ImageDraw, ImageFont

        green = "#" + styles.OSDAG_GREEN_HEX
        red = "#" + styles.FAIL_RED_HEX
        names = list(values)
        nums = [float(values[n]) for n in names]
        labels = [_UR_CHART_LABELS.get(n, n) for n in names]

        # Canvas (2× final display size for crisp downsampling).
        W, H = 1400, 700
        left, right, top, bottom = 140, 50, 95, 130
        plot_w, plot_h = W - left - right, H - top - bottom
        ymax = max(1.2, max(nums) * 1.15)
        ypx = lambda v: top + plot_h * (1.0 - v / ymax)

        font_path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"),
                                 "Fonts", "arial.ttf")
        try:
            f_title = ImageFont.truetype(font_path, 26)
            f_tick = ImageFont.truetype(font_path, 20)
            f_label = ImageFont.truetype(font_path, 22)
            f_value = ImageFont.truetype(font_path, 22)
            f_note = ImageFont.truetype(font_path, 19)
        except OSError:  # pragma: no cover - fallback font
            f_title = f_tick = f_label = f_value = f_note = ImageFont.load_default()

        img = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(img)

        # Title and y-axis caption.
        title = "Governing Utilization Ratios by Element"
        d.text(((W - d.textlength(title, font=f_title)) / 2, 18), title,
               fill="#222222", font=f_title)
        d.text((left - 118, top - 48), "UR", fill="#222222", font=f_tick)

        # Horizontal gridlines + y tick labels.
        step = 0.25 if ymax <= 1.6 else 0.5
        t = 0.0
        while t <= ymax + 1e-9:
            yy = ypx(t)
            d.line([(left, yy), (W - right, yy)], fill="#E2E2E2", width=2)
            s = f"{t:.2f}" if step < 0.5 else f"{t:.1f}"
            d.text((left - 12 - d.textlength(s, font=f_tick), yy - 13), s,
                   fill="#444444", font=f_tick)
            t += step

        # Axes.
        d.line([(left, top), (left, H - bottom)], fill="#222222", width=3)
        d.line([(left, H - bottom), (W - right, H - bottom)], fill="#222222", width=3)

        # Red dashed threshold at UR = 1.0.
        y_limit = ypx(1.0)
        x = left
        while x < W - right:
            d.line([(x, y_limit), (min(x + 14, W - right), y_limit)], fill=red, width=4)
            x += 24
        note = "UR = 1.0 (limit)"
        d.text((W - right - d.textlength(note, font=f_note) - 6, y_limit - 32),
               note, fill=red, font=f_note)

        # Bars, value labels and wrapped x labels.
        slot = plot_w / len(nums)
        bar_w = min(150, slot * 0.55)
        for i, (num, label) in enumerate(zip(nums, labels)):
            cx = left + slot * (i + 0.5)
            bx0, bx1 = cx - bar_w / 2, cx + bar_w / 2
            by = ypx(num)
            color = red if num > 1.0 else green
            d.rectangle([bx0, by, bx1, H - bottom], fill=color,
                        outline="#333333", width=3)
            val_s = f"{num:.2f}"
            d.text((cx - d.textlength(val_s, font=f_value) / 2, by - 34),
                   val_s, fill=color, font=f_value)
            for li, line in enumerate(label.split("\n")):
                d.text((cx - d.textlength(line, font=f_label) / 2,
                        H - bottom + 18 + li * 30), line,
                       fill="#222222", font=f_label)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as exc:
        logging.getLogger(__name__).warning("UR summary chart failed: %s", exc)
        return None


# ── Task #5: Chapter 7 material quantity charts ────────────────────────────

def _chart_fonts():
    """Load the same font set used by the UR chart (with default-font fallback)."""
    from PIL import ImageFont
    import os

    path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arial.ttf")
    try:
        return {
            "title": ImageFont.truetype(path, 26),
            "tick": ImageFont.truetype(path, 20),
            "label": ImageFont.truetype(path, 22),
            "value": ImageFont.truetype(path, 22),
            "note": ImageFont.truetype(path, 19),
        }
    except OSError:  # pragma: no cover - fallback font
        f = ImageFont.load_default()
        return {k: f for k in ("title", "tick", "label", "value", "note")}


def _draw_quantity_panel(d, box, title, items, fonts, fmt="{:.2f}"):
    """Draw one bar-chart panel into ``box = (x0, y0, x1, y1)`` of a PIL canvas.

    ``items`` is a list of ``(label, value_or_None)``.  A ``None`` value is
    drawn as an empty outlined bar labelled ``N/A`` — never as zero.
    """
    x0, y0, x1, y1 = box
    pad_l, pad_r, pad_t, pad_b = 92, 24, 66, 92
    px0, px1 = x0 + pad_l, x1 - pad_r
    py0, py1 = y0 + pad_t, y1 - pad_b
    pw, ph = px1 - px0, py1 - py0
    nums = [float(v) for _, v in items if v is not None]
    ymax = max(1.0, max(nums) * 1.18) if nums else 1.0
    ypx = lambda v: py1 - ph * (v / ymax)

    # Units are stated in the LaTeX caption below the figure, not on the plot,
    # to keep the top y-tick label and the panel title from colliding.
    d.text((x0 + 12, y0 + 8), title, fill="#222222", font=fonts["title"])

    step = ymax / 4.0
    t = 0.0
    while t <= ymax + 1e-9:
        yy = ypx(t)
        d.line([(px0, yy), (px1, yy)], fill="#E2E2E2", width=2)
        s = f"{t:.2f}"
        d.text((px0 - 10 - d.textlength(s, font=fonts["tick"]), yy - 12), s,
               fill="#444444", font=fonts["tick"])
        t += step
    d.line([(px0, py0), (px0, py1)], fill="#222222", width=3)
    d.line([(px0, py1), (px1, py1)], fill="#222222", width=3)

    slot = pw / len(items)
    bar_w = min(130, slot * 0.55)
    green, red = "#" + styles.OSDAG_GREEN_HEX, "#" + styles.FAIL_RED_HEX
    for i, (label, value) in enumerate(items):
        cx = px0 + slot * (i + 0.5)
        bx0, bx1 = cx - bar_w / 2, cx + bar_w / 2
        if value is None:
            top = ypx(ymax * 0.72)
            d.rectangle([bx0, top, bx1, py1], outline="#9A9A9A", width=3)
            val_s = "N/A"
            color = "#777777"
        else:
            num = float(value)
            top = ypx(num)
            d.rectangle([bx0, top, bx1, py1], fill=green, outline="#333333", width=3)
            val_s = fmt.format(num)
            color = green
        d.text((cx - d.textlength(val_s, font=fonts["value"]) / 2, top - 32),
               val_s, fill=color, font=fonts["value"])
        for li, line in enumerate(label.split("\n")):
            d.text((cx - d.textlength(line, font=fonts["label"]) / 2,
                    py1 + 16 + li * 28), line, fill="#222222", font=fonts["label"])


def steel_tonnage_chart(values):
    """PNG bytes: structural steel tonnage (MT) by element.

    ``values`` is an ordered mapping ``{label: MT or None}``; ``None`` renders
    as an outlined N/A bar (no invented number).
    """
    if not values:
        return None
    try:
        import io
        import logging

        from PIL import Image, ImageDraw

        fonts = _chart_fonts()
        img = Image.new("RGB", (1400, 700), "white")
        d = ImageDraw.Draw(img)
        _draw_quantity_panel(
            d, (0, 0, 1400, 700), "Structural Steel Tonnage by Element",
            list(values.items()), fonts,
        )
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as exc:
        logging.getLogger(__name__).warning("Steel tonnage chart failed: %s", exc)
        return None


def concrete_rebar_chart(concrete_m3, rebar_mt):
    """PNG bytes: concrete volume (m³) and rebar weight (MT) in two panels.

    Separate panels with independent scales — unlike units are never plotted
    on a shared Y axis.  ``None`` values render as N/A bars.
    """
    try:
        import io
        import logging

        from PIL import Image, ImageDraw

        fonts = _chart_fonts()
        img = Image.new("RGB", (1400, 700), "white")
        d = ImageDraw.Draw(img)
        d.line([(700, 20), (700, 680)], fill="#C8C8C8", width=2)
        _draw_quantity_panel(
            d, (0, 0, 700, 700), "Concrete Volume",
            [("Deck Slab", concrete_m3)], fonts,
        )
        _draw_quantity_panel(
            d, (700, 0, 1400, 700), "Reinforcement Steel",
            [("Deck Rebar", rebar_mt)], fonts,
        )
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as exc:
        logging.getLogger(__name__).warning("Concrete/rebar chart failed: %s", exc)
        return None


