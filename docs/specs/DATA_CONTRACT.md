# Contract Overview

## Purpose

Data Contract นี้กำหนด interface ระหว่างระบบต้นทางที่ผลิตข้อมูล Cyber Risk กับ analytics layer ของ Project `Client Cyber Risk Dashboard`

ขอบเขต contract นี้ครอบคลุมข้อมูล Risk ที่ analytics pipeline ต้องรับเข้าเพื่อรองรับ:

- การวิเคราะห์ Unresolved Risk แยกตาม Business Unit
- การคำนวณ `Risk Priority Score`
- การแสดง Top Risk Follow-up
- การแสดง `risk_title` และ `owner`

## Contract Parties

| Party | Responsibility | Owner |
|---|---|---|
| Producer | สร้างและส่งข้อมูล Cyber Risk ตาม schema ที่ระบุใน contract | `null` |
| Consumer | Analytics pipeline / semantic layer ของ `Client Cyber Risk Dashboard` | Data / Analytics team |
| Business Consumer | ใช้ผลลัพธ์ dashboard ในการตัดสินใจ | management |

**Producer Owner Resolution Owner:** management / source-system owner

## Contract Scope

Contracted source dataset:

`cyber_risk_source`

Source ตัวอย่างสำหรับ development:

`oab_cyber_risks_2_5mb.csv`

Contract นี้ครอบคลุม source fields เท่านั้น

Derived fields ต่อไปนี้อยู่นอก producer contract และสร้างใน analytics layer:

- `is_unresolved`
- `risk_priority_score`
- `snapshot_at`
- surrogate keys
- aggregate metric columns

## Contract Version

- Contract Version: `1.0-draft`
- Effective Date: `null`
- Approval Owner: management + source-system owner

Contract จะเปลี่ยนจาก `draft` เป็น effective เมื่อ Producer และ Consumer ยืนยัน schema และ SLA ร่วมกัน

# Schema Definitions

## cyber_risk_source

**Grain**

หนึ่ง record ต่อ `risk_id` ใน source update หนึ่งครั้ง

| Field Name | Data Type | Nullable | Contractual Allowed Values / Range | Usage |
|---|---|---:|---|---|
| `risk_id` | STRING | No | unique Risk identifier; exact format not contractually fixed | business key |
| `business_unit` | STRING | No | `null` — ต้องยืนยันกับ source owner | dimension |
| `risk_title` | STRING | No | free text | Top Risk display |
| `likelihood` | INTEGER | No | `null` — ต้องยืนยัน contractual range | `Risk Priority Score` input |
| `impact` | INTEGER | No | `null` — ต้องยืนยัน contractual range | `Risk Priority Score` input |
| `status` | STRING | No | `null` — ต้องยืนยัน contractual allowed set | Unresolved Risk logic |
| `owner` | STRING | No | source owner identifier | Top Risk display |

### Observed Sample Values

ข้อมูลต่อไปนี้เป็นเพียงสิ่งที่พบใน source ตัวอย่าง ไม่ถือเป็น contract constraint จนกว่า Producer จะอนุมัติ:

- `status`: พบ `open`, `in_progress`, `closed`
- `likelihood`: ตัวอย่างรองรับค่าตัวเลขที่ใช้ใน scoring
- `impact`: ตัวอย่างรองรับค่าตัวเลขที่ใช้ใน scoring
- `owner`: รูปแบบตัวอย่างเช่น `Owner-30`

Business definition ของ analytics layer กำหนดว่า:

`Unresolved Risk = status != 'closed'`

แต่ allowed values ทั้งหมดของ `status` ยังคงต้องได้รับการรับรองจาก Producer

# SLA Commitments

ความต้องการทางธุรกิจคือ management ต้องเห็นข้อมูลหลัง source มีการ update “ทันที”

คำว่า “ทันที” เป็น business expectation แต่ยังไม่ใช่ technical SLA ที่วัดได้ จึงยังไม่แปลงเป็นจำนวนนาทีหรือชั่วโมง

| SLA | Committed Value | Calibration Source | Calibration Owner |
|---|---|---|---|
| Latency SLA | `null` | Production source capability + pipeline measurement | source-system owner + Data Engineering |
| Availability SLA | `null` | Production platform availability baseline | source-system owner + Platform/Data Engineering |
| Completeness SLA | `null` | Baseline measurement after production ingestion | Data Engineering + Data Governance |

ก่อน production release ค่า SLA ทั้งสามต้องถูกเปลี่ยนจาก `null` เป็นค่าที่วัดและตรวจสอบได้ หรือได้รับการอนุมัติให้คงสถานะ pending โดย owner ที่ระบุ

# Breaking Change Policy

## Additive Change

การเพิ่ม optional/nullable field ใหม่โดยไม่เปลี่ยน semantics ของ field เดิมถือเป็น additive change เมื่อ consumer เดิมสามารถทำงานต่อได้โดยไม่ต้องแก้ไข

ตัวอย่าง:

`new_optional_field STRING NULL`

## Breaking Change

การเปลี่ยนแปลงต่อไปนี้ถือเป็น breaking change:

- rename field
- remove field ที่ consumer ใช้งาน
- เปลี่ยน data type
- เปลี่ยนความหมายของ field เดิม
- เปลี่ยน field จาก nullable เป็น required
- เปลี่ยน identifier semantics
- เพิ่มหรือเปลี่ยน allowed value ที่ทำให้ consumer logic เดิมไม่รองรับ
- เปลี่ยน semantics ของ `status`
- เปลี่ยน semantics หรือ scale ของ `likelihood` / `impact`

โดยเฉพาะ `status`, `likelihood` และ `impact` กระทบ metric calculation โดยตรง ดังนั้นการเปลี่ยน semantics ของ field เหล่านี้ต้องถือเป็น breaking change

## Notice Period

Breaking change ต้องแจ้ง Consumer ล่วงหน้าอย่างน้อย:

**14 days**

## Versioning Strategy

ใช้ contract version แบบ:

`major.minor`

แนวทาง:

- additive compatible change → เพิ่ม minor version
- breaking change → เพิ่ม major version

ตัวอย่าง:

`1.0 → 1.1` additive  
`1.x → 2.0` breaking

## Migration Procedure

เมื่อมี breaking change:

1. Producer แจ้ง proposed schema และ effective date
2. Data team ทำ impact analysis กับ downstream models และ metrics
3. ถ้าจำเป็น ให้สร้าง contract version ใหม่แบบคู่ขนาน
4. Pipeline ใหม่ต้องผ่าน schema validation ก่อน production
5. Consumer migrate ไป version ใหม่ภายใน agreed migration window
6. เมื่อ consumer ทั้งหมด migrate แล้วจึง deprecate version เก่า
7. หาก metric definition เปลี่ยนตาม schema change ต้องบันทึกใน `ANALYTICS_CHANGELOG.md`

ห้ามเปลี่ยน production schema แบบ breaking โดยไม่มี version transition และ migration procedure

# Required Fields

สำหรับ dashboard scope ปัจจุบัน fields ต่อไปนี้เป็น required fields:

| Field | Required Because |
|---|---|
| `risk_id` | รักษา grain และป้องกันการนับ Risk ซ้ำ |
| `business_unit` | วิเคราะห์การกระจุกตัวของ Risk ตามหน่วยงาน |
| `risk_title` | แสดงชื่อรายการใน Top 3 |
| `likelihood` | input ของ `Risk Priority Score` |
| `impact` | input ของ `Risk Priority Score` |
| `status` | ใช้ตัดสิน `Unresolved Risk` |
| `owner` | แสดงผู้รับผิดชอบใน Top 3 |

การไม่มี field ใด field หนึ่งข้างต้นถือเป็น contract violation สำหรับ dashboard scope ปัจจุบัน

อย่างไรก็ตาม วิธีตอบสนองเมื่อ violation เกิดขึ้น เช่น reject, quarantine หรือ partial load เป็นหน้าที่ของ `DATA_QUALITY.md` และ `PIPELINE_SPEC.md` ไม่ได้ประกาศซ้ำใน contract นี้

# Data Type Constraints

| Field | Contract Type | Constraint |
|---|---|---|
| `risk_id` | STRING | non-null; stable identifier |
| `business_unit` | STRING | non-null |
| `risk_title` | STRING | non-null |
| `likelihood` | INTEGER | non-null; allowed range = `null` pending producer confirmation |
| `impact` | INTEGER | non-null; allowed range = `null` pending producer confirmation |
| `status` | STRING | non-null; allowed set = `null` pending producer confirmation |
| `owner` | STRING | non-null |

## Type Compatibility

การ cast ข้อมูลเพื่อซ่อนการเปลี่ยน type ของ Producer ไม่ถือว่า contract ยัง compatible

ตัวอย่าง:

Producer เปลี่ยน `likelihood` จาก INTEGER เป็น free-text STRING

ถือเป็น breaking change แม้ analytics pipeline จะสามารถ `CAST` บางค่ากลับมาเป็น INTEGER ได้ก็ตาม

## Semantic Compatibility

Data type เดิมแต่ความหมายเปลี่ยนถือเป็น breaking changeเช่นกัน

ตัวอย่าง:

หาก `business_unit` เปลี่ยนจาก

“หน่วยงานที่ Risk ถูกบันทึกหรือ assign อยู่”

ไปเป็น

“หน่วยงานที่ได้รับผลกระทบ”

ถือเป็น breaking semantic change แม้ field ยังเป็น STRING และชื่อ column ไม่เปลี่ยน

# Upstream Event Contract (Product Events)

**Not applicable for current scope**

source ที่ให้มาปัจจุบันเป็น dataset/file interface ไม่ได้ระบุว่าเป็น Product Event stream และไม่มี `TRACKING_PLAN.md` upstream

ดังนั้น:

- consumed product events: none confirmed
- `event_schema_version`: not applicable
- upstream `event_name` enum: not applicable

## Schema Drift Detection Expectation

แม้ source ปัจจุบันไม่ใช่ event stream แต่ pipeline ต้องสามารถตรวจ schema drift ของ `cyber_risk_source` ได้

Expected detection mechanism:

- compare incoming field names กับ Data Contract
- compare incoming data types กับ Data Contract
- detect required field removal
- detect unexpected type changes
- detect changesต่อ allowed values เมื่อ contractual allowed sets ถูกอนุมัติแล้ว

Implementation owner:
- `PIPELINE_SPEC.md` — ingestion/schema-drift response
- `DATA_QUALITY.md` — validation rule และ monitoring

รายละเอียด implementation ยังไม่ประกาศใน
