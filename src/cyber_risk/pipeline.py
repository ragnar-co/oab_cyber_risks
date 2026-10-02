"""Ingestion pipeline: source CSV -> validation -> DuckDB semantic snapshot.

Implements PIPELINE-01..06 (PIPELINE_SPEC.md), quality rules (DATA_QUALITY.md)
and the snapshot publication gate backed by `snapshot_registry`
(DATA_MODEL_SPEC.md). Business logic follows METRIC_LOGIC.md:

    Unresolved Risk      = status != 'closed'
    Risk Priority Score  = likelihood x impact
"""

from __future__ import annotations

import tempfile
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import duckdb

# DATA_CONTRACT.md — Required Fields
REQUIRED_FIELDS = (
    "risk_id",
    "business_unit",
    "risk_title",
    "likelihood",
    "impact",
    "status",
    "owner",
)

# Observed in the development sample only; not a contractual allowed set.
OBSERVED_STATUS_VALUES = ("open", "in_progress", "closed")

SCHEMA_DDL = """
CREATE SEQUENCE IF NOT EXISTS seq_business_unit_key START 1;
CREATE SEQUENCE IF NOT EXISTS seq_owner_key START 1;
CREATE SEQUENCE IF NOT EXISTS seq_risk_snapshot_key START 1;
CREATE SEQUENCE IF NOT EXISTS seq_unit_snapshot_key START 1;
CREATE SEQUENCE IF NOT EXISTS seq_unit_score_snapshot_key START 1;

CREATE TABLE IF NOT EXISTS snapshot_registry (
    snapshot_at        TIMESTAMP PRIMARY KEY,
    publication_status VARCHAR NOT NULL,
    pipeline_run_id    VARCHAR NOT NULL,
    source_name        VARCHAR,
    source_row_count   BIGINT,
    published_at       TIMESTAMP,
    message            VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_business_unit (
    business_unit_key  INTEGER PRIMARY KEY DEFAULT nextval('seq_business_unit_key'),
    business_unit_name VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_owner (
    owner_key INTEGER PRIMARY KEY DEFAULT nextval('seq_owner_key'),
    owner_id  VARCHAR NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fact_risk_snapshot (
    risk_snapshot_key   BIGINT PRIMARY KEY DEFAULT nextval('seq_risk_snapshot_key'),
    risk_id             VARCHAR,
    risk_title          VARCHAR,
    business_unit_key   INTEGER,
    owner_key           INTEGER,
    likelihood          INTEGER,
    impact              INTEGER,
    status              VARCHAR,
    risk_priority_score INTEGER,
    is_unresolved       BOOLEAN,
    snapshot_at         TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_unresolved_risk_unit_snapshot (
    unit_snapshot_key           BIGINT PRIMARY KEY DEFAULT nextval('seq_unit_snapshot_key'),
    business_unit_key           INTEGER,
    unresolved_risk_count       BIGINT,
    total_unresolved_risk_count BIGINT,
    unresolved_risk_share       DOUBLE,
    snapshot_at                 TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_unresolved_risk_score_snapshot (
    unit_score_snapshot_key BIGINT PRIMARY KEY DEFAULT nextval('seq_unit_score_snapshot_key'),
    business_unit_key       INTEGER,
    risk_priority_score     INTEGER,
    unresolved_risk_count   BIGINT,
    snapshot_at             TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dq_result (
    snapshot_at  TIMESTAMP,
    rule_id      VARCHAR,
    rule_name    VARCHAR,
    severity     VARCHAR,
    failed_count BIGINT,
    passed       BOOLEAN
);

CREATE TABLE IF NOT EXISTS quarantine_risk (
    snapshot_at TIMESTAMP,
    rule_id     VARCHAR,
    risk_id     VARCHAR,
    raw_record  VARCHAR
);
"""


@dataclass
class RuleResult:
    rule_id: str
    rule_name: str
    severity: str  # rule_severity: error | warning
    failed_count: int

    @property
    def passed(self) -> bool:
        return self.failed_count == 0


@dataclass
class IngestResult:
    snapshot_at: datetime
    publication_status: str  # published | failed
    source_row_count: int = 0
    rules: list[RuleResult] = field(default_factory=list)
    message: str | None = None

    @property
    def published(self) -> bool:
        return self.publication_status == "published"

    @property
    def errors(self) -> list[RuleResult]:
        return [r for r in self.rules if r.severity == "error" and not r.passed]

    @property
    def warnings(self) -> list[RuleResult]:
        return [r for r in self.rules if r.severity == "warning" and not r.passed]


class SchemaDriftError(Exception):
    """Incoming schema is not compatible with DATA_CONTRACT.md (DQ-020)."""


def connect(db_path: str | Path) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(db_path))
    con.execute(SCHEMA_DDL)
    return con


def extract_csv(source: str | Path) -> Path:
    """Return a CSV path; a .zip source is unpacked to a temp dir (first .csv member)."""
    source = Path(source)
    if source.suffix.lower() != ".zip":
        return source
    with zipfile.ZipFile(source) as zf:
        members = [
            m for m in zf.namelist()
            if m.lower().endswith(".csv") and not m.startswith("__MACOSX/")
        ]
        if not members:
            raise SchemaDriftError(f"zip {source.name} has no .csv member")
        out_dir = Path(tempfile.mkdtemp(prefix="cyber_risk_"))
        return Path(zf.extract(members[0], out_dir))


def _load_raw(con: duckdb.DuckDBPyConnection, csv_path: Path) -> list[str]:
    """PIPELINE-01: load source as all-VARCHAR to preserve source values."""
    con.execute(
        "CREATE OR REPLACE TEMP TABLE raw_cyber_risk_source AS "
        "SELECT * FROM read_csv(?, header = true, all_varchar = true)",
        [str(csv_path)],
    )
    columns = [row[0] for row in con.execute("DESCRIBE raw_cyber_risk_source").fetchall()]
    # Some producers emit a UTF-8 BOM before the first header; strip it so the
    # contract comparison is on real field names, not on encoding artefacts.
    for col in columns:
        clean = col.lstrip("﻿").strip()
        if clean != col:
            con.execute(f'ALTER TABLE raw_cyber_risk_source RENAME "{col}" TO "{clean}"')
    return [c.lstrip("﻿").strip() for c in columns]


def _check_schema(columns: list[str]) -> None:
    """DQ-020 — Upstream Schema Drift. No silent rename/cast."""
    missing = [f for f in REQUIRED_FIELDS if f not in columns]
    if missing:
        raise SchemaDriftError(f"required field(s) missing: {', '.join(missing)}")


def _build_staging(con: duckdb.DuckDBPyConnection) -> None:
    """stg_cyber_risk: normalize types, keep raw values for investigation."""
    con.execute(
        """
        CREATE OR REPLACE TEMP TABLE stg_cyber_risk AS
        SELECT
            NULLIF(TRIM(risk_id), '')       AS risk_id,
            NULLIF(TRIM(business_unit), '') AS business_unit,
            NULLIF(TRIM(risk_title), '')    AS risk_title,
            NULLIF(TRIM(likelihood), '')    AS likelihood_raw,
            NULLIF(TRIM(impact), '')        AS impact_raw,
            TRY_CAST(NULLIF(TRIM(likelihood), '') AS INTEGER) AS likelihood,
            TRY_CAST(NULLIF(TRIM(impact), '') AS INTEGER)     AS impact,
            NULLIF(TRIM(status), '')        AS status,
            NULLIF(TRIM(owner), '')         AS owner
        FROM raw_cyber_risk_source
        """
    )


# Row-level rules evaluated on staging, before anything is written to semantic
# tables. Each entry: (rule_id, rule_name, severity, failing-row predicate).
STAGING_RULES = (
    ("DQ-001", "Missing Risk ID", "error", "risk_id IS NULL"),
    (
        "DQ-003",
        "Required Metric Inputs Missing",
        "error",
        "status IS NULL OR likelihood_raw IS NULL OR impact_raw IS NULL",
    ),
    ("DQ-004", "Missing Business Unit", "error", "business_unit IS NULL"),
    ("DQ-005", "Missing Owner", "warning", "owner IS NULL"),
    (
        "DQ-021",
        "Likelihood / Impact Type Validity",
        "error",
        "(likelihood_raw IS NOT NULL AND likelihood IS NULL) "
        "OR (impact_raw IS NOT NULL AND impact IS NULL)",
    ),
    (
        "DQ-022",
        "Status Outside Observed Values",
        "warning",
        "status IS NOT NULL AND status NOT IN ("
        + ", ".join(f"'{s}'" for s in OBSERVED_STATUS_VALUES)
        + ")",
    ),
)


def _run_staging_rules(con, snapshot_at) -> list[RuleResult]:
    results = []
    for rule_id, name, severity, predicate in STAGING_RULES:
        con.execute(
            f"""
            INSERT INTO quarantine_risk
            SELECT ?, ?, risk_id, to_json(s)::VARCHAR
            FROM stg_cyber_risk AS s
            WHERE {predicate}
            """,
            [snapshot_at, rule_id],
        )
        (failed,) = con.execute(
            f"SELECT COUNT(*) FROM stg_cyber_risk WHERE {predicate}"
        ).fetchone()
        results.append(RuleResult(rule_id, name, severity, failed))

    # DQ-010 — Duplicate Risk Grain (one row per risk_id per snapshot)
    con.execute(
        """
        INSERT INTO quarantine_risk
        SELECT ?, 'DQ-010', risk_id, to_json(s)::VARCHAR
        FROM stg_cyber_risk AS s
        WHERE risk_id IN (
            SELECT risk_id FROM stg_cyber_risk
            WHERE risk_id IS NOT NULL
            GROUP BY risk_id HAVING COUNT(*) > 1
        )
        """,
        [snapshot_at],
    )
    (dupes,) = con.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT risk_id FROM stg_cyber_risk
            WHERE risk_id IS NOT NULL
            GROUP BY risk_id HAVING COUNT(*) > 1
        )
        """
    ).fetchone()
    results.append(RuleResult("DQ-010", "Duplicate Risk Grain", "error", dupes))
    return results


def _build_semantic(con, snapshot_at) -> None:
    """PIPELINE-02..06 for one snapshot. Idempotent: rebuilds that snapshot only."""
    for table in (
        "fact_risk_snapshot",
        "fact_unresolved_risk_unit_snapshot",
        "fact_unresolved_risk_score_snapshot",
    ):
        con.execute(f"DELETE FROM {table} WHERE snapshot_at = ?", [snapshot_at])

    # PIPELINE-03 — dimensions, upsert by business key (SCD type 1)
    con.execute(
        """
        INSERT INTO dim_business_unit (business_unit_name)
        SELECT DISTINCT business_unit FROM stg_cyber_risk
        WHERE business_unit IS NOT NULL
          AND business_unit NOT IN (SELECT business_unit_name FROM dim_business_unit)
        ORDER BY 1
        """
    )
    con.execute(
        """
        INSERT INTO dim_owner (owner_id)
        SELECT DISTINCT owner FROM stg_cyber_risk
        WHERE owner IS NOT NULL
          AND owner NOT IN (SELECT owner_id FROM dim_owner)
        ORDER BY 1
        """
    )

    # PIPELINE-02 + PIPELINE-04 — canonical derived fields, risk-level fact
    con.execute(
        """
        INSERT INTO fact_risk_snapshot (
            risk_id, risk_title, business_unit_key, owner_key,
            likelihood, impact, status,
            risk_priority_score, is_unresolved, snapshot_at
        )
        SELECT
            s.risk_id,
            s.risk_title,
            b.business_unit_key,
            o.owner_key,
            s.likelihood,
            s.impact,
            s.status,
            CASE
                WHEN s.likelihood IS NULL OR s.impact IS NULL THEN NULL
                ELSE s.likelihood * s.impact
            END AS risk_priority_score,
            CASE
                WHEN s.status IS NULL THEN NULL
                WHEN s.status <> 'closed' THEN TRUE
                ELSE FALSE
            END AS is_unresolved,
            ? AS snapshot_at
        FROM stg_cyber_risk AS s
        LEFT JOIN dim_business_unit AS b ON b.business_unit_name = s.business_unit
        LEFT JOIN dim_owner AS o ON o.owner_id = s.owner
        """,
        [snapshot_at],
    )

    # PIPELINE-05 — Business Unit aggregate (METRIC-01, METRIC-02)
    con.execute(
        """
        INSERT INTO fact_unresolved_risk_unit_snapshot (
            business_unit_key, unresolved_risk_count,
            total_unresolved_risk_count, unresolved_risk_share, snapshot_at
        )
        WITH unit_counts AS (
            SELECT business_unit_key, snapshot_at, COUNT(*) AS unresolved_risk_count
            FROM fact_risk_snapshot
            WHERE is_unresolved = TRUE AND snapshot_at = ?
            GROUP BY business_unit_key, snapshot_at
        )
        SELECT
            business_unit_key,
            unresolved_risk_count,
            SUM(unresolved_risk_count) OVER (PARTITION BY snapshot_at),
            CASE
                WHEN SUM(unresolved_risk_count) OVER (PARTITION BY snapshot_at) = 0 THEN 0
                ELSE 100.0 * unresolved_risk_count
                     / SUM(unresolved_risk_count) OVER (PARTITION BY snapshot_at)
            END,
            snapshot_at
        FROM unit_counts
        """,
        [snapshot_at],
    )

    # PIPELINE-06 — Priority Score aggregate (METRIC-04)
    con.execute(
        """
        INSERT INTO fact_unresolved_risk_score_snapshot (
            business_unit_key, risk_priority_score, unresolved_risk_count, snapshot_at
        )
        SELECT business_unit_key, risk_priority_score, COUNT(*), snapshot_at
        FROM fact_risk_snapshot
        WHERE is_unresolved = TRUE
          AND risk_priority_score IS NOT NULL
          AND snapshot_at = ?
        GROUP BY business_unit_key, risk_priority_score, snapshot_at
        """,
        [snapshot_at],
    )


# Post-build assertions on the semantic tables of one snapshot. Each query
# returns the number of violating rows; `?` is bound to snapshot_at.
SEMANTIC_RULES = (
    ("DQ-002", "Missing Snapshot Timestamp", "error",
     "SELECT COUNT(*) FROM fact_risk_snapshot WHERE snapshot_at IS NULL"),
    ("DQ-006", "Unresolved Flag Consistency", "error",
     """SELECT COUNT(*) FROM fact_risk_snapshot WHERE snapshot_at = ? AND (
            (status = 'closed' AND is_unresolved = TRUE)
         OR (status <> 'closed' AND is_unresolved <> TRUE))"""),
    ("DQ-007", "Risk Priority Score Consistency", "error",
     """SELECT COUNT(*) FROM fact_risk_snapshot WHERE snapshot_at = ?
          AND likelihood IS NOT NULL AND impact IS NOT NULL
          AND risk_priority_score <> likelihood * impact"""),
    ("DQ-011", "Business Unit Aggregate Grain Uniqueness", "error",
     """SELECT COUNT(*) FROM (SELECT business_unit_key FROM fact_unresolved_risk_unit_snapshot
          WHERE snapshot_at = ? GROUP BY business_unit_key HAVING COUNT(*) > 1)"""),
    ("DQ-012", "Priority Aggregate Grain Uniqueness", "error",
     """SELECT COUNT(*) FROM (SELECT business_unit_key, risk_priority_score
          FROM fact_unresolved_risk_score_snapshot WHERE snapshot_at = ?
          GROUP BY business_unit_key, risk_priority_score HAVING COUNT(*) > 1)"""),
    ("DQ-013", "Risk -> Business Unit", "error",
     """SELECT COUNT(*) FROM fact_risk_snapshot f
          LEFT JOIN dim_business_unit d ON f.business_unit_key = d.business_unit_key
          WHERE f.snapshot_at = ? AND f.business_unit_key IS NOT NULL
            AND d.business_unit_key IS NULL"""),
    ("DQ-014", "Risk -> Owner", "warning",
     """SELECT COUNT(*) FROM fact_risk_snapshot f
          LEFT JOIN dim_owner d ON f.owner_key = d.owner_key
          WHERE f.snapshot_at = ? AND f.owner_key IS NOT NULL AND d.owner_key IS NULL"""),
    ("DQ-015", "Business Unit Aggregate -> Dimension", "error",
     """SELECT COUNT(*) FROM fact_unresolved_risk_unit_snapshot f
          LEFT JOIN dim_business_unit d ON f.business_unit_key = d.business_unit_key
          WHERE f.snapshot_at = ? AND d.business_unit_key IS NULL"""),
    ("DQ-016", "Priority Aggregate -> Dimension", "error",
     """SELECT COUNT(*) FROM fact_unresolved_risk_score_snapshot f
          LEFT JOIN dim_business_unit d ON f.business_unit_key = d.business_unit_key
          WHERE f.snapshot_at = ? AND d.business_unit_key IS NULL"""),
    # IT-003 — Aggregate Reconciliation (returns 1 when mismatched)
    ("IT-003", "Aggregate Reconciliation", "error",
     """SELECT CASE WHEN
            (SELECT COALESCE(SUM(unresolved_risk_count), 0)
               FROM fact_unresolved_risk_unit_snapshot WHERE snapshot_at = $1)
          = (SELECT COUNT(*) FROM fact_risk_snapshot
               WHERE snapshot_at = $1 AND is_unresolved = TRUE)
        AND (SELECT COALESCE(SUM(unresolved_risk_count), 0)
               FROM fact_unresolved_risk_score_snapshot WHERE snapshot_at = $1)
          = (SELECT COUNT(*) FROM fact_risk_snapshot
               WHERE snapshot_at = $1 AND is_unresolved = TRUE
                 AND risk_priority_score IS NOT NULL)
        THEN 0 ELSE 1 END"""),
)


def _run_semantic_rules(con, snapshot_at) -> list[RuleResult]:
    results = []
    for rule_id, name, severity, sql in SEMANTIC_RULES:
        n_params = sql.count("?")
        params = [snapshot_at] if ("$1" in sql or n_params) else []
        (failed,) = con.execute(sql, params).fetchone()
        results.append(RuleResult(rule_id, name, severity, int(failed)))
    return results


def _record_rules(con, snapshot_at, rules: list[RuleResult]) -> None:
    con.executemany(
        "INSERT INTO dq_result VALUES (?, ?, ?, ?, ?, ?)",
        [(snapshot_at, r.rule_id, r.rule_name, r.severity, r.failed_count, r.passed)
         for r in rules],
    )


def _finish(con, snapshot_at, status: str, message: str | None = None) -> None:
    con.execute(
        """
        UPDATE snapshot_registry
        SET publication_status = ?,
            published_at = CASE WHEN ? = 'published' THEN now()::TIMESTAMP END,
            message = ?
        WHERE snapshot_at = ?
        """,
        [status, status, message, snapshot_at],
    )


def ingest(
    con: duckdb.DuckDBPyConnection,
    source: str | Path,
    source_name: str | None = None,
    snapshot_at: datetime | None = None,
) -> IngestResult:
    """Run the full pipeline for one source update and publish it if it passes.

    A snapshot is published only when no `error` rule fails (DATA_QUALITY.md
    Publication Gate). Otherwise semantic rows of that snapshot are rolled back,
    the registry row is marked `failed`, and dashboards keep reading the last
    published snapshot.
    """
    snapshot_at = snapshot_at or datetime.now()
    source = Path(source)
    source_name = source_name or source.name
    run_id = str(uuid.uuid4())

    con.execute("DELETE FROM dq_result WHERE snapshot_at = ?", [snapshot_at])
    con.execute("DELETE FROM quarantine_risk WHERE snapshot_at = ?", [snapshot_at])
    con.execute("DELETE FROM snapshot_registry WHERE snapshot_at = ?", [snapshot_at])
    con.execute(
        "INSERT INTO snapshot_registry (snapshot_at, publication_status, pipeline_run_id, "
        "source_name) VALUES (?, 'building', ?, ?)",
        [snapshot_at, run_id, source_name],
    )

    result = IngestResult(snapshot_at=snapshot_at, publication_status="building")
    try:
        columns = _load_raw(con, extract_csv(source))
        _check_schema(columns)
    except (SchemaDriftError, duckdb.Error, zipfile.BadZipFile, OSError) as exc:
        result.rules.append(RuleResult("DQ-020", "Upstream Schema Drift", "error", 1))
        _record_rules(con, snapshot_at, result.rules)
        result.publication_status = "failed"
        result.message = f"Schema / source error: {exc}"
        _finish(con, snapshot_at, "failed", result.message)
        return result

    result.rules.append(RuleResult("DQ-020", "Upstream Schema Drift", "error", 0))
    _build_staging(con)
    (result.source_row_count,) = con.execute("SELECT COUNT(*) FROM stg_cyber_risk").fetchone()
    con.execute(
        "UPDATE snapshot_registry SET source_row_count = ? WHERE snapshot_at = ?",
        [result.source_row_count, snapshot_at],
    )

    result.rules += _run_staging_rules(con, snapshot_at)
    if result.errors:
        _record_rules(con, snapshot_at, result.rules)
        result.publication_status = "failed"
        result.message = "Blocked by error rule(s): " + ", ".join(r.rule_id for r in result.errors)
        _finish(con, snapshot_at, "failed", result.message)
        return result

    con.execute("BEGIN TRANSACTION")
    try:
        _build_semantic(con, snapshot_at)
        result.rules += _run_semantic_rules(con, snapshot_at)
        if result.errors:
            con.execute("ROLLBACK")
        else:
            con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise

    _record_rules(con, snapshot_at, result.rules)
    if result.errors:
        result.publication_status = "failed"
        result.message = "Blocked by error rule(s): " + ", ".join(r.rule_id for r in result.errors)
    else:
        result.publication_status = "published"
        if result.warnings:
            result.message = "Published with warning(s): " + ", ".join(
                r.rule_id for r in result.warnings
            )
    _finish(con, snapshot_at, result.publication_status, result.message)
    return result
