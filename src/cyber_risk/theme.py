"""Visual theme for the dashboard — tokens from VIZ_DESIGN_SPEC.md.

Colour is used for structure (primary vs. muted), never to encode risk
severity: no approved thresholds exist, so there is no red/amber/green.
"""

from __future__ import annotations

from html import escape

import altair as alt

PRIMARY = "#1F4E79"
SECONDARY = "#5B6573"
ACCENT = "#2F75B5"
BACKGROUND = "#FFFFFF"
SURFACE = "#F5F7F9"
TEXT_PRIMARY = "#1F2933"
TEXT_SECONDARY = "#52606D"
BORDER = "#CBD2D9"
MUTED_BAR = "#CBD2D9"
GRID = "#E9EDF1"

FONT = "IBM Plex Sans Thai"
FONT_STACK = f"'{FONT}', 'Noto Sans Thai', system-ui, sans-serif"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600&display=swap');

:root {{
  --primary: {PRIMARY};
  --accent: {ACCENT};
  --surface: {SURFACE};
  --text: {TEXT_PRIMARY};
  --text-2: {TEXT_SECONDARY};
  --border: {BORDER};
  --grid: {GRID};
}}

html, body, .stApp, .stApp p, .stApp li, .stApp label, .stApp input,
.stApp textarea, .stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp td, .stApp th, .stMarkdown, [data-testid="stMetricValue"] {{
  font-family: {FONT_STACK};
}}

.block-container {{ padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1280px; }}

/* Header */
.dash-header h1 {{
  font-size: 22px; font-weight: 600; color: var(--text);
  margin: 0; padding: 0; line-height: 1.3;
}}
.dash-header p {{ margin: 2px 0 0; color: var(--text-2); font-size: 14px; }}
.meta-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 4px; }}
.pill {{
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 999px; padding: 3px 12px; font-size: 13px; color: var(--text-2);
}}
.pill b {{ color: var(--text); font-weight: 500; }}

/* Section titles */
.section-title {{
  font-size: 17px; font-weight: 600; color: var(--text);
  margin: 28px 0 10px; padding-bottom: 6px; border-bottom: 1px solid var(--grid);
}}
.chart-title {{ font-size: 15px; font-weight: 600; color: var(--text); margin: 0 0 2px; }}
.chart-sub {{ font-size: 13px; color: var(--text-2); margin: 0 0 8px; }}
.note {{ font-size: 12.5px; color: var(--text-2); margin: 6px 0 0; line-height: 1.55; }}

/* KPI cards */
.kpi-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }}
@media (max-width: 760px) {{ .kpi-grid {{ grid-template-columns: 1fr; }} }}
.kpi {{
  background: {BACKGROUND}; border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 18px 16px;
}}
.kpi.primary {{ border-top: 3px solid var(--primary); }}
.kpi .label {{ font-size: 13px; color: var(--text-2); font-weight: 500; }}
.kpi .value {{ font-size: 30px; font-weight: 600; color: var(--text); line-height: 1.25; margin-top: 2px; }}
.kpi .sub {{ font-size: 13px; color: var(--text-2); margin-top: 4px; }}
.kpi .bar {{ display: flex; height: 6px; border-radius: 3px; overflow: hidden; background: var(--grid); margin-top: 10px; }}
.kpi .bar span {{ display: block; height: 100%; }}

/* Tables */
table.dash {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
table.dash caption {{ text-align: left; font-size: 12.5px; color: var(--text-2); caption-side: bottom; padding-top: 8px; }}
table.dash th {{
  text-align: left; font-weight: 500; font-size: 12.5px; color: var(--text-2);
  padding: 8px 10px; border-bottom: 1px solid var(--border); background: var(--surface);
}}
table.dash td {{ padding: 10px; border-bottom: 1px solid var(--grid); color: var(--text); vertical-align: top; }}
table.dash td.num, table.dash th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.rank {{
  display: inline-flex; width: 26px; height: 26px; border-radius: 50%;
  align-items: center; justify-content: center; font-weight: 600; font-size: 13px;
  background: var(--primary); color: #fff;
}}
.risk-title {{ font-weight: 500; }}
.risk-meta {{ font-size: 12.5px; color: var(--text-2); margin-top: 2px; }}
.score {{ font-weight: 600; font-size: 16px; }}
.score small {{ display: block; font-weight: 400; font-size: 12px; color: var(--text-2); white-space: nowrap; }}
table.dash th, table.dash td.owner {{ white-space: nowrap; }}

table.matrix th, table.matrix td {{ text-align: center; }}
table.matrix th[scope="row"] {{ text-align: left; white-space: nowrap; }}
table.matrix td {{ padding: 8px 6px; }}
table.matrix td .n {{ display: block; font-size: 16px; font-weight: 600; font-variant-numeric: tabular-nums; }}
table.matrix td .s {{ display: block; font-size: 12px; color: var(--text-2); }}
table.matrix td.zero .n {{ color: var(--text-2); font-weight: 400; }}

/* Bar list (horizontal bars rendered as HTML: responsive, never clipped) */
.barlist {{ display: flex; flex-direction: column; gap: 9px; margin: 6px 0 2px; }}
.bl-row {{ display: grid; grid-template-columns: minmax(92px, 132px) minmax(28px, 1fr) 80px; align-items: center; gap: 8px; }}
.bl-label {{ font-size: 13px; color: var(--text); line-height: 1.3; overflow-wrap: break-word; }}
.bl-row.sel .bl-label {{ font-weight: 600; }}
.bl-track {{ height: 14px; background: var(--surface); border-radius: 3px; overflow: hidden; }}
.bl-track span {{ display: block; height: 100%; border-radius: 0 3px 3px 0; }}
.bl-value {{ font-size: 13px; color: var(--text); font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; line-height: 1.25; min-width: 52px; }}
.bl-value small {{ display: block; color: var(--text-2); font-size: 12px; }}
.bl-tag {{ display: block; font-size: 11.5px; color: var(--primary); font-weight: 600; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: var(--surface); }}
.status {{ display: inline-block; font-size: 12.5px; font-weight: 600; padding: 2px 10px; border-radius: 999px; }}
.status.published {{ background: #E6EEF6; color: var(--primary); }}
.status.failed {{ background: #F2F4F7; color: var(--text); border: 1px solid var(--text-2); }}
</style>
"""


def altair_theme() -> dict:
    """Altair config: calm axes, ≥12px labels, no chart border."""
    return {
        "config": {
            "font": FONT_STACK,
            "view": {"stroke": None},
            "background": BACKGROUND,
            "axis": {
                "labelFont": FONT_STACK,
                "titleFont": FONT_STACK,
                "labelFontSize": 12,
                "titleFontSize": 12,
                "titleFontWeight": 500,
                "labelColor": TEXT_SECONDARY,
                "titleColor": TEXT_SECONDARY,
                "gridColor": GRID,
                "domain": False,
                "ticks": False,
                "labelPadding": 6,
            },
            "axisY": {"grid": False},
            "text": {"font": FONT_STACK, "fontSize": 12, "color": TEXT_PRIMARY},
            "bar": {"cornerRadiusEnd": 3},
        }
    }


def register_altair_theme() -> None:
    @alt.theme.register("cyber_risk", enable=True)
    def _theme():
        return alt.theme.ThemeConfig(altair_theme())


def section(title: str) -> str:
    return f'<div class="section-title">{escape(title)}</div>'


def chart_heading(title: str, sub: str | None = None) -> str:
    html = f'<div class="chart-title">{escape(title)}</div>'
    if sub:
        html += f'<div class="chart-sub">{escape(sub)}</div>'
    return html


def note(text: str) -> str:
    return f'<div class="note">{escape(text)}</div>'


def header(title: str, subtitle: str) -> str:
    return (
        f'<div class="dash-header"><h1>{escape(title)}</h1>'
        f"<p>{escape(subtitle)}</p></div>"
    )


def meta_pills(items: list[tuple[str, str]]) -> str:
    pills = "".join(
        f'<span class="pill">{escape(k)} <b>{escape(v)}</b></span>' for k, v in items
    )
    return f'<div class="meta-row">{pills}</div>'


def kpi_cards(total: int, closed: int, unresolved: int, open_n: int, in_progress: int) -> str:
    def pct(n: int, d: int) -> float:
        return 100.0 * n / d if d else 0.0

    closed_pct = pct(closed, total)
    unresolved_pct = pct(unresolved, total)
    return f"""
<div class="kpi-grid" role="group" aria-label="สรุปจำนวนความเสี่ยง">
  <div class="kpi">
    <div class="label">ความเสี่ยงทั้งหมด</div>
    <div class="value">{total:,}</div>
    <div class="sub">ทุกสถานะ ใน snapshot นี้</div>
  </div>
  <div class="kpi">
    <div class="label">ปิดแล้ว</div>
    <div class="value">{closed:,}</div>
    <div class="sub">{closed_pct:.1f}% ของทั้งหมด</div>
    <div class="bar" aria-hidden="true"><span style="width:{closed_pct:.2f}%;background:{SECONDARY}"></span></div>
  </div>
  <div class="kpi primary">
    <div class="label">ยังไม่ปิด (status ≠ closed)</div>
    <div class="value">{unresolved:,}</div>
    <div class="sub">{unresolved_pct:.1f}% ของทั้งหมด · open {open_n:,} · in_progress {in_progress:,}</div>
    <div class="bar" aria-hidden="true"><span style="width:{unresolved_pct:.2f}%;background:{PRIMARY}"></span></div>
  </div>
</div>
"""


def top_risks_table(rows, show_bu: bool, caption: str) -> str:
    head = (
        '<tr><th scope="col">อันดับ</th><th scope="col">ชื่อความเสี่ยง</th>'
        '<th scope="col" class="num">คะแนน</th><th scope="col">ผู้รับผิดชอบ</th></tr>'
    )
    body = []
    for r in rows.itertuples():
        meta = f"{escape(r.risk_id)}" + (f" · {escape(str(r.business_unit_name))}" if show_bu else "")
        body.append(
            "<tr>"
            f'<td><span class="rank" aria-label="อันดับ {r.follow_up_rank}">{r.follow_up_rank}</span></td>'
            f'<td><div class="risk-title">{escape(r.risk_title)}</div><div class="risk-meta">{meta}</div></td>'
            f'<td class="num"><div class="score">{r.risk_priority_score}'
            f"<small>L{r.likelihood} × I{r.impact}</small></div></td>"
            f"<td class=\"owner\">{escape(str(r.owner_id or '—'))}</td>"
            "</tr>"
        )
    return (
        f'<table class="dash"><caption>{escape(caption)}</caption>'
        f"<thead>{head}</thead><tbody>{''.join(body)}</tbody></table>"
    )


def matrix_table(matrix, caption: str) -> str:
    impacts = sorted(matrix.impact.unique())
    likelihoods = sorted(matrix.likelihood.unique(), reverse=True)
    cell = {(r.likelihood, r.impact): r.unresolved_risk_count for r in matrix.itertuples()}
    head = '<tr><th scope="col">Likelihood \\ Impact</th>' + "".join(
        f'<th scope="col">Impact {i}</th>' for i in impacts
    ) + "</tr>"
    body = []
    for lk in likelihoods:
        tds = []
        for im in impacts:
            n = int(cell.get((lk, im), 0))
            cls = ' class="zero"' if n == 0 else ""
            tds.append(f'<td{cls}><span class="n">{n:,}</span><span class="s">คะแนน {lk * im}</span></td>')
        body.append(f'<tr><th scope="row">Likelihood {lk}</th>{"".join(tds)}</tr>')
    return (
        f'<table class="dash matrix"><caption>{escape(caption)}</caption>'
        f"<thead>{head}</thead><tbody>{''.join(body)}</tbody></table>"
    )


def bar_list(rows, max_value: float, description: str, has_selection: bool) -> str:
    """Horizontal bars as HTML.

    rows: iterable of (label, value, value_text, detail_text, selected).
    Selected row is marked by colour *and* text ("เลือกอยู่").
    """
    items = []
    for label, value, value_text, detail, sel in rows:
        width = 0 if not max_value else max(0.0, min(100.0, 100.0 * value / max_value))
        colour = PRIMARY if (sel or not has_selection) else MUTED_BAR
        tag = '<span class="bl-tag">◀ เลือกอยู่</span>' if sel else ""
        detail_html = f"<small>{escape(detail)}</small>" if detail else ""
        items.append(
            f'<div class="bl-row{" sel" if sel else ""}" role="listitem" '
            f'aria-label="{escape(label)}: {escape(value_text)} {escape(detail or "")}">'
            f'<div class="bl-label" title="{escape(label)}">{escape(label)}</div>'
            f'<div class="bl-track" aria-hidden="true"><span style="width:{width:.2f}%;background:{colour}"></span></div>'
            f'<div class="bl-value">{escape(value_text)}{detail_html}{tag}</div>'
            "</div>"
        )
    return f'<div class="barlist" role="list" aria-label="{escape(description)}">{"".join(items)}</div>'
