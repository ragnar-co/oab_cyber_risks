"""Tests mapped to TESTING_STRATEGY.md (UT / IT / MV)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

from cyber_risk import pipeline, queries

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample" / "oab_cyber_risks_2_5mb.csv.zip"
HEADER = "risk_id,business_unit,risk_title,likelihood,impact,status,owner\n"


@pytest.fixture
def con(tmp_path):
    c = pipeline.connect(tmp_path / "test.duckdb")
    yield c
    c.close()


@pytest.fixture
def loaded(con):
    result = pipeline.ingest(con, SAMPLE, snapshot_at=datetime(2026, 10, 2, 10, 0))
    assert result.published, result.message
    return con


def bu_key(con, name):
    return con.execute(
        "SELECT business_unit_key FROM dim_business_unit WHERE business_unit_name = ?", [name]
    ).fetchone()[0]


def write_csv(tmp_path, body, name="src.csv", header=HEADER):
    p = tmp_path / name
    p.write_text(header + body, encoding="utf-8")
    return p


# --- MV: golden dataset -----------------------------------------------------

def test_mv001_counts(loaded):
    c = queries.risk_counts(loaded)
    assert (c.total, c.closed, c.unresolved) == (10_507, 2_528, 7_979)


def test_mv001_by_business_unit(loaded):
    df = queries.unresolved_by_business_unit(loaded)
    assert dict(zip(df.business_unit_name, df.unresolved_risk_count)) == {
        "Operations": 2123, "IT Infrastructure": 1781, "Sales": 1460,
        "Finance": 1112, "Customer Service": 863, "HR": 640,
    }
    assert list(df.unresolved_risk_count) == sorted(df.unresolved_risk_count, reverse=True)


def test_mv002_share(loaded):
    df = queries.unresolved_by_business_unit(loaded).set_index("business_unit_name")
    assert df.loc["Operations", "unresolved_risk_share"] == pytest.approx(26.6073, abs=1e-4)
    assert df.unresolved_risk_share.sum() == pytest.approx(100.0)


def test_mv004_score_25(loaded):
    df = queries.unresolved_by_priority_score(loaded).set_index("risk_priority_score")
    assert df.loc[25, "unresolved_risk_count"] == 471
    assert df.unresolved_risk_count.sum() == 7_979


def test_mv005_top3_global(loaded):
    df = queries.top_risks(loaded)
    assert list(df.risk_id) == ["R000004", "R000007", "R000008"]
    assert list(df.owner_id) == ["Owner-39", "Owner-48", "Owner-04"]
    assert list(df.risk_priority_score) == [25, 25, 25]
    assert df.risk_title[0].startswith("การทดสอบกู้คืนระบบสำคัญไม่ครบตามแผน")


def test_mv005b_top3_reranked_within_business_unit(loaded):
    df = queries.top_risks(loaded, bu=bu_key(loaded, "HR"))
    assert list(df.risk_id) == ["R000608", "R001210", "R002115"]
    assert list(df.follow_up_rank) == [1, 2, 3]


def test_filter_by_business_unit_counts(loaded):
    c = queries.risk_counts(loaded, bu=bu_key(loaded, "Operations"))
    assert c.unresolved == 2123
    assert c.total == c.closed + c.unresolved == 2503
    scores = queries.unresolved_by_priority_score(loaded, bu=bu_key(loaded, "Operations"))
    assert scores.unresolved_risk_count.sum() == 2123


# --- UT: transformation logic -----------------------------------------------

def test_ut001_ut002_derived_fields(con, tmp_path):
    src = write_csv(tmp_path, "A1,HR,t,1,1,open,O1\nA2,HR,t,2,5,in_progress,O1\nA3,HR,t,5,5,closed,O1\n")
    assert pipeline.ingest(con, src).published
    rows = dict(con.execute(
        "SELECT risk_id, (is_unresolved, risk_priority_score) FROM fact_risk_snapshot"
    ).fetchall())
    assert rows == {"A1": (True, 1), "A2": (True, 10), "A3": (False, 25)}


def test_ut009_unpublished_snapshot_is_not_shown(loaded, tmp_path):
    bad = write_csv(tmp_path, ",HR,t,1,1,open,O1\n")
    result = pipeline.ingest(loaded, bad)
    assert result.publication_status == "failed"
    assert "DQ-001" in result.message
    assert queries.current_snapshot(loaded) == datetime(2026, 10, 2, 10, 0)
    assert queries.risk_counts(loaded).total == 10_507


# --- DQ / IT: failure paths ---------------------------------------------------

@pytest.mark.parametrize(
    "body, rule",
    [
        (",HR,t,1,1,open,O1\n", "DQ-001"),
        ("A1,HR,t,,1,open,O1\n", "DQ-003"),
        ("A1,,t,1,1,open,O1\n", "DQ-004"),
        ("A1,HR,t,high,1,open,O1\n", "DQ-021"),
        ("A1,HR,t,1,1,open,O1\nA1,HR,t,2,2,open,O1\n", "DQ-010"),
    ],
)
def test_error_rules_block_publication(con, tmp_path, body, rule):
    result = pipeline.ingest(con, write_csv(tmp_path, body))
    assert not result.published
    assert rule in {r.rule_id for r in result.errors}
    assert con.execute("SELECT COUNT(*) FROM fact_risk_snapshot").fetchone()[0] == 0
    assert con.execute(
        "SELECT COUNT(*) FROM quarantine_risk WHERE rule_id = ?", [rule]
    ).fetchone()[0] >= 1


def test_warning_rules_do_not_block(con, tmp_path):
    result = pipeline.ingest(con, write_csv(tmp_path, "A1,HR,t,1,1,open,\nA2,HR,t,1,1,Closed,O1\n"))
    assert result.published
    assert {r.rule_id for r in result.warnings} == {"DQ-005", "DQ-022"}


def test_it005_schema_drift_missing_field(con, tmp_path):
    src = write_csv(tmp_path, "A1,HR,t,1,1,O1\n",
                    header="risk_id,business_unit,risk_title,likelihood,impact,owner\n")
    result = pipeline.ingest(con, src)
    assert not result.published
    assert result.errors[0].rule_id == "DQ-020"
    assert "status" in result.message


def test_bom_header_is_accepted(con, tmp_path):
    src = tmp_path / "bom.csv"
    src.write_bytes(("﻿" + HEADER + "A1,HR,t,2,3,open,O1\n").encode("utf-8"))
    assert pipeline.ingest(con, src).published


def test_it004_idempotent_rerun_same_snapshot(con):
    ts = datetime(2026, 10, 2, 9, 0)
    pipeline.ingest(con, SAMPLE, snapshot_at=ts)
    counts = [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in (
        "fact_risk_snapshot", "fact_unresolved_risk_unit_snapshot",
        "fact_unresolved_risk_score_snapshot")]
    pipeline.ingest(con, SAMPLE, snapshot_at=ts)
    again = [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in (
        "fact_risk_snapshot", "fact_unresolved_risk_unit_snapshot",
        "fact_unresolved_risk_score_snapshot")]
    assert counts == again == [10_507, 6, 6 * 13]


def test_null_score_never_ranks(con, tmp_path):
    """UT-008 — enforced upstream: NULL metric inputs block the snapshot (DQ-003)."""
    result = pipeline.ingest(con, write_csv(tmp_path, "A0,HR,t,,5,open,O1\nA1,HR,t,1,1,open,O1\n"))
    assert not result.published
    assert queries.current_snapshot(con) is None


# --- MV-006..008: management extension metrics ----------------------------------

def test_mv006_closed_risk_ratio(loaded):
    df = queries.status_by_business_unit(loaded).set_index("business_unit_name")
    assert df.loc["Operations", "closed_risk_count"] == 380
    assert df.loc["Operations", "closed_risk_ratio"] == pytest.approx(15.18, abs=0.01)
    assert df.loc["HR", "closed_risk_ratio"] == pytest.approx(37.92, abs=0.01)
    assert df.closed_risk_count.sum() == 2_528
    assert df.total_risk_count.sum() == 10_507


def test_mv007_not_started_share(loaded):
    df = queries.status_by_business_unit(loaded).set_index("business_unit_name")
    assert df.loc["Finance", "not_started_risk_count"] == 685
    assert df.loc["Finance", "not_started_share"] == pytest.approx(61.60, abs=0.01)
    assert df.not_started_risk_count.sum() == 4_277


def test_mv006_business_unit_with_everything_closed(con, tmp_path):
    src = write_csv(tmp_path, "A1,HR,t,1,1,closed,O1\nA2,Sales,t,2,2,open,O1\n")
    assert pipeline.ingest(con, src).published
    df = queries.status_by_business_unit(con).set_index("business_unit_name")
    assert df.loc["HR", "closed_risk_ratio"] == 100.0
    assert pd.isna(df.loc["HR", "not_started_share"])


def test_mv008_risk_matrix(loaded):
    m = queries.risk_matrix(loaded).set_index(["likelihood", "impact"]).unresolved_risk_count
    assert len(m) == 25
    assert m[(5, 5)] == 471
    assert m[(5, 2)] == 449 and m[(2, 5)] == 479   # both score 10, different shape
    assert m[(1, 5)] == 0 and m[(5, 1)] == 0
    assert m.sum() == 7_979


def test_mv008_risk_matrix_filtered(loaded):
    m = queries.risk_matrix(loaded, bu=bu_key(loaded, "HR"))
    assert len(m) == 25
    assert m.unresolved_risk_count.sum() == 640


# --- Dashboard smoke (Streamlit AppTest) -----------------------------------------

def test_dashboard_renders_and_filters(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("CYBER_RISK_DB", str(tmp_path / "app.duckdb"))
    app = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(str(app), default_timeout=60).run()
    assert not at.exception
    html = " ".join(h.proto.body for h in at.get("html"))
    assert "10,507" in html and "7,979" in html and "R000004" in html

    at.selectbox(key="bu_filter").select("HR").run()
    assert not at.exception
    html = " ".join(h.proto.body for h in at.get("html"))
    assert "R000608" in html and "640" in html
    assert at.query_params["bu"] == ["HR"]
