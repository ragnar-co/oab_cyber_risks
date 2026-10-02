# Metric Profiles

## METRIC-01 — Unresolved Risk Count

**metric_status:** draft  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
จำนวน Risk ที่ยังไม่ได้ปิดตาม business definition ของโปรเจกต์

**Formula**  
นับ `risk_id` ที่ `status != 'closed'`

`COUNT(risk_id WHERE status != 'closed')`

**Grain**  
`1 business_unit × 1 source update snapshot`

**Required Filters**
- `status != 'closed'`

**Optional Filters**
- `business_unit`
- `risk_priority_score`
- `owner`

**Segment Breakdowns**
- `business_unit`
- `risk_priority_score`

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

---

## METRIC-02 — Unresolved Risk Share by Business Unit

**metric_status:** draft  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
สัดส่วน Unresolved Risk ของแต่ละ Business Unit เทียบกับ Unresolved Risk ทั้งหมด

**Formula**

`Unresolved Risk Share = BU Unresolved Risk Count / Total Unresolved Risk Count × 100`

**Numerator**
จำนวน `risk_id` ที่ `status != 'closed'` ของ Business Unit นั้น

**Denominator**
จำนวน `risk_id` ที่ `status != 'closed'` ของทุก Business Unit

**Grain**  
`1 business_unit × 1 source update snapshot`

**Required Filters**
- `status != 'closed'`

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

---

## METRIC-03 — Risk Priority Score

**metric_status:** draft  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
คะแนนที่ใช้เรียงลำดับ Risk เพื่อสนับสนุนการตัดสินใจว่ารายการใดควรถูกติดตามก่อน

**Formula**

`Risk Priority Score = likelihood × impact`

**Grain**  
`1 risk_id × 1 source update snapshot`

**Required Filters**
- สำหรับ dashboard ติดตาม: `status != 'closed'`

**Segment Breakdowns**
- `business_unit`
- `owner`

**Interpretation**
คะแนนที่สูงกว่าถูกเรียงก่อนคะแนนที่ต่ำกว่า

คะแนนนี้ยังไม่ถูกแปลงเป็น bucket เช่น `Low`, `Medium`, `High`, `Critical`

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

---

## METRIC-04 — Unresolved Risk Count by Priority Score

**metric_status:** draft  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
จำนวน Unresolved Risk จำแนกตาม `Risk Priority Score` เพื่อแสดงการกระจายของระดับคะแนนความเสี่ยง

**Formula**

`COUNT(risk_id WHERE status != 'closed') GROUP BY business_unit, risk_priority_score`

**Grain**  
`1 business_unit × 1 risk_priority_score × 1 source update snapshot`

**Required Filters**
- `status != 'closed'`

**Optional Filters**
- `business_unit`
- `owner`

**Segment Breakdowns**
- `business_unit`
- `risk_priority_score`

**Dashboard Use**
รองรับกราฟ “จำนวนความเสี่ยงที่ยังไม่ปิด แยกตามหน่วยงานและระดับความเสี่ยง”

ใน version นี้คำว่า “ระดับความเสี่ยง” หมายถึง `Risk Priority Score` โดยตรง ไม่ใช่ risk-level bucket

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

---

## METRIC-05 — Top Risk Follow-up Rank

**metric_status:** draft  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
ลำดับของ Unresolved Risk สำหรับใช้เลือก 3 รายการแรกที่ management ควรเห็นเพื่อประกอบการติดตาม

**Ranking Formula — Plain Language**
1. เลือกเฉพาะ Risk ที่ยังไม่ปิด
2. คำนวณ `Risk Priority Score`
3. เรียง `Risk Priority Score` จากมากไปน้อย
4. หากคะแนนเท่ากัน ใช้ `risk_id` เป็น technical tie-break เพื่อให้ผลลัพธ์ deterministic
5. เลือก 3 records แรก

**Notation**

`RANK ORDER BY (likelihood × impact) DESC, risk_id ASC`

**Grain**  
`1 risk_id × 1 source update snapshot`

**Required Filters**
- `status != 'closed'`

**Required Output Fields**
- `risk_title`
- `risk_priority_score`
- `owner`

**Supporting Fields**
- `risk_id`
- `business_unit`
- `likelihood`
- `impact`

**Display Rule**
- `LIMIT 3`

**Tie-break Note**
`risk_id ASC` เป็น technical tie-break เท่านั้น ไม่ได้หมายความว่า Risk ที่มี `risk_id` ต่ำกว่ามี business priority สูงกว่าเมื่อคะแนนเท่ากัน

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

## METRIC-06 — Closed Risk Ratio by Business Unit

**metric_status:** draft  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
สัดส่วน Risk ที่ปิดแล้วต่อ Risk ทั้งหมดของแต่ละ Business Unit ณ snapshot หนึ่ง ใช้เปรียบเทียบความคืบหน้าการจัดการ Risk ระหว่างหน่วยงาน

**Formula**

`Closed Risk Ratio = COUNT(risk_id WHERE status = 'closed') / COUNT(risk_id) × 100`

**Grain**  
`1 business_unit × 1 source update snapshot`

**Required Filters**
- `status IS NOT NULL`

**Interpretation**
- เป็นสถานะสะสม ณ snapshot ไม่ใช่ความเร็วในการปิด (closure velocity) เพราะ source ไม่มีวันที่เปิด/ปิด
- ค่าต่ำอาจมาจาก Risk ใหม่จำนวนมาก ไม่ใช่การจัดการช้าเสมอไป — ต้องอ่านคู่กับ METRIC-01

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

---

## METRIC-07 — Not Started Share of Unresolved Risk

**metric_status:** draft — definition pending confirmation  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
สัดส่วนของ Unresolved Risk ที่ยังไม่เริ่มดำเนินการ ในแต่ละ Business Unit

**Formula**

`Not Started Share = COUNT(risk_id WHERE status = 'open') / COUNT(risk_id WHERE status != 'closed') × 100`

**Grain**  
`1 business_unit × 1 source update snapshot`

**Required Filters**
- `status != 'closed'` (denominator)

**Zero-denominator rule**  
Business Unit ที่ไม่มี Unresolved Risk ให้ค่าเป็น `NULL` และไม่แสดงในกราฟ (ไม่ใช่ 0%)

**Pending Confirmation**  
ความหมาย `status = 'open'` = "ยังไม่เริ่มดำเนินการ" เป็นการตีความจาก observed values (`open` / `in_progress` / `closed`) ยังไม่ได้รับการยืนยันจาก management หรือ source-system owner

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

---

## METRIC-08 — Unresolved Risk Matrix (Likelihood × Impact)

**metric_status:** draft  
**version:** 1.0  
**parent_kpi:** Unresolved Cyber Risk Exposure  
**owner:** management  
**primary_consumer:** management  
**refresh_cadence:** ทุกครั้งที่ source data มีการ update

**Business Definition**  
จำนวน Unresolved Risk ในแต่ละช่องของ likelihood × impact เพื่อแยก Risk ที่มี `Risk Priority Score` เท่ากันแต่ต่างองค์ประกอบ (เช่น L5×I2 กับ L2×I5 = 10)

**Formula**

`COUNT(risk_id WHERE status != 'closed') GROUP BY likelihood, impact`

**Grain**  
`1 likelihood × 1 impact × 1 source update snapshot` (optional Business Unit filter)

**Required Filters**
- `status != 'closed'`

**Optional Filters**
- `business_unit`

**Axis Rule**  
ใช้ค่า likelihood / impact ที่พบใน snapshot ปัจจุบัน ไม่สมมติ range 1–5 เพราะ contractual range ยังเป็น `null` (`DATA_CONTRACT.md`) ช่องที่ไม่มี Risk แสดง 0

**Action Threshold**
- warning: `null`
- critical: `null`
- calibration_owner: management

ไม่มีการระบายสีช่องตามระดับความเสี่ยงจนกว่าจะมี approved bucket rule

# Formula Reference

| Metric | Formula |
|---|---|
| Unresolved Risk Count | `COUNT(risk_id WHERE status != 'closed')` |
| Unresolved Risk Share by Business Unit | `BU unresolved / total unresolved × 100` |
| Risk Priority Score | `likelihood × impact` |
| Unresolved Risk Count by Priority Score | `COUNT(unresolved risk_id) GROUP BY business_unit, risk_priority_score` |
| Top Risk Follow-up Rank | `ORDER BY risk_priority_score DESC, risk_id ASC` |
| Closed Risk Ratio by Business Unit | `closed / total × 100` |
| Not Started Share of Unresolved Risk | `open / unresolved × 100` |
| Unresolved Risk Matrix | `COUNT(unresolved risk_id) GROUP BY likelihood, impact` |

# Grain and Filter Matrix

| Metric | Grain | Required Filter | Segment / Output |
|---|---|---|---|
| Unresolved Risk Count | `1 business_unit × 1 snapshot` | `status != 'closed'` | `business_unit` |
| Unresolved Risk Share by Business Unit | `1 business_unit × 1 snapshot` | `status != 'closed'` | `business_unit` |
| Risk Priority Score | `1 risk_id × 1 snapshot` | dashboard: `status != 'closed'` | `business_unit`, `owner` |
| Unresolved Risk Count by Priority Score | `1 business_unit × 1 risk_priority_score × 1 snapshot` | `status != 'closed'` | `business_unit`, `risk_priority_score` |
| Top Risk Follow-up Rank | `1 risk_id × 1 snapshot` | `status != 'closed'` | `risk_title`, `risk_priority_score`, `owner` |
| Closed Risk Ratio by Business Unit | `1 business_unit × 1 snapshot` | `status IS NOT NULL` | `business_unit` |
| Not Started Share of Unresolved Risk | `1 business_unit × 1 snapshot` | `status != 'closed'` | `business_unit` |
| Unresolved Risk Matrix | `1 likelihood × 1 impact × 1 snapshot` | `status != 'closed'` | `likelihood`, `impact` |

# Action Thresholds

| Metric | Warning Threshold | Critical Threshold | Calibration Owner |
|---|---|---|---|
| Unresolved Risk Count | `null` | `null` | management |
| Unresolved Risk Share by Business Unit | `null` | `null` | management |
| Risk Priority Score | `null` | `null` | management |
| Unresolved Risk Count by Priority Score | `null` | `null` | management |
| Top Risk Follow-up Rank | `null` | `null` | management |
| Closed Risk Ratio by Business Unit | `null` | `null` | management |
| Not Started Share of Unresolved Risk | `null` | `null` | management |
| Unresolved Risk Matrix | `null` | `null` | management |

ไม่มีการกำหนด threshold หรือ risk-level bucket จนกว่าจะผ่าน calibration และได้รับการอนุมัติจาก management
