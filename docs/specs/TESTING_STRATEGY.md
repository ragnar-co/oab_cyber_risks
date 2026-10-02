# Unit Tests (dbt / SQL)

Unit tests ใช้ตรวจ transformation logic และ schema behavior ของ models โดยอิง `DATA_QUALITY.md` เป็น baseline ของ assertions

## fact_risk_snapshot

### UT-001 — Unresolved Flag Logic

**Source Logic**

`Unresolved Risk = status != 'closed'`

**Test Cases**

| status | Expected `is_unresolved` |
|---|---|
| `open` | `TRUE` |
| `in_progress` | `TRUE` |
| `closed` | `FALSE` |
| `NULL` | `NULL` |

**Assertion**
ผลจาก transformation ต้องตรงกับ expected values ทุก row

---

### UT-002 — Risk Priority Score

Canonical formula:

`risk_priority_score = likelihood × impact`

**Test Cases**

| likelihood | impact | Expected |
|---:|---:|---:|
| 1 | 1 | 1 |
| 2 | 5 | 10 |
| 5 | 5 | 25 |
| `NULL` | 5 | `NULL` |
| 5 | `NULL` | `NULL` |

ห้ามแทน missing input ด้วย 0

---

### UT-008 — NULL Score Excluded from Top 3

Fixture: snapshot ที่มี unresolved Risk หนึ่งรายการที่ `risk_priority_score IS NULL` และรายการอื่นมี score ปกติ

**Expected**
- Risk ที่ score เป็น NULL ไม่อยู่ใน output ของ METRIC-05
- rank 1 เป็น Risk ที่ score สูงสุดที่ไม่ใช่ NULL

ป้องกันกรณี warehouse เรียง `NULL` ก่อนเมื่อ `ORDER BY ... DESC`

---

### UT-009 — Current Snapshot Selection

Fixture: `snapshot_registry` ที่มี snapshot N-1 = `published` และ snapshot N = `building` หรือ `failed`

**Expected**
- metric query ทุกตัวคืนข้อมูลของ snapshot N-1
- ไม่มี query ใดคืนข้อมูลของ snapshot N

---

### UT-003 — Risk Grain Uniqueness

Grain:

`risk_id × snapshot_at`

```sql
SELECT
    risk_id,
    snapshot_at,
    COUNT(*) AS row_count
FROM fact_risk_snapshot
GROUP BY risk_id, snapshot_at
HAVING COUNT(*) > 1;
```

**Expected:** 0 rows

ครอบคลุม `DQ-010`

---

## fact_unresolved_risk_unit_snapshot

### UT-004 — Business Unit Aggregate

จาก `fact_risk_snapshot` ให้ aggregate เฉพาะ:

`is_unresolved = TRUE`

ที่ grain:

`business_unit × snapshot_at`

```sql
SELECT
    business_unit_key,
    snapshot_at,
    COUNT(*) AS expected_count
FROM fact_risk_snapshot
WHERE is_unresolved = TRUE
GROUP BY business_unit_key, snapshot_at;
```

ผลต้องตรงกับ `unresolved_risk_count` ใน aggregate fact

---

### UT-005 — Business Unit Aggregate Grain

```sql
SELECT
    business_unit_key,
    snapshot_at,
    COUNT(*)
FROM fact_unresolved_risk_unit_snapshot
GROUP BY business_unit_key, snapshot_at
HAVING COUNT(*) > 1;
```

**Expected:** 0 rows

ครอบคลุม `DQ-011`

---

## fact_unresolved_risk_score_snapshot

### UT-006 — Score Aggregate

aggregation ต้องใช้เฉพาะ:

- `is_unresolved = TRUE`
- `risk_priority_score IS NOT NULL`

grain:

`business_unit × risk_priority_score × snapshot_at`

---

### UT-007 — Score Aggregate Grain

```sql
SELECT
    business_unit_key,
    risk_priority_score,
    snapshot_at,
    COUNT(*)
FROM fact_unresolved_risk_score_snapshot
GROUP BY
    business_unit_key,
    risk_priority_score,
    snapshot_at
HAVING COUNT(*) > 1;
```

**Expected:** 0 rows

ครอบคลุม `DQ-012`

---

## DATA_QUALITY Baseline Coverage

Unit/SQL assertions ต้องครอบคลุม quality rules จาก `DATA_QUALITY.md` ดังนี้:

| DQ Rule | Test Coverage |
|---|---|
| DQ-001 Missing Risk ID | schema/singular test |
| DQ-002 Missing Snapshot | schema/singular test |
| DQ-003 Missing Metric Inputs | singular SQL test |
| DQ-004 Missing Business Unit | relationship/completeness test |
| DQ-005 Missing Owner | warning-only SQL test |
| DQ-006 Unresolved Flag Consistency | UT-001 |
| DQ-007 Risk Priority Score Consistency | UT-002 |
| DQ-008 Likelihood Validity | pending approved range |
| DQ-009 Impact Validity | pending approved range |
| DQ-010 Risk Grain Duplicate | UT-003 |
| DQ-011 Unit Aggregate Grain | UT-005 |
| DQ-012 Score Aggregate Grain | UT-007 |
| DQ-013 Risk → Business Unit | relationship test |
| DQ-014 Risk → Owner | relationship warning |
| DQ-015 Unit Aggregate → Dimension | relationship test |
| DQ-016 Score Aggregate → Dimension | relationship test |
| DQ-017–019 Anomaly Rules | monitoring tests after threshold calibration |
| DQ-020 Schema Drift | integration/contract test |
| DQ-021 Likelihood / Impact Type Validity | singular SQL test |
| DQ-022 Status Outside Observed Values | warning-only SQL test |

# Integration Tests

Integration tests ตรวจการทำงานข้าม pipeline stages ตั้งแต่ ingestion ถึง semantic facts

## IT-001 — End-to-End Pipeline Run

Test path:

`source → stg_cyber_risk → int_risk_snapshot → dimensions → fact_risk_snapshot → aggregate facts`

**Expected**
- pipeline stages สำเร็จตาม dependency order
- semantic facts อยู่ snapshot เดียวกัน
- ไม่มี `error` quality rule fail

---

## IT-002 — Row Reconciliation

สำหรับ snapshot เดียวกัน:

```text
source valid risk rows
=
fact_risk_snapshot valid rows
```

หลังหักเฉพาะ records ที่ถูก quarantine ตาม quality rule ที่บันทึกไว้อย่างชัดเจน

ห้ามตรวจแค่ aggregate total เพราะ row-level mismatch สองฝั่งอาจหักล้างกันจนยอดรวมดูถูกต้อง

---

## IT-003 — Aggregate Reconciliation

สำหรับ snapshot เดียวกัน:

```text
SUM(fact_unresolved_risk_unit_snapshot.unresolved_risk_count)
=
COUNT(fact_risk_snapshot WHERE is_unresolved = TRUE)
```

และ:

```text
SUM(fact_unresolved_risk_score_snapshot.unresolved_risk_count)
=
COUNT(
    fact_risk_snapshot
    WHERE is_unresolved = TRUE
      AND risk_priority_score IS NOT NULL
)
```

---

## IT-004 — Idempotency

รัน pipeline ของ snapshot เดิม 2 ครั้ง

**Expected**
- จำนวน rows ใน `fact_risk_snapshot` ไม่เพิ่ม
- จำนวน rows ใน aggregate facts ไม่เพิ่ม
- metric values ไม่เปลี่ยนเมื่อ input เดิมไม่เปลี่ยน

ตรวจตาม keys:

`risk_id × snapshot_at`

`business_unit_key × snapshot_at`

`business_unit_key × risk_priority_score × snapshot_at`

---

## IT-005 — Schema Drift

จำลอง source ที่:

- ลบ required field
- rename field
- เปลี่ยน incompatible type

**Expected**
- `PIPELINE-01` ไม่ publish snapshot ใหม่
- incoming data ถูก quarantine
- test ต้อง fail
- deployment/run ถูก block สำหรับ breaking schema change

ครอบคลุม `DQ-020`

---

## IT-006 — Partial Pipeline Failure

จำลองกรณี `fact_risk_snapshot` สำเร็จ แต่ aggregate fact ตัวหนึ่งล้มเหลว

**Expected**
- snapshot ใหม่ยังไม่ถูก publish ไป dashboard
- ห้ามให้ dashboard ผสม fact จาก snapshot ใหม่กับ aggregate จาก snapshot เก่า

# Metric Validation Tests

Metric validation ใช้ **golden dataset** และอ้างสูตรใน `METRIC_LOGIC.md` โดยตรง

## Golden Dataset — Sample Source

Development fixture:

`oab_cyber_risks_2_5mb.csv`

ค่าที่ตรวจได้จาก source ตัวอย่าง:

| Check | Expected |
|---|---:|
| Total Risk records | 10,507 |
| Unresolved Risk Count (`status != closed`) | 7,979 |
| Operations unresolved | 2,123 |
| IT Infrastructure unresolved | 1,781 |
| Sales unresolved | 1,460 |
| Finance unresolved | 1,112 |
| Customer Service unresolved | 863 |
| HR unresolved | 640 |
| Unresolved records with score 25 | 471 |

ค่าชุดนี้เป็น **golden values สำหรับ sample fixture เท่านั้น** ไม่ใช่ target หรือ threshold ของ production

**Verification:** ตรวจซ้ำด้วย DuckDB กับ `data/sample/oab_cyber_risks_2_5mb.csv.zip` เมื่อ 2026-10-02 — ทุกค่าในตารางนี้ และ Top 3 ใน MV-005 ตรงกัน

**Fixture Profile (observed)**
- `risk_id` unique 10,507 ค่า ไม่มี NULL ใน field ใด
- `status`: `open` 4,277 / `in_progress` 3,702 / `closed` 2,528 (lowercase ไม่มี whitespace)
- `likelihood` และ `impact`: integer 1–5
- `owner`: 48 ค่าที่ไม่ซ้ำ
- header ของไฟล์มี UTF-8 BOM — ingestion ต้องตัด BOM ก่อนเทียบ field name กับ `DATA_CONTRACT.md` มิฉะนั้น CSV reader บางตัว (เช่น Python `csv` ที่ไม่ใช้ `utf-8-sig`) จะอ่าน `risk_id` เป็น `\ufeffrisk_id` และ schema drift check (`DQ-020`) จะ fail

---

## MV-001 — METRIC-01 Unresolved Risk Count

สูตรจาก `METRIC_LOGIC.md`:

`COUNT(risk_id WHERE status != 'closed')`

**Expected sample result**

`7,979`

---

## MV-002 — METRIC-02 Share by Business Unit

ตัวอย่าง Operations:

```text
2,123 / 7,979 × 100
```

test ต้องคำนวณ expected value จาก golden dataset และเทียบกับ semantic output โดยใช้ tolerance ที่เหมาะกับ numeric precision ของ implementation

Expected sample values (percentage scale `0–100`, ปัด 4 ตำแหน่ง):

| Business Unit | Unresolved | Share |
|---|---:|---:|
| Operations | 2,123 | 26.6073 |
| IT Infrastructure | 1,781 | 22.3211 |
| Sales | 1,460 | 18.2980 |
| Finance | 1,112 | 13.9366 |
| Customer Service | 863 | 10.8159 |
| HR | 640 | 8.0211 |

**Numeric tolerance:** `null`  
**Calibration Owner:** Analytics Engineering

---

## MV-003 — METRIC-03 Risk Priority Score

ตัวอย่าง row ที่:

`likelihood = 5`  
`impact = 5`

ต้องได้:

`risk_priority_score = 25`

test ต้องตรวจทั้ง row-level calculation ไม่ใช่เฉพาะ distribution aggregate

---

## MV-004 — METRIC-04 Unresolved Risk Count by Priority Score

สำหรับ score `25`

**Expected sample value**

`471`

ต้อง reconcile กับ row-level source records ที่:

```text
status != closed
AND likelihood × impact = 25
```

---

## MV-005 — METRIC-05 Top Risk Follow-up Rank

Canonical ranking:

`risk_priority_score DESC, risk_id ASC`

Expected Top 3 จาก sample fixture:

| Rank | risk_id | risk_title | Score | owner |
|---:|---|---|---:|---|
| 1 | `R000004` | การทดสอบกู้คืนระบบสำคัญไม่ครบตามแผน — ระบบ Ticket / สาขาสมมติ 038 / รายการ 00004 | 25 | `Owner-39` |
| 2 | `R000007` | ไม่มีขั้นตอนยืนยันตัวตนก่อนเปลี่ยนข้อมูลลูกค้า — ระบบ Cloud Console / สาขาสมมติ 028 / รายการ 00007 | 25 | `Owner-48` |
| 3 | `R000008` | บัญชีผู้รับจ้างหมดสัญญายังใช้งานได้ — ระบบ ERP / สาขาสมมติ 171 / รายการ 00008 | 25 | `Owner-04` |

ผลต้องตรงทั้ง:
- rank
- `risk_id`
- `risk_title`
- score
- owner

### MV-005b — Top 3 within Business Unit Filter

Top 3 ต้องถูก rank ใหม่ภายใน Business Unit ที่เลือก (ไม่ใช่ filter Global Top 3 หลัง ranking)

Expected จาก sample fixture (`risk_id`, score ทุกรายการ = 25):

| Business Unit | Rank 1 | Rank 2 | Rank 3 |
|---|---|---|---|
| Customer Service | `R000007` | `R000505` | `R000612` |
| Finance | `R000008` | `R000136` | `R000359` |
| HR | `R000608` | `R001210` | `R002115` |
| IT Infrastructure | `R000004` | `R000196` | `R000335` |
| Operations | `R000081` | `R000091` | `R000092` |
| Sales | `R000165` | `R000201` | `R000305` |

ตัวอย่าง: filter `HR` ต้องได้ 3 rows ข้างต้น — ถ้าใช้ Global Top 3 แล้ว filter จะได้ 0 rows

**Tie note:** fixture มี unresolved score 25 จำนวน 471 รายการ Top 3 ทุกกรณีจึงถูกตัดสินด้วย `risk_id ASC`

## MV-006 — METRIC-06 Closed Risk Ratio

| Business Unit | Closed / Total | Expected % |
|---|---:|---:|
| Operations | 380 / 2,503 | 15.18 |
| IT Infrastructure | 422 / 2,203 | 19.16 |
| Sales | 446 / 1,906 | 23.40 |
| Finance | 430 / 1,542 | 27.89 |
| Customer Service | 459 / 1,322 | 34.72 |
| HR | 391 / 1,031 | 37.92 |

Edge case: Business Unit ที่ปิดครบต้องแสดง 100% (ไม่หายจากผลลัพธ์)

---

## MV-007 — METRIC-07 Not Started Share

| Business Unit | Open / Unresolved | Expected % |
|---|---:|---:|
| Finance | 685 / 1,112 | 61.60 |
| HR | 363 / 640 | 56.72 |
| Operations | 1,143 / 2,123 | 53.84 |
| Sales | 770 / 1,460 | 52.74 |
| IT Infrastructure | 911 / 1,781 | 51.15 |
| Customer Service | 405 / 863 | 46.93 |

Edge case: Business Unit ที่ไม่มี Unresolved Risk ต้องได้ `NULL` ไม่ใช่ 0

---

## MV-008 — METRIC-08 Unresolved Risk Matrix

Expected (All Business Units), แถว = likelihood, คอลัมน์ = impact:

| L \\ I | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|
| 5 | 0 | 449 | 497 | 505 | 471 |
| 4 | 0 | 436 | 469 | 499 | 476 |
| 3 | 0 | 487 | 451 | 473 | 470 |
| 2 | 0 | 220 | 404 | 463 | 479 |
| 1 | 164 | 169 | 219 | 178 | 0 |

- ต้องมีครบ 25 ช่อง (ช่องว่าง = 0)
- ผลรวม = 7,979; filter HR ผลรวม = 640

# Dashboard Acceptance Tests

Acceptance tests ส่วนนี้ map กับ Acceptance Criteria `AC-01`–`AC-06` ใน `DASHBOARD_SPEC.md`

## DA-001 — Unresolved Risk by Business Unit

ตรวจว่า:
- chart render สำเร็จ
- ใช้ `METRIC-01`
- category = `business_unit`
- value = `unresolved_risk_count`
- sort descending
- ตัวเลขตรงกับ semantic output

---

## DA-002 — Risk by Priority Score

ตรวจว่า:
- chart ใช้ `METRIC-04`
- score ที่แสดงคือ `Risk Priority Score`
- ไม่มีการแปลงเป็น `Low/Medium/High/Critical` โดยไม่มี approved threshold
- Business Unit filter เปลี่ยนข้อมูลอย่างถูกต้อง

---

## DA-003 — Top 3 Risk Follow-up

ตรวจว่า table:
- มี 3 rows
- แสดง `risk_title`
- แสดง `risk_priority_score`
- แสดง `owner`
- ลำดับตรงกับ `METRIC-05`
- tie-break ตรงกับ `risk_id ASC`

---

## DA-004 — Cross-filter Consistency

เมื่อเลือก Business Unit:

- Business Unit bar
- Priority Score chart
- Risk detail
- Top 3

ต้องใช้ filter context เดียวกัน

---

## DA-005 — Snapshot Consistency

ทุก visualization บน dashboard view เดียวกันต้องใช้ snapshot เดียวกัน

ห้ามแสดง:

```text
chart A = snapshot N
chart B = snapshot N-1
```

---

## DA-006 — Accessibility

ตรวจอย่างน้อย:
- chart title
- accessible text/alt text
- keyboard navigation สำหรับ interactive controls
- state ไม่สื่อด้วยสีอย่างเดียว
- table header มี semantic labels

# Test Automation and CI

## Test Execution Stages

### Pull Request / Change Validation

รัน:
- SQL/unit tests
- schema tests
- relationship tests
- transformation logic tests
- metric golden-dataset tests ที่ได้รับผลกระทบ

### Pre-deployment

รัน:
- full unit test suite
- integration tests
- schema-drift fixture
- idempotency test
- metric validation suite

### Post-deployment / Pipeline Runtime

รัน:
- `DATA_QUALITY.md` assertions
- row/aggregate reconciliation
- latest snapshot publication checks

- dashboard acceptance suite (`DA-001`–`DA-006`)

## Blocking Tests

สิ่งต่อไปนี้ block deployment / publication:

- quality rule ที่มี `rule_severity = error`
- unit test fail
- grain uniqueness fail
- referential-integrity error
- schema breaking-change test fail
- idempotency fail
- metric golden-dataset result ไม่ตรง
- aggregate reconciliation ไม่ตรง
- pipeline snapshot consistency fail

## Warning-only Tests

quality rule ที่มี `rule_severity = warning`:

- alert owner
- บันทึก test result
- ไม่ block deployment โดยอัตโนมัติ

ตัวอย่างจาก current `DATA_QUALITY.md`:
- missing owner
- anomaly checks หลังมี calibrated threshold ตาม severity ที่กำหนด

## Coverage Expectation

**Coverage target:** `null`

**Calibration Owner:** Analytics Engineering / Data Engineering

**Calibration Source:**  
หลังมี test inventory จริงใน repository ให้วัด coverage อย่างน้อยตาม:
- models covered
- quality rules covered
- metric logic covered
- pipeline critical paths covered

เหตุผลที่ยังไม่กำหนดเปอร์เซ็นต์คือยังไม่มี implementation repository/test inventory สำหรับสร้าง baseline ที่พิสูจน์ได้

อย่างไรก็ตามมี minimum structural gate ที่กำหนดได้ทันที:

- ทุก fact table ต้องมี test อย่างน้อย 1 ตัว
- ทุก `DATA_QUALITY.md` rule ต้อง map ไปยัง test/monitoring assertion
- ทุก metric ต้องมี metric validation test
- critical pipeline path ต้องมี integration test
- idempotency ต้องถูก test

## Orchestration Integration

pipeline orchestration tool:

`null`

CI/CD platform:

`null`

**Decision Owner:** Data Engineering

เมื่อ tooling ถูกเลือก ต้อง integrate test execution กับ orchestrator โดย:
- test stage ต้องสำเร็จก่อน publish semantic snapshot
- failing blocking test ต้องหยุด downstream publication
- test result ต้องเก็บให้ trace กลับไปยัง pipeline run/snapshot ได้
