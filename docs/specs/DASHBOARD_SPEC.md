# Dashboard Inventory

| Dashboard Name | Version | Tool / Platform | Access Path | Owner |
|---|---|---|---|---|
| Client Cyber Risk Dashboard | `1.0-draft` | `null` | `null` | management / Analytics |

## Scope

Dashboard นี้รองรับ KPI:

`Unresolved Cyber Risk Exposure`

และตอบ Critical Questions หลัก:

1. ความเสี่ยงที่ยังไม่ปิดกระจุกอยู่ที่หน่วยงานใด
2. รายการความเสี่ยงใดควรถูกติดตามก่อน

## Current Platform Decisions

| Item | Value | Decision Owner |
|---|---|---|
| BI Tool | `null` | Analytics / Project Owner |
| Production URL | `null` | Analytics / Platform |
| Authentication Method | `null` | Platform / Security |
| Production Data Connection | `null` | Data Engineering |

# Dashboard Profiles

## Client Cyber Risk Dashboard

**Purpose**

ให้ management เห็นภาพรวมของ Unresolved Cyber Risk จาก snapshot ล่าสุด โดยเน้น:

- การกระจุกตัวของ Risk ตาม Business Unit
- การกระจายของ `Risk Priority Score`
- รายการ Top 3 ที่ควรถูกติดตามก่อน

**Target User**

`management`

**Primary KPI**

`Unresolved Cyber Risk Exposure`

**Data Sources**

- `fact_unresolved_risk_unit_snapshot`
- `fact_unresolved_risk_score_snapshot`
- `fact_risk_snapshot`
- `dim_business_unit`
- `dim_owner`

## Dashboard Layout

### Section 1 — Executive Overview

#### CHART-01 — Total Unresolved Risk

**Metric**

`Unresolved Risk Count`

**chart_type**

`kpi_card`

**complexity_level**

`basic`

**Display**

ยอดรวม Unresolved Risk ของ latest snapshot

**Source**

`fact_unresolved_risk_unit_snapshot`

**Calculation**

ผลรวม `unresolved_risk_count` ของ Business Units ใน snapshot เดียวกัน

---

### Section 2 — Risk Concentration

#### CHART-02 — Unresolved Risk by Business Unit

**Metric**

`Unresolved Risk Count`

**chart_type**

`bar`

**complexity_level**

`basic`

**Category**

`business_unit`

**Value**

`unresolved_risk_count`

**Sort**

`unresolved_risk_count DESC`

**Purpose**

ตอบคำถาม:

“ความเสี่ยงที่ยังไม่ปิดกระจุกอยู่ที่หน่วยงานใด”

**Source**

- `fact_unresolved_risk_unit_snapshot`
- `dim_business_unit`

---

#### CHART-03 — Unresolved Risk Share by Business Unit

**Metric**

`Unresolved Risk Share by Business Unit`

**chart_type**

`bar`

**complexity_level**

`basic`

**Category**

`business_unit`

**Value**

`unresolved_risk_share`

**Format**

percentage

**Sort**

`unresolved_risk_share DESC`

**Source**

- `fact_unresolved_risk_unit_snapshot`
- `dim_business_unit`

---

### Section 3 — Risk Priority Distribution

#### CHART-04 — Unresolved Risk by Priority Score

**Metric**

`Unresolved Risk Count by Priority Score`

**chart_type**

`bar`

**complexity_level**

`basic`

**Category**

`risk_priority_score`

**Value**

`unresolved_risk_count`

**Business Unit Context**

สามารถ filter ด้วย `business_unit`

**Purpose**

แสดงจำนวน Risk ที่ยังไม่ปิดตามระดับ `Risk Priority Score`

**Important Interpretation**

ใน version ปัจจุบัน “ระดับความเสี่ยง” หมายถึงคะแนน:

`Risk Priority Score = likelihood × impact`

Dashboard ห้ามแปลงคะแนนเป็น:

- Low
- Medium
- High
- Critical

จนกว่าจะมี approved/calibrated bucket rule

**Source**

`fact_unresolved_risk_score_snapshot`

---

### Section 4 — Priority Follow-up

#### CHART-05 — Top 3 Risks to Follow Up

**Metric**

`Top Risk Follow-up Rank`

**chart_type**

`table`

**complexity_level**

`basic`

**Rows**

3

**Columns**

| Display Column | Source |
|---|---|
| Rank | `follow_up_rank` |
| Risk | `risk_title` |
| Score | `risk_priority_score` |
| Owner | `owner_id` |

**Canonical Sort**

`risk_priority_score DESC, risk_id ASC`

`risk_id ASC` เป็น technical tie-break เท่านั้น

**Source**

- `fact_risk_snapshot`
- `dim_owner`

### Section 5 — Risk Management Progress

#### CHART-06 — Closed Risk Ratio by Business Unit

**Metric** `Closed Risk Ratio by Business Unit` · **chart_type** `bar` · **complexity_level** `basic`

**Value** `closed_risk_ratio` (percentage) · **Sort** DESC · **Source** `fact_risk_snapshot`, `dim_business_unit`

แสดงทุก Business Unit เสมอ; Business Unit filter = highlight

---

#### CHART-07 — Not Started Share of Unresolved Risk

**Metric** `Not Started Share of Unresolved Risk` · **chart_type** `bar` · **complexity_level** `basic`

**Value** `not_started_share` (percentage) · **Sort** DESC · **Source** `fact_risk_snapshot`, `dim_business_unit`

แสดงทุก Business Unit ที่มี Unresolved Risk; Business Unit filter = highlight · นิยาม `open` = ยังไม่เริ่มดำเนินการ รอยืนยัน

---

### Section 6 — Risk Matrix

#### CHART-08 — Unresolved Risk Matrix

**Metric** `Unresolved Risk Matrix` · **chart_type** `table` · **complexity_level** `basic`

แถว likelihood, คอลัมน์ impact, ค่า `unresolved_risk_count` · ตอบสนองต่อ Business Unit filter · ไม่ระบายสี

**Source** `fact_risk_snapshot`

## Chart Inventory

| Chart ID | Metric | chart_type | Supported VIZ Matrix Entry |
|---|---|---|---|
| CHART-01 | Unresolved Risk Count | `kpi_card` | basic KPI card rule |
| CHART-02 | Unresolved Risk Count | `bar` | VIZ-01 |
| CHART-03 | Unresolved Risk Share by Business Unit | `bar` | VIZ-02 |
| CHART-04 | Unresolved Risk Count by Priority Score | `bar` | VIZ-04 |
| CHART-05 | Top Risk Follow-up Rank | `table` | VIZ-05 |
| CHART-06 | Closed Risk Ratio by Business Unit | `bar` | VIZ-06 |
| CHART-07 | Not Started Share of Unresolved Risk | `bar` | VIZ-07 |
| CHART-08 | Unresolved Risk Matrix | `table` | VIZ-08 |

## Acceptance Criteria

### AC-01 — Business Unit Risk Chart

ต้องผ่าน `DA-001` จาก `TESTING_STRATEGY.md`

- chart render สำเร็จ
- ใช้ `Unresolved Risk Count`
- category คือ Business Unit
- count ตรงกับ semantic dataset
- sort จากมากไปน้อย

### AC-02 — Priority Score Distribution

ต้องผ่าน `DA-002`

- ใช้ `Unresolved Risk Count by Priority Score`
- แสดง score ตาม canonical definition
- ไม่มี unapproved risk-level bucket
- Business Unit filter ให้ผลถูกต้อง

### AC-03 — Top 3 Risk

ต้องผ่าน `DA-003`

- มี 3 rows
- แสดง `risk_title`
- แสดง `risk_priority_score`
- แสดง `owner`
- rank ตรงกับ canonical `Top Risk Follow-up Rank`

### AC-04 — Filter Synchronization

ต้องผ่าน `DA-004`

เมื่อเลือก Business Unit chart ที่เกี่ยวข้องทั้งหมดต้องใช้ filter context เดียวกัน

### AC-05 — Snapshot Consistency

ต้องผ่าน `DA-005`

ทุก chart บน dashboard view เดียวกันต้องมาจาก snapshot เดียวกัน

### AC-06 — Accessibility

ต้องผ่าน `DA-006`

อย่างน้อยต้องมี:

- chart title
- accessible text
- keyboard-accessible controls
- semantic table headers
- ไม่พึ่งสีเพียงอย่างเดียวในการสื่อความหมาย

# Metric Coverage Matrix

ชื่อ metric ใน matrix นี้ใช้ชื่อตรงจาก `METRIC_SPEC.md` ห้ามสร้าง dashboard alias

| KPI | Metric | Client Cyber Risk Dashboard | Visualization |
|---|---|---:|---|
| Unresolved Cyber Risk Exposure | Unresolved Risk Count | Yes | CHART-01, CHART-02 |
| Unresolved Cyber Risk Exposure | Unresolved Risk Share by Business Unit | Yes | CHART-03 |
| Unresolved Cyber Risk Exposure | Risk Priority Score | Yes | Supporting field / CHART-05 |
| Unresolved Cyber Risk Exposure | Unresolved Risk Count by Priority Score | Yes | CHART-04 |
| Unresolved Cyber Risk Exposure | Top Risk Follow-up Rank | Yes | CHART-05 |
| Unresolved Cyber Risk Exposure | Closed Risk Ratio by Business Unit | Yes | CHART-06 |
| Unresolved Cyber Risk Exposure | Not Started Share of Unresolved Risk | Yes | CHART-07 |
| Unresolved Cyber Risk Exposure | Unresolved Risk Matrix | Yes | CHART-08 |

## KPI Coverage

`Unresolved Cyber Risk Exposure`

มี coverage ใน `Client Cyber Risk Dashboard`

ดังนั้น KPI ที่เรากำหนดไว้ใน `KPI_DICTIONARY.md` มี dashboard consumption แล้ว

# Drill-down Logic

## Global Filter Context

### Business Unit

ผู้ใช้สามารถเลือก:

`business_unit`

จาก CHART-02 หรือ dashboard filter

เมื่อเลือกแล้ว ต้อง filter:

- CHART-03
- CHART-04
- CHART-05

ให้ใช้ Business Unit เดียวกัน

CHART-01 สามารถแสดงค่าใน current filter context ได้

CHART-06 และ CHART-07 แสดงทุก Business Unit เสมอ (highlight หน่วยงานที่เลือก) CHART-08 ใช้ filter เดียวกับ CHART-04

---

## Drill-down Path 1 — Business Unit → Risk Distribution

```text
Unresolved Risk by Business Unit
        ↓ select business_unit
Unresolved Risk by Priority Score
```

ตัวอย่าง behavior:

ผู้ใช้ click Business Unit หนึ่งหน่วยงาน

CHART-04 ต้องเปลี่ยนเป็น distribution ของ Risk Priority Score เฉพาะหน่วยงานนั้น

---

## Drill-down Path 2 — Business Unit → Top Risk

```text
Business Unit
      ↓
Top 3 Risks to Follow Up
```

เมื่อ filter Business Unit:

Top 3 ต้องคำนวณใหม่ภายใน filter context

ไม่ใช่แค่เอา Global Top 3 มา filter หลัง ranking

canonical sequence คือ:

```text
filter unresolved risks
→ filter business_unit
→ calculate / select risk_priority_score
→ rank
→ select Top 3
```

---

## Drill-down Path 3 — Priority Score → Risk Detail

```text
Risk Priority Score
        ↓
Risk-level detail
```

เมื่อเลือก score ใน CHART-04 สามารถแสดงรายละเอียดที่ grain:

`risk_id × snapshot`

fields อย่างน้อย:

- `risk_title`
- `business_unit`
- `risk_priority_score`
- `owner`

การเปิด detailed Risk view เป็น interaction ระดับ `basic` ผ่าน table/filter context ไม่เพิ่ม custom visualization

---

## Filter State

ทุก chart ต้องแสดง filter context ปัจจุบันอย่างเห็นได้ชัด

ตัวอย่าง:

```text
Business Unit: Operations
Snapshot: <latest snapshot timestamp>
```

ผู้ใช้ต้องสามารถ reset filter กลับเป็น All Business Units ได้

---

## Interaction Constraints

Dashboard ต้องทำตาม `VIZ_DESIGN_SPEC.md`:

- bar click → filter
- table → sortable/filterable ตามที่กำหนด
- Top 3 executive table ไม่อนุญาตให้ user เปลี่ยน canonical ranking
- ไม่มี animation
- ไม่มี multi-axis
- ไม่มี unapproved custom visualization

# Refresh Schedule

## Business Refresh Requirement

Business expectation:

`ทุกครั้งที่ source data มีการ update`

และ stakeholder ต้องการเห็นข้อมูลใหม่:

`ทันที`

แต่คำว่า `ทันที` ยังไม่ใช่ calibrated technical SLA

ดังนั้น:

| Item | Value | Calibration Owner |
|---|---|---|
| Source update cadence | `null` | source-system owner |
| Pipeline cron / trigger | `null` | Data Engineering |
| Dashboard refresh trigger | หลัง semantic snapshot สำเร็จ | Data Engineering / Analytics |
| Maximum freshness delay | `null` | Data Engineering + management |

## Publication Sequence

Dashboard ต้อง refresh หลัง snapshot ใหม่ผ่านทั้งหมด:

1. pipeline สำเร็จ
2. blocking `DATA_QUALITY.md` rules ผ่าน
3. semantic facts/aggregates ถูกสร้างครบ
4. blocking tests ผ่าน
5. snapshot ถูก publish
6. dashboard refresh

ห้าม dashboard refresh จาก partial snapshot

## Snapshot Rule

ทุก chart ต้องใช้:

`latest successfully published snapshot`

ไม่ใช่เพียง:

`MAX(snapshot_at)`

หาก snapshot ล่าสุดสร้างไม่ครบหรือ quality gate fail ต้องใช้ last successfully published snapshot ตาม operational policy

Implementation: เลือกจาก `snapshot_registry WHERE publication_status = 'published'` ตาม Common Current-Snapshot Rule ใน `METRIC_LOGIC.md` ทุก chart ใช้ snapshot ที่ได้จาก query เดียวกันนี้

## Refresh Timestamp

Dashboard ต้องแสดง:

`Data last updated: <snapshot timestamp>`

เพื่อให้ management รู้ว่ากำลังตัดสินใจจากข้อมูลรอบใด

## Performance Budget

ค่าต่อไปนี้ยังไม่มี production measurement:

| Performance Requirement | Value | Calibration Owner |
|---|---|---|
| Initial dashboard load time | `null` | Analytics / BI Platform |
| Filter response time | `null` | Analytics / BI Platform |
| Drill-down response time | `null` | Analytics / BI Platform |
| Concurrent management users | `null` | Platform / Project Owner |

Calibration Source:

- production BI telemetry
- expected meeting usage
- platform concurrency limits

ห้ามกำหนด performance threshold ขึ้นเองก่อนมี baseline หรือ platform requirement ที่ยืนยันแล้ว

## Performance Validation

ก่อน production release ต้อง:

- วัด initial load time
- วัด filter response
- วัด drill-down response
- ทดสอบ dashboard ด้วย expected concurrency
- บันทึก calibrated performance budget กลับมาในเอกสารนี้
