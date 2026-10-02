"""Metric queries — canonical SQL from METRIC_LOGIC.md.

Every query reads the latest *published* snapshot from `snapshot_registry`
and accepts an optional `business_unit_key` (None = All Business Units),
applied before aggregation / ranking.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import duckdb
import pandas as pd

CURRENT_SNAPSHOT_CTE = """
current_snapshot AS (
    SELECT MAX(snapshot_at) AS snapshot_at
    FROM snapshot_registry
    WHERE publication_status = 'published'
)
"""

BU_FILTER = "($bu IS NULL OR f.business_unit_key = $bu)"


@dataclass
class RiskCounts:
    total: int
    closed: int
    unresolved: int


def current_snapshot(con: duckdb.DuckDBPyConnection) -> datetime | None:
    (snapshot_at,) = con.execute(f"WITH {CURRENT_SNAPSHOT_CTE} SELECT snapshot_at FROM current_snapshot").fetchone()
    return snapshot_at


def business_units(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Business Units present in the current published snapshot."""
    return con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE}
        SELECT DISTINCT d.business_unit_key, d.business_unit_name
        FROM fact_risk_snapshot AS f
        JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        JOIN dim_business_unit AS d ON f.business_unit_key = d.business_unit_key
        ORDER BY d.business_unit_name
        """
    ).df()


def risk_counts(con: duckdb.DuckDBPyConnection, bu: int | None = None) -> RiskCounts:
    """Total / closed / unresolved Risk count for the current snapshot.

    Unresolved comes from the METRIC-01 aggregate; total and closed are read
    from the risk-level fact of the same snapshot.
    """
    total, closed = con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE}
        SELECT
            COUNT(*),
            COUNT(*) FILTER (WHERE f.is_unresolved = FALSE)
        FROM fact_risk_snapshot AS f
        JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        WHERE {BU_FILTER}
        """,
        {"bu": bu},
    ).fetchone()
    (unresolved,) = con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE}
        SELECT COALESCE(SUM(f.unresolved_risk_count), 0)
        FROM fact_unresolved_risk_unit_snapshot AS f
        JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        WHERE {BU_FILTER}
        """,
        {"bu": bu},
    ).fetchone()
    return RiskCounts(total=int(total), closed=int(closed), unresolved=int(unresolved))


def unresolved_by_business_unit(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """METRIC-01 + METRIC-02 — always all Business Units (share vs. whole org)."""
    return con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE}
        SELECT
            d.business_unit_key,
            d.business_unit_name,
            f.unresolved_risk_count,
            f.total_unresolved_risk_count,
            f.unresolved_risk_share
        FROM fact_unresolved_risk_unit_snapshot AS f
        JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        JOIN dim_business_unit AS d ON f.business_unit_key = d.business_unit_key
        ORDER BY f.unresolved_risk_count DESC, d.business_unit_name
        """
    ).df()


def unresolved_by_priority_score(
    con: duckdb.DuckDBPyConnection, bu: int | None = None
) -> pd.DataFrame:
    """METRIC-04 — Unresolved Risk Count by Priority Score."""
    return con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE}
        SELECT
            f.risk_priority_score,
            SUM(f.unresolved_risk_count)::BIGINT AS unresolved_risk_count
        FROM fact_unresolved_risk_score_snapshot AS f
        JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        WHERE {BU_FILTER}
        GROUP BY f.risk_priority_score
        ORDER BY f.risk_priority_score DESC
        """,
        {"bu": bu},
    ).df()


def top_risks(
    con: duckdb.DuckDBPyConnection, bu: int | None = None, limit: int = 3
) -> pd.DataFrame:
    """METRIC-05 — Top Risk Follow-up Rank (re-ranked inside the filter)."""
    return con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE},
        ranked_risks AS (
            SELECT
                f.risk_id,
                f.risk_title,
                f.risk_priority_score,
                f.likelihood,
                f.impact,
                d.business_unit_name,
                o.owner_id,
                ROW_NUMBER() OVER (
                    ORDER BY f.risk_priority_score DESC, f.risk_id ASC
                ) AS follow_up_rank
            FROM fact_risk_snapshot AS f
            JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
            LEFT JOIN dim_business_unit AS d ON f.business_unit_key = d.business_unit_key
            LEFT JOIN dim_owner AS o ON f.owner_key = o.owner_key
            WHERE f.is_unresolved = TRUE
              AND f.risk_priority_score IS NOT NULL
              AND {BU_FILTER}
        )
        SELECT
            follow_up_rank, risk_id, risk_title, risk_priority_score,
            likelihood, impact, owner_id, business_unit_name
        FROM ranked_risks
        WHERE follow_up_rank <= $limit
        ORDER BY follow_up_rank
        """,
        {"bu": bu, "limit": limit},
    ).df()


def tie_count_at_top(con: duckdb.DuckDBPyConnection, bu: int | None = None) -> tuple[int | None, int]:
    """(top score, how many unresolved risks share it) — explains tie-break impact."""
    row = con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE}
        SELECT f.risk_priority_score, SUM(f.unresolved_risk_count)::BIGINT
        FROM fact_unresolved_risk_score_snapshot AS f
        JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        WHERE {BU_FILTER}
        GROUP BY f.risk_priority_score
        ORDER BY f.risk_priority_score DESC
        LIMIT 1
        """,
        {"bu": bu},
    ).fetchone()
    return (row[0], int(row[1])) if row else (None, 0)


def risk_detail(
    con: duckdb.DuckDBPyConnection, bu: int | None = None, score: int | None = None
) -> pd.DataFrame:
    """VIZ-03 — record-level unresolved Risk detail (drill-down from score)."""
    return con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE}
        SELECT
            f.risk_id,
            f.risk_title,
            d.business_unit_name,
            f.likelihood,
            f.impact,
            f.risk_priority_score,
            f.status,
            o.owner_id
        FROM fact_risk_snapshot AS f
        JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        LEFT JOIN dim_business_unit AS d ON f.business_unit_key = d.business_unit_key
        LEFT JOIN dim_owner AS o ON f.owner_key = o.owner_key
        WHERE f.is_unresolved = TRUE
          AND {BU_FILTER}
          AND ($score IS NULL OR f.risk_priority_score = $score)
        ORDER BY f.risk_priority_score DESC NULLS LAST, f.risk_id
        """,
        {"bu": bu, "score": score},
    ).df()


def snapshot_history(con: duckdb.DuckDBPyConnection, limit: int = 20) -> pd.DataFrame:
    return con.execute(
        """
        SELECT snapshot_at, publication_status, source_name, source_row_count,
               published_at, message
        FROM snapshot_registry
        ORDER BY snapshot_at DESC
        LIMIT ?
        """,
        [limit],
    ).df()


def dq_results(con: duckdb.DuckDBPyConnection, snapshot_at: datetime) -> pd.DataFrame:
    return con.execute(
        """
        SELECT rule_id, rule_name, severity, failed_count, passed
        FROM dq_result WHERE snapshot_at = ?
        ORDER BY rule_id
        """,
        [snapshot_at],
    ).df()


def quarantined(con: duckdb.DuckDBPyConnection, snapshot_at: datetime, limit: int = 200) -> pd.DataFrame:
    return con.execute(
        """
        SELECT rule_id, risk_id, raw_record
        FROM quarantine_risk WHERE snapshot_at = ?
        ORDER BY rule_id, risk_id
        LIMIT ?
        """,
        [snapshot_at, limit],
    ).df()


def status_by_business_unit(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """METRIC-06 Closed Risk Ratio + METRIC-07 Not Started Share, all Business Units.

    Read from the risk-level fact so a Business Unit with zero unresolved
    risks (absent from the unit aggregate) still appears with 100% closed.
    """
    return con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE},
        counts AS (
            SELECT
                d.business_unit_key,
                d.business_unit_name,
                COUNT(*) AS total_risk_count,
                COUNT(*) FILTER (WHERE f.is_unresolved = FALSE) AS closed_risk_count,
                COUNT(*) FILTER (WHERE f.is_unresolved = TRUE) AS unresolved_risk_count,
                COUNT(*) FILTER (WHERE f.is_unresolved = TRUE AND f.status = 'open')
                    AS not_started_risk_count
            FROM fact_risk_snapshot AS f
            JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
            JOIN dim_business_unit AS d ON f.business_unit_key = d.business_unit_key
            WHERE f.is_unresolved IS NOT NULL
            GROUP BY d.business_unit_key, d.business_unit_name
        )
        SELECT
            *,
            100.0 * closed_risk_count / total_risk_count AS closed_risk_ratio,
            CASE
                WHEN unresolved_risk_count = 0 THEN NULL
                ELSE 100.0 * not_started_risk_count / unresolved_risk_count
            END AS not_started_share
        FROM counts
        ORDER BY business_unit_name
        """
    ).df()


def risk_matrix(con: duckdb.DuckDBPyConnection, bu: int | None = None) -> pd.DataFrame:
    """METRIC-08 — Unresolved Risk count per likelihood x impact cell (long form).

    Axis values are those observed in the current snapshot (no assumed 1-5
    range: DATA_CONTRACT.md has no approved range yet); empty cells are 0.
    """
    return con.execute(
        f"""
        WITH {CURRENT_SNAPSHOT_CTE},
        snap AS (
            SELECT f.*
            FROM fact_risk_snapshot AS f
            JOIN current_snapshot AS s ON f.snapshot_at = s.snapshot_at
        ),
        axes AS (
            SELECT l.likelihood, i.impact
            FROM (SELECT DISTINCT likelihood FROM snap WHERE likelihood IS NOT NULL) AS l
            CROSS JOIN (SELECT DISTINCT impact FROM snap WHERE impact IS NOT NULL) AS i
        ),
        cells AS (
            SELECT f.likelihood, f.impact, COUNT(*) AS unresolved_risk_count
            FROM snap AS f
            WHERE f.is_unresolved = TRUE AND {BU_FILTER}
            GROUP BY f.likelihood, f.impact
        )
        SELECT
            a.likelihood,
            a.impact,
            a.likelihood * a.impact AS risk_priority_score,
            COALESCE(c.unresolved_risk_count, 0) AS unresolved_risk_count
        FROM axes AS a
        LEFT JOIN cells AS c USING (likelihood, impact)
        ORDER BY a.likelihood DESC, a.impact
        """,
        {"bu": bu},
    ).df()
