"""Client Cyber Risk Dashboard — Streamlit app.

Run:  uv run streamlit run app.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

import altair as alt
import duckdb
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from cyber_risk import pipeline, queries  # noqa: E402

DB_PATH = Path(os.environ.get("CYBER_RISK_DB", ROOT / "data" / "cyber_risk.duckdb"))
SAMPLE_PATH = ROOT / "data" / "sample" / "oab_cyber_risks_2_5mb.csv.zip"
AUTOLOAD_SAMPLE = os.environ.get("AUTOLOAD_SAMPLE", "true").lower() == "true"
DB_LOCK_WAIT_SECONDS = int(os.environ.get("DB_LOCK_WAIT_SECONDS", "60"))
ALL_BU = "ทั้งหมด (All Business Units)"

# VIZ_DESIGN_SPEC.md — Palette. No red/yellow/green for risk score: no
# approved thresholds exist, so colour must not imply severity.
PRIMARY = "#1F4E79"
SECONDARY = "#5B6573"
MUTED = "#CBD2D9"
TEXT = "#1F2933"

st.set_page_config(page_title="Client Cyber Risk Dashboard", layout="wide")


@st.cache_resource
def get_connection():
    """Open the DuckDB file, waiting while another process holds its lock.

    DuckDB allows one writer process per file. During a rolling redeploy the
    new container starts before the old one stops, so retry instead of failing.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + DB_LOCK_WAIT_SECONDS
    while True:
        try:
            return pipeline.connect(DB_PATH)
        except duckdb.IOException as exc:
            if "lock" not in str(exc).lower() or time.monotonic() > deadline:
                raise
            time.sleep(2)


con = get_connection()


def run_ingest(path: Path, name: str) -> None:
    result = pipeline.ingest(con, path, source_name=name)
    st.session_state["last_ingest"] = result


# First run: load the bundled sample so the dashboard is never empty.
if (
    AUTOLOAD_SAMPLE
    and queries.current_snapshot(con) is None
    and SAMPLE_PATH.exists()
    and "last_ingest" not in st.session_state
):
    run_ingest(SAMPLE_PATH, SAMPLE_PATH.name)


# --- Sidebar: data load & validation ----------------------------------------

with st.sidebar:
    st.header("นำเข้าข้อมูล")
    uploaded = st.file_uploader("อัปโหลด CSV (หรือ .zip ที่มี CSV)", type=["csv", "zip"])
    if st.button("ตรวจสอบและบันทึกลง DuckDB", type="primary", disabled=uploaded is None):
        suffix = Path(uploaded.name).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(uploaded.getvalue())
        run_ingest(Path(tmp.name), uploaded.name)
    if st.button("โหลดไฟล์ตัวอย่างใหม่", disabled=not SAMPLE_PATH.exists()):
        run_ingest(SAMPLE_PATH, SAMPLE_PATH.name)

    history = queries.snapshot_history(con, limit=1)
    if not history.empty:
        latest = history.iloc[0]
        st.subheader("ผลการตรวจสอบล่าสุด")
        st.caption(f"{latest.source_name} · {latest.snapshot_at:%Y-%m-%d %H:%M:%S}")
        if latest.publication_status == "published":
            st.success(f"Published · {int(latest.source_row_count):,} rows")
        else:
            st.error("Failed — ไม่ถูก publish; dashboard ยังแสดง snapshot ก่อนหน้า")
        if isinstance(latest.message, str):
            st.caption(latest.message)
        rules = queries.dq_results(con, latest.snapshot_at)
        rules["result"] = rules.passed.map({True: "PASS", False: "FAIL"})
        st.dataframe(
            rules[["rule_id", "rule_name", "severity", "failed_count", "result"]],
            hide_index=True,
            width="stretch",
        )
        bad = queries.quarantined(con, latest.snapshot_at)
        if not bad.empty:
            with st.expander(f"Quarantined records ({len(bad)})"):
                st.dataframe(bad, hide_index=True, width="stretch")

    with st.expander("Snapshot history"):
        st.dataframe(queries.snapshot_history(con), hide_index=True, width="stretch")


# --- Header & filter ----------------------------------------------------------

st.title("Client Cyber Risk Dashboard")

snapshot_at = queries.current_snapshot(con)
if snapshot_at is None:
    st.info("ยังไม่มี snapshot ที่ผ่านการตรวจสอบ — อัปโหลด CSV จาก sidebar")
    st.stop()

units = queries.business_units(con)
options = [ALL_BU, *units.business_unit_name]
selected = st.selectbox("หน่วยงาน (Business Unit)", options, key="bu_filter")
bu_key = (
    None
    if selected == ALL_BU
    else int(units.loc[units.business_unit_name == selected, "business_unit_key"].iloc[0])
)
context = f"Business Unit: {selected} · Snapshot: {snapshot_at:%Y-%m-%d %H:%M:%S}"
st.caption(f"Data last updated: {snapshot_at:%Y-%m-%d %H:%M:%S} · Business Unit: {selected}")



def bu_bar_chart(df, value, x_title, label, tooltip, description, x_max=None):
    """Horizontal Business Unit bar, sorted by `value` desc, selected BU emphasised.

    Selection is marked by colour *and* a text marker (VIZ_DESIGN_SPEC.md
    Color Independence).
    """
    df = df.sort_values([value, "business_unit_name"], ascending=[False, True]).copy()
    df["selected"] = df.business_unit_name == selected
    df["label"] = df.apply(lambda r: label(r) + ("  ◀ เลือกอยู่" if r.selected else ""), axis=1)
    has_selection = bu_key is not None
    x_max = x_max if x_max is not None else max(1, df[value].max()) * 1.5
    base = alt.Chart(df).encode(
        y=alt.Y("business_unit_name:N", sort=list(df.business_unit_name), title=None),
        x=alt.X(f"{value}:Q", title=x_title, scale=alt.Scale(domain=[0, x_max])),
        tooltip=tooltip,
    )
    bars = base.mark_bar().encode(
        color=alt.condition(
            alt.datum.selected if has_selection else alt.datum[value] >= 0,
            alt.value(PRIMARY),
            alt.value(MUTED),
        )
    )
    labels = base.mark_text(align="left", dx=4, color=TEXT).encode(text="label:N")
    return (bars + labels).properties(height=320, description=description)


# --- KPI cards ------------------------------------------------------------------

counts = queries.risk_counts(con, bu_key)
c1, c2, c3 = st.columns(3)
c1.metric("ความเสี่ยงทั้งหมด", f"{counts.total:,}")
c2.metric("ปิดแล้ว", f"{counts.closed:,}")
c3.metric(
    "ยังไม่ปิด",
    f"{counts.unresolved:,}",
    help="Unresolved Risk = status != 'closed' (รวม open และ in_progress)",
)


# --- Charts -------------------------------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("ความเสี่ยงที่ยังไม่ปิด แยกตามหน่วยงาน")
    by_bu = queries.unresolved_by_business_unit(con)
    chart = bu_bar_chart(
        by_bu,
        value="unresolved_risk_count",
        x_title="จำนวน Unresolved Risk",
        label=lambda r: f"{r.unresolved_risk_count:,} ({r.unresolved_risk_share:.1f}%)",
        tooltip=[
            alt.Tooltip("business_unit_name:N", title="Business Unit"),
            alt.Tooltip("unresolved_risk_count:Q", title="Unresolved Risk Count", format=","),
            alt.Tooltip("unresolved_risk_share:Q", title="Unresolved Risk Share (%)", format=".2f"),
            alt.Tooltip("total_unresolved_risk_count:Q", title="Total Unresolved", format=","),
        ],
        description="จำนวน Unresolved Risk แยกตาม Business Unit เรียงจากมากไปน้อย ณ snapshot ล่าสุด",
    )
    st.altair_chart(chart, width="stretch")
    st.caption(
        "เรียงจากมากไปน้อย · ตัวเลขในวงเล็บคือสัดส่วนต่อ Unresolved Risk ทั้งองค์กร "
        "(METRIC-02) · กราฟนี้แสดงทุกหน่วยงานเสมอเพื่อใช้เปรียบเทียบ"
    )

with right:
    st.subheader("ความเสี่ยงที่ยังไม่ปิด แยกตามระดับความเสี่ยง")
    by_score = queries.unresolved_by_priority_score(con, bu_key)
    score_order = [int(s) for s in by_score.risk_priority_score]
    sbase = alt.Chart(by_score).encode(
        y=alt.Y(
            "risk_priority_score:O",
            sort=score_order,
            title="Risk Priority Score (likelihood × impact)",
        ),
        x=alt.X("unresolved_risk_count:Q", title="จำนวน Unresolved Risk", scale=alt.Scale(domain=[0, max(1, by_score.unresolved_risk_count.max()) * 1.2])),
        tooltip=[
            alt.Tooltip("risk_priority_score:O", title="Risk Priority Score"),
            alt.Tooltip("unresolved_risk_count:Q", title="Unresolved Risk Count", format=","),
        ],
    )
    schart = (
        sbase.mark_bar(color=PRIMARY)
        + sbase.mark_text(align="left", dx=4, color=TEXT).encode(
            text=alt.Text("unresolved_risk_count:Q", format=",")
        )
    ).properties(
        height=max(320, 26 * len(by_score)),
        description=f"จำนวน Unresolved Risk แยกตาม Risk Priority Score · {context}",
    )
    st.altair_chart(schart, width="stretch")
    st.caption(
        f"{selected} · ระดับความเสี่ยง = Risk Priority Score = likelihood × impact "
        "(ตามเกณฑ์ที่ management อนุมัติ ยังไม่มีการแบ่งกลุ่ม Low/Medium/High/Critical)"
    )


# --- Top 3 ----------------------------------------------------------------------

st.subheader("Top 3 ความเสี่ยงที่ควรติดตาม")
top = queries.top_risks(con, bu_key)
if top.empty:
    st.info("ไม่มีความเสี่ยงที่ยังไม่ปิดใน filter นี้")
else:
    show = top.rename(
        columns={
            "follow_up_rank": "อันดับ",
            "risk_title": "ชื่อความเสี่ยง",
            "risk_priority_score": "คะแนน",
            "owner_id": "ผู้รับผิดชอบ",
            "business_unit_name": "หน่วยงาน",
        }
    )[["อันดับ", "ชื่อความเสี่ยง", "คะแนน", "ผู้รับผิดชอบ", "หน่วยงาน"]]
    st.dataframe(
        show,
        hide_index=True,
        width="stretch",
        column_config={
            "อันดับ": st.column_config.NumberColumn(width="small"),
            "ชื่อความเสี่ยง": st.column_config.TextColumn(width="large"),
            "คะแนน": st.column_config.NumberColumn(width="small"),
        },
    )
    top_score, ties = queries.tie_count_at_top(con, bu_key)
    note = "เรียงตาม คะแนน มาก→น้อย; คะแนนเท่ากันใช้ risk_id น้อย→มาก เป็น technical tie-break เท่านั้น"
    if ties > 3:
        note += f" · มี {ties:,} รายการที่คะแนน {top_score} เท่ากัน — ลำดับในกลุ่มนี้ไม่ได้สะท้อน business priority"
    st.caption(f"{context} · {note}")


# --- Risk management progress (METRIC-06, METRIC-07) -----------------------------

st.subheader("ความคืบหน้าการจัดการความเสี่ยงรายหน่วยงาน")
status_bu = queries.status_by_business_unit(con)
p_left, p_right = st.columns(2)

with p_left:
    st.markdown("**สัดส่วนความเสี่ยงที่ปิดแล้ว**")
    st.altair_chart(
        bu_bar_chart(
            status_bu,
            value="closed_risk_ratio",
            x_title="% ปิดแล้ว (closed ÷ ทั้งหมด)",
            label=lambda r: f"{r.closed_risk_ratio:.1f}% ({r.closed_risk_count:,}/{r.total_risk_count:,})",
            tooltip=[
                alt.Tooltip("business_unit_name:N", title="Business Unit"),
                alt.Tooltip("closed_risk_ratio:Q", title="Closed Risk Ratio (%)", format=".1f"),
                alt.Tooltip("closed_risk_count:Q", title="Closed", format=","),
                alt.Tooltip("total_risk_count:Q", title="Total", format=","),
            ],
            description="สัดส่วนความเสี่ยงที่ปิดแล้วต่อทั้งหมด แยกตาม Business Unit ณ snapshot ล่าสุด",
            x_max=100 * 1.4,
        ),
        width="stretch",
    )
    st.caption(
        "METRIC-06 · สถานะสะสม ณ snapshot นี้ ไม่ใช่ความเร็วในการปิด (source ไม่มีวันที่) · "
        "แสดงทุกหน่วยงานเสมอเพื่อเปรียบเทียบ"
    )

with p_right:
    st.markdown("**ความเสี่ยงที่ยังไม่ปิด และยังไม่เริ่มดำเนินการ (open)**")
    started = status_bu.dropna(subset=["not_started_share"])
    st.altair_chart(
        bu_bar_chart(
            started,
            value="not_started_share",
            x_title="% open ÷ ยังไม่ปิด",
            label=lambda r: f"{r.not_started_share:.1f}% ({r.not_started_risk_count:,}/{r.unresolved_risk_count:,})",
            tooltip=[
                alt.Tooltip("business_unit_name:N", title="Business Unit"),
                alt.Tooltip("not_started_share:Q", title="Not Started Share (%)", format=".1f"),
                alt.Tooltip("not_started_risk_count:Q", title="Open", format=","),
                alt.Tooltip("unresolved_risk_count:Q", title="Unresolved", format=","),
            ],
            description="สัดส่วนความเสี่ยงที่ยังไม่ปิดซึ่งยังมีสถานะ open แยกตาม Business Unit ณ snapshot ล่าสุด",
            x_max=100 * 1.4,
        ),
        width="stretch",
    )
    st.caption(
        "METRIC-07 · ส่วนที่เหลือคือ in_progress · นิยาม open = ยังไม่เริ่มดำเนินการ "
        "รอ management ยืนยัน"
    )


# --- Risk matrix (METRIC-08) --------------------------------------------------------

st.subheader("Risk Matrix: Likelihood × Impact (ความเสี่ยงที่ยังไม่ปิด)")
matrix = queries.risk_matrix(con, bu_key)
grid = matrix.pivot(index="likelihood", columns="impact", values="unresolved_risk_count")
grid = grid.sort_index(ascending=False)
grid.columns = [f"Impact {c}" for c in grid.columns]
grid = grid.reset_index().rename(columns={"likelihood": "Likelihood"})
grid["Likelihood"] = grid["Likelihood"].map(lambda v: f"Likelihood {v}")
st.dataframe(
    grid,
    hide_index=True,
    width="stretch",
    column_config={c: st.column_config.NumberColumn(format="%d") for c in grid.columns[1:]},
)
st.caption(
    f"METRIC-08 · {context} · แต่ละช่อง = จำนวน Unresolved Risk · Risk Priority Score = "
    "likelihood × impact (เช่น L5×I2 และ L2×I5 ได้ 10 เท่ากัน แต่ต่างกันที่โอกาสเกิด/ผลกระทบ) · "
    "แสดงเป็นตารางตัวเลข ไม่ใช้สีแทนระดับ เพราะยังไม่มีเกณฑ์ระดับที่อนุมัติ"
)


# --- Drill-down: score -> risk detail ---------------------------------------------

with st.expander("รายละเอียดความเสี่ยงที่ยังไม่ปิด (drill-down ตามคะแนน)"):
    score_choice = st.selectbox(
        "Risk Priority Score", ["ทั้งหมด", *score_order], key="score_filter"
    )
    detail = queries.risk_detail(con, bu_key, None if score_choice == "ทั้งหมด" else int(score_choice))
    st.caption(f"{len(detail):,} รายการ · {context}")
    st.dataframe(
        detail.rename(
            columns={
                "risk_title": "ชื่อความเสี่ยง",
                "business_unit_name": "หน่วยงาน",
                "risk_priority_score": "คะแนน",
                "owner_id": "ผู้รับผิดชอบ",
            }
        ),
        hide_index=True,
        width="stretch",
    )
