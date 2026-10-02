# Null and Completeness Checks

เอกสารนี้เป็น owner ของ `rule_severity`

ค่าที่ใช้ใน Project:

- `error` — quality failure ที่ block pipeline / ห้าม publish dataset ใหม่
- `warning` — quality failure ที่ alert แต่ pipeline สามารถทำงานต่อได้

## DQ-001 — Missing Risk ID

**table / column:** `fact_risk_snapshot.risk_id`  
**rule_type:** null check  
**severity:** `error`

**Expected Behavior**  
ทุก Risk record ต้องมี `risk_id` เพราะเป็นส่วนหนึ่งของ grain `risk_id × snapshot_at`

```sql
SELECT *
FROM fact_risk_snapshot
WHERE risk_id IS NULL;
```

**Pass Condition**  
query ต้องคืน 0 rows

**Action on Failure**
- block publication ของ snapshot
- quarantine invalid records
- alert Data Engineering
- investigate upstream source/contract violation

---

## DQ-002 — Missing Snapshot Timestamp

**table / column:** `fact_risk_snapshot.snapshot_at`  
**rule_type:** null check  
**severity:** `error`

```sql
SELECT *
FROM fact_risk_snapshot
WHERE snapshot_at IS NULL;
```

**Pass Condition**  
0 rows

**Action on Failure**
- block pipeline
- ไม่ publish snapshot
- investigate ingestion metadata generation

---

## DQ-003 — Required Metric Inputs Missing

**table / columns:** `fact_risk_snapshot.status`, `likelihood`, `impact`  
**rule_type:** completeness check  
**severity:** `error`

```sql
SELECT *
FROM fact_risk_snapshot
WHERE
    status IS NULL
    OR likelihood IS NULL
    OR impact IS NULL;
```

**Expected Behavior**  
ข้อมูลที่จะเข้าสู่ metric calculation ต้องมี input ที่จำเป็นครบ

**Action on Failure**
- block affected snapshot จาก metric publication
- quarantine records
- alert Data Engineering และ source-system owner

---

## DQ-004 — Missing Business Unit

**table / column:** `fact_risk_snapshot.business_unit_key`  
**rule_type:** completeness check  
**severity:** `error`

```sql
SELECT *
FROM fact_risk_snapshot
WHERE business_unit_key IS NULL;
```

**Reason**  
`METRIC-01`, `METRIC-02`, `METRIC-04` ต้องใช้ Business Unit เป็น dimension หลัก

**Action on Failure**
- block affected aggregates
- quarantine records
- investigate source `business_unit` หรือ dimension-key resolution

---

## DQ-005 — Missing Owner

**table / column:** `fact_risk_snapshot.owner_key`  
**rule_type:** completeness check  
**severity:** `warning`

```sql
SELECT *
FROM fact_risk_snapshot
WHERE owner_key IS NULL;
```

**Expected Behavior**  
Top Risk Follow-up ควรมี owner สำหรับ management

**Action on Failure**
- alert Analytics/Data Engineering
- สามารถ publish aggregate metrics ที่ไม่ใช้ owner ต่อได้
- Top 3 display ต้องระบุ record ที่ owner ไม่สมบูรณ์ตาม downstream handling

---

## Completeness Rate

Minimum completeness threshold สำหรับ field ต่าง ๆ:

`null`

**Calibration Source**
- observed production ingestion history

**Calibration Owner**
- Data Engineering + Data Governance

ห้ามสร้าง percentage threshold ก่อนมี production baseline

# Range and Validity Checks

## DQ-006 — Unresolved Flag Consistency

**table:** `fact_risk_snapshot`  
**rule_type:** validity check  
**severity:** `error`

Business rule:

`Unresolved Risk = status != 'closed'`

```sql
SELECT *
FROM fact_risk_snapshot
WHERE
    (status = 'closed' AND is_unresolved = TRUE)
    OR
    (status <> 'closed' AND is_unresolved <> TRUE);
```

**Pass Condition**  
0 rows

**Action on Failure**
- block pipeline
- investigate `int_risk_snapshot`
- do not publish affected metric datasets

---

## DQ-007 — Risk Priority Score Consistency

**table:** `fact_risk_snapshot`  
**rule_type:** validity check  
**severity:** `error`

Canonical rule:

`risk_priority_score = likelihood × impact`

```sql
SELECT *
FROM fact_risk_snapshot
WHERE
    likelihood IS NOT NULL
    AND impact IS NOT NULL
    AND risk_priority_score <> likelihood * impact;
```

**Pass Condition**  
0 rows

**Action on Failure**
- block publication
- investigate transformation logic

---

## DQ-008 — Likelihood Validity

**table / column:** `fact_risk_snapshot.likelihood`  
**rule_type:** range check  
**severity:** `error`

Contractual allowed range:

`null`

**Calibration Owner**
- source-system owner + management

จนกว่าจะยืนยัน allowed range ได้ จะตรวจได้เฉพาะ type/non-null จาก contract และ schema validation ไม่สร้าง numeric bound เอง

---

## DQ-009 — Impact Validity

**table / column:** `fact_risk_snapshot.impact`  
**rule_type:** range check  
**severity:** `error`

Contractual allowed range:

`null`

**Calibration Owner**
- source-system owner + management

ยังไม่มี approved numeric range

---

## DQ-010 — Duplicate Risk Grain

**table:** `fact_risk_snapshot`  
**rule_type:** validity / uniqueness  
**severity:** `error`

```sql
SELECT
    risk_id,
    snapshot_at,
    COUNT(*) AS row_count
FROM fact_risk_snapshot
GROUP BY
    risk_id,
    snapshot_at
HAVING COUNT(*) > 1;
```

**Pass Condition**  
0 rows

**Action on Failure**
- block publication
- investigate idempotent upsert logic ใน `PIPELINE_SPEC.md`
- rerun หลังแก้ duplicate cause

---

## DQ-011 — Business Unit Aggregate Grain Uniqueness

**table:** `fact_unresolved_risk_unit_snapshot`  
**severity:** `error`

```sql
SELECT
    business_unit_key,
    snapshot_at,
    COUNT(*) AS row_count
FROM fact_unresolved_risk_unit_snapshot
GROUP BY
    business_unit_key,
    snapshot_at
HAVING COUNT(*) > 1;
```

**Pass Condition**  
0 rows

---

## DQ-012 — Priority Aggregate Grain Uniqueness

**table:** `fact_unresolved_risk_score_snapshot`  
**severity:** `error`

```sql
SELECT
    business_unit_key,
    risk_priority_score,
    snapshot_at,
    COUNT(*) AS row_count
FROM fact_unresolved_risk_score_snapshot
GROUP BY
    business_unit_key,
    risk_priority_score,
    snapshot_at
HAVING COUNT(*) > 1;
```

**Pass Condition**  
0 rows

# Referential Integrity Checks

ทุก FK pair จาก `DATA_MODEL_SPEC.md` ต้องมี executable assertion

## DQ-013 — Risk → Business Unit

**severity:** `error`

```sql
SELECT f.*
FROM fact_risk_snapshot AS f
LEFT JOIN dim_business_unit AS d
    ON f.business_unit_key = d.business_unit_key
WHERE
    f.business_unit_key IS NOT NULL
    AND d.business_unit_key IS NULL;
```

**Action on Failure**
- block publication
- investigate dimension build/key resolution

---

## DQ-014 — Risk → Owner

**severity:** `warning`

```sql
SELECT f.*
FROM fact_risk_snapshot AS f
LEFT JOIN dim_owner AS d
    ON f.owner_key = d.owner_key
WHERE
    f.owner_key IS NOT NULL
    AND d.owner_key IS NULL;
```

**Action on Failure**
- alert Data Engineering
- prevent affected record from appearing as valid Top 3 owner output
- aggregate metrics independent of owner may continue

---

## DQ-015 — Business Unit Aggregate → Business Unit Dimension

**severity:** `error`

```sql
SELECT f.*
FROM fact_unresolved_risk_unit_snapshot AS f
LEFT JOIN dim_business_unit AS d
    ON f.business_unit_key = d.business_unit_key
WHERE d.business_unit_key IS NULL;
```

**Action on Failure**
- block aggregate publication

---

## DQ-016 — Priority Aggregate → Business Unit Dimension

**severity:** `error`

```sql
SELECT f.*
FROM fact_unresolved_risk_score_snapshot AS f
LEFT JOIN dim_business_unit AS d
    ON f.business_unit_key = d.business_unit_key
WHERE d.business_unit_key IS NULL;
```

**Action on Failure**
- block aggregate publication

# Anomaly Detection Rules

Anomaly detection ต้องใช้ baseline จาก observed history เท่านั้น

ปัจจุบันยังไม่มี production history เพียงพอ ดังนั้น anomaly thresholds ทั้งหมดเป็น `null`

## DQ-017 — Source Row Count Anomaly

**metric**
- incoming row count per snapshot

**threshold**
- `null`

**Calibration Source**
- production row-count history

**Calibration Owner**
- Data Engineering

**severity**
- `warning`

**SQL Observation**

```sql
SELECT
    snapshot_at,
    COUNT(*) AS row_count
FROM fact_risk_snapshot
GROUP BY snapshot_at
ORDER BY snapshot_at;
```

เมื่อ calibration เสร็จ ต้องระบุ expected range จาก historical distribution ที่ตรวจสอบย้อนหลังได้

---

## DQ-018 — Unresolved Risk Count Anomaly

**metric**
- total unresolved risk count per snapshot

**threshold**
- `null`

**Calibration Source**
- observed production history

**Calibration Owner**
- management + Analytics

**severity**
- `warning`

```sql
SELECT
    snapshot_at,
    SUM(unresolved_risk_count) AS unresolved_risk_count
FROM fact_unresolved_risk_unit_snapshot
GROUP BY snapshot_at
ORDER BY snapshot_at;
```

ห้ามตั้ง percentage-change threshold จนกว่าจะมี history เพียงพอสำหรับ calibration

---

## DQ-019 — Risk Priority Distribution Anomaly

**metric**
- distribution ของ `risk_priority_score`

**threshold**
- `null`

**Calibration Source**
- observed production score distribution

**Calibration Owner**
- management + Analytics

**severity**
- `warning`

```sql
SELECT
    snapshot_at,
    risk_priority_score,
    SUM(unresolved_risk_count) AS risk_count
FROM fact_unresolved_risk_score_snapshot
GROUP BY
    snapshot_at,
    risk_priority_score
ORDER BY
    snapshot_at,
    risk_priority_score;
```

---

## DQ-020 — Upstream Schema Drift

**rule_type:** schema drift  
**severity:** `error`

Incoming source schema ต้องถูกเปรียบเทียบกับ `DATA_CONTRACT.md`

ต้องตรวจอย่างน้อย:
- required field หาย
- field rename
- incompatible type change
- unexpected structural change

**Expected Fields**

```text
risk_id
business_unit
risk_title
likelihood
impact
status
owner
```

**Action on Failure**
1. stop affected ingestion
2. quarantine incoming data
3. ห้าม publish semantic snapshot ใหม่
4. alert source-system owner และ Data Engineering
5. ประเมินว่าเป็น breaking contract change หรือไม่
6. หลังแก้แล้วจึง rerun pipeline

ห้าม silently cast หรือ rename เพื่อซ่อน contract-breaking schema drift

## DQ-021 — Likelihood / Impact Type Validity

**table / columns:** `stg_cyber_risk.likelihood`, `impact`  
**rule_type:** validity / type check  
**severity:** `error`

ค่าที่มีอยู่แต่ cast เป็น INTEGER ไม่ได้ (เช่น `"high"`) ถือเป็น contract violation ตาม `DATA_CONTRACT.md` Data Type Constraints ห้าม silently cast เป็น NULL แล้วโหลดต่อ

```sql
SELECT *
FROM stg_cyber_risk
WHERE
    (likelihood_raw IS NOT NULL AND TRY_CAST(likelihood_raw AS INTEGER) IS NULL)
    OR (impact_raw IS NOT NULL AND TRY_CAST(impact_raw AS INTEGER) IS NULL);
```

**Pass Condition**  
0 rows

**Action on Failure**
- block publication
- quarantine records
- alert source-system owner

---

## DQ-022 — Status Outside Observed Values

**table / column:** `stg_cyber_risk.status`  
**rule_type:** validity check  
**severity:** `warning`

Allowed set ของ `status` ยังไม่ถูกรับรองจาก Producer จึงตรวจเทียบกับค่าที่พบใน sample (`open`, `in_progress`, `closed`) เป็น warning เท่านั้น

เหตุผล: ค่าเช่น `Closed` หรือ `closed ` จะถูกนับเป็น Unresolved ตามกฎ `status != 'closed'` โดยไม่มีใครเห็น rule นี้ทำให้ปัญหาถูก alert

```sql
SELECT *
FROM stg_cyber_risk
WHERE status NOT IN ('open', 'in_progress', 'closed');
```

**Action on Failure**
- alert Data Engineering + source-system owner
- publish ต่อได้ (warning)
- เมื่อ Producer อนุมัติ allowed set แล้ว ให้ทบทวน severity

# Quality Dashboards

Quality Dashboard ต้องแสดงสถานะของ quality rules แยกจาก business dashboard

## Required Panels

### Pipeline Quality Status
แสดง:
- latest pipeline run
- snapshot ที่ตรวจ
- จำนวน `error` rules ที่ fail
- จำนวน `warning` rules ที่ fail

### Completeness

แสดง:
- null count ของ required fields
- missing `business_unit`
- missing `owner`

completeness target:

`null`

Calibration Owner:
- Data Engineering + Data Governance

### Referential Integrity

แสดง failed records จาก:
- DQ-013
- DQ-014
- DQ-015
- DQ-016

### Duplicate / Grain Violations

แสดง:
- duplicate `risk_id × snapshot_at`
- duplicate aggregate grains

### Anomaly Monitoring

แสดง observed history ของ:
- source row count
- unresolved risk count
- risk priority distribution

จนกว่า threshold จะ calibrate dashboard ต้องแสดง observations/history ได้ แต่ห้ามแสดงว่า anomaly “ผ่าน/ไม่ผ่าน” จาก threshold ที่ยังเป็น `null`

## Publication Gate

snapshot ใหม่สามารถ publish ไปยัง business dashboard ได้เมื่อ:

- ไม่มี `error` quality rule ที่ fail
- semantic facts/aggregates ของ snapshot เดียวกันสร้างครบ
- schema drift check ผ่าน

`warning` สามารถให้ pipeline เดินต่อได้ แต่ต้องถูกแสดงและ alert ตาม owner ของ rule
