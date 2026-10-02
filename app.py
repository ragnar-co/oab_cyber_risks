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

from cyber_risk import pipeline, queries, theme  # noqa: E402

DB_PATH = Path(os.environ.get("CYBER_RISK_DB", ROOT / "data" / "cyber_risk.duckdb"))
SAMPLE_PATH = ROOT / "data" / "sample" / "oab_cyber_risks_2_5mb.csv.zip"
AUTOLOAD_SAMPLE = os.environ.get("AUTOLOAD_SAMPLE", "true").lower() == "true"
DB_LOCK_WAIT_SECONDS = int(os.environ.get("DB_LOCK_WAIT_SECONDS", "60"))
ALL_BU = "ทุกหน่วยงาน"

st.set_page_config(page_title="Client Cyber Risk Dashboard", layout="wide")
st.html(theme.CSS)
theme.register_altair_theme()


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
        status = latest.publication_status
        rows = f" · {int(latest.source_row_count):,} rows" if pd.notna(latest.source_row_count) else ""
        st.html(f'<span class="status {status}">{status.upper()}</span>')
        st.caption(f"{latest.source_name} · {latest.snapshot_at:%Y-%m-%d %H:%M:%S}{rows}")
        if status != "published":
            st.error("ไม่ถูก publish — dashboard ยังแสดง snapshot ก่อนหน้า")
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

snapshot_at = queries.current_snapshot(con)

head_left, head_right = st.columns([3, 1.4], vertical_alignment="bottom")
with head_left:
    st.html(
        theme.header(
            "Client Cyber Risk Dashboard",
            "ภาพรวมความเสี่ยงด้าน cyber ที่ยังไม่ปิด สำหรับการติดตามของผู้บริหาร",
        )
    )

if snapshot_at is None:
    st.info("ยังไม่มี snapshot ที่ผ่านการตรวจสอบ — อัปโหลด CSV จาก sidebar")
    st.stop()

units = queries.business_units(con)
options = [ALL_BU, *units.business_unit_name]
# ?bu=<Business Unit> preselects the filter so a filtered view can be shared.
if "bu_filter" not in st.session_state:
    requested = st.query_params.get("bu")
    st.session_state["bu_filter"] = requested if requested in options else ALL_BU
with head_right:
    selected = st.selectbox("หน่วยงาน (Business Unit)", options, key="bu_filter")
if selected == ALL_BU:
    st.query_params.pop("bu", None)
else:
    st.query_params["bu"] = selected
bu_key = (
    None
    if selected == ALL_BU
    else int(units.loc[units.business_unit_name == selected, "business_unit_key"].iloc[0])
)
snapshot_label = f"{snapshot_at:%Y-%m-%d %H:%M:%S}"
context = f"Business Unit: {selected} · Snapshot: {snapshot_label}"
st.html(
    theme.meta_pills(
        [
            ("Data last updated", snapshot_label),
            ("หน่วยงาน", selected),
        ]
    )
)


# --- KPI cards ------------------------------------------------------------------

counts = queries.risk_counts(con, bu_key)
status_bu = queries.status_by_business_unit(con)
scope = status_bu if bu_key is None else status_bu[status_bu.business_unit_key == bu_key]
open_n = int(scope.not_started_risk_count.sum())
st.html(
    theme.kpi_cards(
        total=counts.total,
        closed=counts.closed,
        unresolved=counts.unresolved,
        open_n=open_n,
        in_progress=counts.unresolved - open_n,
    )
)


# --- Charts helpers -------------------------------------------------------------


def bu_bars(df, value, value_text, detail, description, max_value=None):
    """Business Unit bars sorted by `value` desc; selected BU highlighted."""
    df = df.sort_values([value, "business_unit_name"], ascending=[False, True])
    rows = [
        (r.business_unit_name, float(r[value]), value_text(r), detail(r), r.business_unit_name == selected)
        for _, r in df.iterrows()
    ]
    top = max_value if max_value is not None else (df[value].max() if len(df) else 0)
    st.html(theme.bar_list(rows, float(top or 0), description, has_selection=bu_key is not None))


# --- Section: concentration -------------------------------------------------------

st.html(theme.section("การกระจุกตัวของความเสี่ยงที่ยังไม่ปิด"))
left, right = st.columns(2, gap="medium")

with left, st.container(border=True):
    st.html(theme.chart_heading("แยกตามหน่วยงาน", "จำนวน (สัดส่วนต่อทั้งองค์กร) · เรียงมาก→น้อย"))
    bu_bars(
        queries.unresolved_by_business_unit(con),
        value="unresolved_risk_count",
        value_text=lambda r: f"{r.unresolved_risk_count:,}",
        detail=lambda r: f"{r.unresolved_risk_share:.1f}%",
        description="จำนวน Unresolved Risk แยกตาม Business Unit เรียงจากมากไปน้อย ณ snapshot ล่าสุด",
    )
    st.html(theme.note("แสดงทุกหน่วยงานเสมอเพื่อเปรียบเทียบ · METRIC-01, METRIC-02"))

with right, st.container(border=True):
    st.html(
        theme.chart_heading(
            "แยกตามระดับความเสี่ยง",
            f"Risk Priority Score = likelihood × impact · {selected}",
        )
    )
    by_score = queries.unresolved_by_priority_score(con, bu_key)
    score_order = [int(s) for s in by_score.risk_priority_score]
    sbase = alt.Chart(by_score).encode(
        y=alt.Y(
            "risk_priority_score:O",
            sort=score_order,
            title="คะแนน",
            axis=alt.Axis(labelColor=theme.TEXT_PRIMARY, labelOverlap=False),
        ),
        x=alt.X(
            "unresolved_risk_count:Q",
            title="จำนวน Unresolved Risk",
            scale=alt.Scale(domain=[0, max(1, by_score.unresolved_risk_count.max()) * 1.2]),
            axis=alt.Axis(tickCount=4),
        ),
        tooltip=[
            alt.Tooltip("risk_priority_score:O", title="Risk Priority Score"),
            alt.Tooltip("unresolved_risk_count:Q", title="Unresolved Risk Count", format=","),
        ],
    )
    st.altair_chart(
        (
            sbase.mark_bar(color=theme.PRIMARY, height={"band": 0.62})
            + sbase.mark_text(align="left", dx=6).encode(text=alt.Text("unresolved_risk_count:Q", format=","))
        ).properties(
            height=max(300, 26 * len(by_score)),
            description=f"จำนวน Unresolved Risk แยกตาม Risk Priority Score · {context}",
        ),
        width="stretch",
    )
    st.html(theme.note("ใช้คะแนนโดยตรง ยังไม่มีการแบ่งกลุ่ม Low/Medium/High/Critical ที่อนุมัติ · METRIC-04"))


# --- Section: Top 3 ----------------------------------------------------------------

st.html(theme.section("Top 3 ความเสี่ยงที่ควรติดตาม"))
top = queries.top_risks(con, bu_key)
with st.container(border=True):
    if top.empty:
        st.info("ไม่มีความเสี่ยงที่ยังไม่ปิดใน filter นี้")
    else:
        top_score, ties = queries.tie_count_at_top(con, bu_key)
        caption = "เรียงคะแนนมาก→น้อย; คะแนนเท่ากันใช้ risk_id น้อย→มาก เป็น technical tie-break เท่านั้น"
        if ties > 3:
            caption += f" · มี {ties:,} รายการที่คะแนน {top_score} เท่ากัน ลำดับในกลุ่มนี้ไม่ได้สะท้อน business priority"
        st.html(theme.top_risks_table(top, show_bu=bu_key is None, caption=f"{caption} · {context}"))


# --- Section: progress (METRIC-06, METRIC-07) ----------------------------------------

st.html(theme.section("ความคืบหน้าการจัดการความเสี่ยงรายหน่วยงาน"))
p_left, p_right = st.columns(2, gap="medium")

with p_left, st.container(border=True):
    st.html(theme.chart_heading("สัดส่วนที่ปิดแล้ว", "closed ÷ ความเสี่ยงทั้งหมดของหน่วยงาน · เรียงมาก→น้อย"))
    bu_bars(
        status_bu,
        value="closed_risk_ratio",
        value_text=lambda r: f"{r.closed_risk_ratio:.1f}%",
        detail=lambda r: f"{r.closed_risk_count:,}/{r.total_risk_count:,}",
        description="สัดส่วนความเสี่ยงที่ปิดแล้วต่อทั้งหมด แยกตาม Business Unit ณ snapshot ล่าสุด",
        max_value=100,
    )
    st.html(theme.note("สถานะสะสม ณ snapshot นี้ ไม่ใช่ความเร็วในการปิด (source ไม่มีวันที่) · METRIC-06"))

with p_right, st.container(border=True):
    st.html(theme.chart_heading("ยังไม่เริ่มดำเนินการ", "open ÷ ความเสี่ยงที่ยังไม่ปิดของหน่วยงาน · เรียงมาก→น้อย"))
    started = status_bu.dropna(subset=["not_started_share"])
    bu_bars(
        started,
        value="not_started_share",
        value_text=lambda r: f"{r.not_started_share:.1f}%",
        detail=lambda r: f"{r.not_started_risk_count:,}/{r.unresolved_risk_count:,}",
        description="สัดส่วนความเสี่ยงที่ยังไม่ปิดซึ่งยังมีสถานะ open แยกตาม Business Unit ณ snapshot ล่าสุด",
        max_value=100,
    )
    st.html(theme.note("ส่วนที่เหลือคือ in_progress · นิยาม open = ยังไม่เริ่ม รอ management ยืนยัน · METRIC-07"))


# --- Section: Risk matrix (METRIC-08) ---------------------------------------------------

st.html(theme.section("Risk Matrix: Likelihood × Impact"))
with st.container(border=True):
    st.html(
        theme.chart_heading(
            "จำนวนความเสี่ยงที่ยังไม่ปิดในแต่ละช่อง",
            "ช่องที่คะแนนเท่ากันอาจต่างกันที่โอกาสเกิดหรือผลกระทบ เช่น L5×I2 กับ L2×I5 = 10",
        )
    )
    st.html(
        theme.matrix_table(
            queries.risk_matrix(con, bu_key),
            caption=f"METRIC-08 · {context} · ไม่ใช้สีแทนระดับ เพราะยังไม่มีเกณฑ์ระดับที่อนุมัติ",
        )
    )


# --- Drill-down: score -> risk detail ---------------------------------------------------

st.html(theme.section("รายละเอียดความเสี่ยงที่ยังไม่ปิด"))
with st.expander("เปิดดูรายการ (drill-down ตามคะแนน)"):
    score_choice = st.selectbox("Risk Priority Score", ["ทั้งหมด", *score_order], key="score_filter")
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
