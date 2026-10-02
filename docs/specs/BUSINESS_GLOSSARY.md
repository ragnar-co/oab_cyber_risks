# Term Definitions

| Term | Official Definition | Common Misunderstanding | Authoritative Source |
|---|---|---|---|
| Risk | รายการความเสี่ยงด้าน cyber หนึ่งรายการที่ระบุด้วย `risk_id` ใน source data | อาจถูกเข้าใจว่าเท่ากับ vulnerability, incident หรือ finding โดยอัตโนมัติ | Source schema `oab_cyber_risks_2_5mb.csv` |
| Unresolved Risk | รายการ Risk ที่มี `status != closed` | อาจเข้าใจว่า unresolved หมายถึงเฉพาะ `status = open` แต่โปรเจกต์นี้รวมทุกสถานะที่ยังไม่เป็น `closed` | Business decision: management, 2026-10-02 |
| Business Unit | หน่วยงานที่รายการ Risk ถูกบันทึกหรือ assign อยู่ ตามค่าใน field `business_unit` | ไม่ได้หมายความโดยอัตโนมัติว่าเป็นหน่วยงานที่ได้รับผลกระทบ หรือเป็น organizational owner ในทุกบริบท | Business decision: management, 2026-10-02; Source field `business_unit` |
| Risk Owner | ผู้รับผิดชอบที่ถูกบันทึกใน field `owner` ของรายการ Risk | ไม่ควรสรุปว่าเป็นเจ้าของ Business Unit หรือผู้อนุมัติการปิด Risk โดยไม่มีข้อมูลเพิ่มเติม | Source field `owner` |
| Likelihood | ค่าที่ใช้แทนองค์ประกอบด้านโอกาสเกิดของ Risk ตาม field `likelihood` | ค่าใน field นี้ไม่ควรถูกตีความนอก scoring rule ของโปรเจกต์ | Source field `likelihood` |
| Impact | ค่าที่ใช้แทนองค์ประกอบด้านผลกระทบของ Risk ตาม field `impact` | ค่าใน field นี้ไม่ควรถูกตีความนอก scoring rule ของโปรเจกต์ | Source field `impact` |
| Closed Risk Ratio | สัดส่วน Risk ที่ `status = closed` ต่อ Risk ทั้งหมดของหน่วยงาน ณ snapshot | อาจเข้าใจว่าเป็นความเร็วในการปิด (closure velocity) แต่เป็นสถานะสะสม ณ snapshot เท่านั้น | `METRIC_SPEC.md` METRIC-06 |
| Not Started Risk | Unresolved Risk ที่ `status = open` — **pending confirmation** | `open` อาจหมายถึงสถานะอื่นในระบบต้นทาง (เช่น เปิดและ assign แล้ว) | Observed sample values; รอ management / source-system owner ยืนยัน |
| Risk Priority | ค่าที่ใช้จัดลำดับรายการ Risk สำหรับการติดตาม โดยคำนวณจาก `Likelihood × Impact` | ไม่ใช่ KPI และไม่ใช่ `data_need_priority`; เป็นค่าเชิงวิเคราะห์ระดับ Risk record | Business decision: management, 2026-10-02 |

# Disputed Terms

| Disputed Term | Competing Definitions | Official Resolution | Approval Date | Decision Owner |
|---|---|---|---|---|
| Unresolved Risk | เฉพาะ `open` หรือทุกสถานะที่ไม่ใช่ `closed` | `status != closed` | 2026-10-02 | management |
| Business Unit | หน่วยงานเจ้าของ / หน่วยงานได้รับผลกระทบ / หน่วยงานที่รายการถูก assign อยู่ | หน่วยงานที่รายการ Risk ถูกบันทึกหรือ assign อยู่ | 2026-10-02 | management |
| Risk Priority | ใช้ likelihood / impact / combination / business rule อื่น | `Likelihood × Impact` | 2026-10-02 | management |
| Not Started Risk | `status = open` = ยังไม่เริ่ม / `open` เป็นเพียงสถานะเปิด | `null` — pending | `null` | management + source-system owner |

# Change Log

| Changed Term | Change Date | Old Definition | New Definition | Reason |
|---|---|---|---|---|
| Unresolved Risk | 2026-10-02 | Definition ยังไม่ตัดสิน | `status != closed` | management ยืนยัน business rule |
| Business Unit | 2026-10-02 | Semantic meaning ยังไม่ตัดสิน | หน่วยงานที่รายการ Risk ถูกบันทึกหรือ assign อยู่ | management ยืนยัน |
| Risk Priority | 2026-10-02 | Priority formula ยังไม่ตัดสิน | `Likelihood × Impact` | management ยืนยัน |

# Enumeration Registry

| Enum | Owner Document |
|---|---|
| `data_literacy_level` | `STAKEHOLDERS.md` |
| `data_need_priority` | `STAKEHOLDERS.md` |
| `scd_type` | `DATA_MODEL_SPEC.md` |
| `pdpa_classification` | `DATA_MODEL_SPEC.md` |
| `rule_severity` | `DATA_QUALITY.md` |
| `dataset_criticality` | `SLA_FRESHNESS.md` |
| `chart_type` | `VIZ_DESIGN_SPEC.md` |
| `complexity_level` | `VIZ_DESIGN_SPEC.md` |
| `metric_status` | `METRIC_SPEC.md` |
| `model_status` | `AI_MODEL_SPEC.md` |
| `work_item_status` | `TASKS.md` |
| `incident_severity` | `RUNBOOK.md` |
| `change_type` | `ANALYTICS_CHANGELOG.md` |
