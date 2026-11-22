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


