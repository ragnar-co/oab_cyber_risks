# Client Cyber Risk Dashboard

แอปรับไฟล์ Cyber Risk CSV → ตรวจสอบคุณภาพข้อมูล → จัดเก็บลง DuckDB → แสดง dashboard สำหรับ management

## Run

```bash
uv sync
uv run streamlit run app.py      # http://localhost:8501
uv run pytest                    # tests จาก TESTING_STRATEGY.md
```

ครั้งแรกที่เปิด แอปจะโหลด `data/sample/oab_cyber_risks_2_5mb.csv.zip` ให้อัตโนมัติ อัปโหลด CSV (หรือ .zip) ใหม่ได้จาก sidebar

DB อยู่ที่ `data/cyber_risk.duckdb` (เปลี่ยนได้ด้วย env `CYBER_RISK_DB`) — DuckDB เปิดเขียนได้ครั้งละ process เดียว

## Dashboard

| ส่วน | เนื้อหา | Metric |
|---|---|---|
| KPI cards | ความเสี่ยงทั้งหมด / ปิดแล้ว / ยังไม่ปิด | METRIC-01 |
| กราฟหน่วยงาน | Unresolved Risk ต่อ Business Unit พร้อม % ต่อทั้งองค์กร | METRIC-01, 02 |
| กราฟระดับความเสี่ยง | Unresolved Risk ต่อ Risk Priority Score | METRIC-04 |
| Top 3 | ชื่อความเสี่ยง, คะแนน, ผู้รับผิดชอบ | METRIC-05 |
| Drill-down | รายการ Risk ตามคะแนน | METRIC-03 |
| สัดส่วนที่ปิดแล้ว | closed ÷ ทั้งหมด ต่อหน่วยงาน | METRIC-06 |
| สัดส่วนที่ยังไม่เริ่ม | open ÷ ยังไม่ปิด ต่อหน่วยงาน | METRIC-07 |
| Risk Matrix | ตาราง likelihood × impact ของความเสี่ยงที่ยังไม่ปิด | METRIC-08 |

Filter หน่วยงาน (ทั้งหมด / รายหน่วยงาน) มีผลกับ KPI cards, กราฟระดับความเสี่ยง, Top 3, Risk Matrix และ drill-down ส่วนกราฟรายหน่วยงาน (METRIC-01/06/07) แสดงทุกหน่วยงานเสมอและ highlight หน่วยงานที่เลือก — Top 3 ถูก rank ใหม่ภายในหน่วยงานที่เลือก

## Business rules ([BUSINESS_GLOSSARY.md](docs/specs/BUSINESS_GLOSSARY.md))

- **Unresolved Risk** = `status != 'closed'` (รวม `open` และ `in_progress`)
- **Risk Priority Score / ระดับความเสี่ยง** = `likelihood × impact` — ใช้คะแนนโดยตรง ไม่มี bucket Low/Medium/High/Critical จนกว่า management อนุมัติ
- **Top 3** = `ORDER BY risk_priority_score DESC, risk_id ASC` (`risk_id` เป็น technical tie-break)

## Pipeline

```text
CSV/zip → raw (all VARCHAR) → DQ-020 schema check → stg_cyber_risk
       → staging rules (DQ-001/003/004/005/010/021/022) → quarantine_risk
       → dim_business_unit, dim_owner, fact_risk_snapshot
       → fact_unresolved_risk_unit_snapshot, fact_unresolved_risk_score_snapshot
       → semantic rules (DQ-002/006/007/011–016, IT-003)
       → snapshot_registry: published | failed
```

ถ้า rule ระดับ `error` fail snapshot นั้นจะไม่ถูก publish และ dashboard ยังแสดง snapshot ล่าสุดที่ผ่าน (ผลตรวจและ quarantined records ดูได้ใน sidebar)

## Repository structure

```text
.
├── app.py                      Streamlit dashboard
├── src/cyber_risk/
│   ├── pipeline.py             ingestion, validation, DuckDB schema, publication gate
│   └── queries.py              metric SQL ตาม METRIC_LOGIC.md
├── tests/test_pipeline.py      golden values, DQ rules, idempotency, schema drift
├── data/
│   ├── sample/                 ไฟล์ CSV ตัวอย่าง (zip)
│   └── cyber_risk.duckdb       สร้างตอนรัน (ไม่ commit)
├── docs/specs/                 project specifications
├── .streamlit/config.toml      theme ตาม VIZ_DESIGN_SPEC.md
└── pyproject.toml / uv.lock
```

## Specifications

| Layer | Docs |
|---|---|
| Business | [STAKEHOLDERS](docs/specs/STAKEHOLDERS.md) · [BUSINESS_GLOSSARY](docs/specs/BUSINESS_GLOSSARY.md) · [KPI_DICTIONARY](docs/specs/KPI_DICTIONARY.md) |
| Metric | [METRIC_SPEC](docs/specs/METRIC_SPEC.md) · [METRIC_LOGIC](docs/specs/METRIC_LOGIC.md) |
| Data | [DATA_CONTRACT](docs/specs/DATA_CONTRACT.md) · [DATA_MODEL_SPEC](docs/specs/DATA_MODEL_SPEC.md) · [PIPELINE_SPEC](docs/specs/PIPELINE_SPEC.md) · [DATA_QUALITY](docs/specs/DATA_QUALITY.md) |
| Presentation | [VIZ_DESIGN_SPEC](docs/specs/VIZ_DESIGN_SPEC.md) · [DASHBOARD_SPEC](docs/specs/DASHBOARD_SPEC.md) |
| QA | [TESTING_STRATEGY](docs/specs/TESTING_STRATEGY.md) |
