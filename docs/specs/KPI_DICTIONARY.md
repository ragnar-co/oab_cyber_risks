# KPI Catalog

## KPI-01: Unresolved Cyber Risk Exposure

**Definition**  
ระดับผลลัพธ์ทางธุรกิจในการควบคุมและลด cyber risk ที่ยังไม่ได้รับการปิด เพื่อให้ management สามารถระบุได้ว่าความเสี่ยงสะสมอยู่ที่ business unit ใด และกำหนดรายการที่ต้องติดตามเป็นลำดับต่อไป

**Business Questions Supported**
- ความเสี่ยงที่ยังไม่ปิดกระจุกอยู่ที่หน่วยงานใด
- ควรติดตามรายการความเสี่ยงใดก่อน

**Owner**
- management

**Target**
- null

**Target Calibration Owner**
- management

**Measurement Frequency**
- ทุกครั้งที่ source data มีการ update

**Business Impact**
- ช่วยให้ management เห็นการกระจุกตัวของ unresolved cyber risk ระหว่าง business units
- ลดการพึ่งพาการอ่านและจัดอันดับรายการจาก Excel ด้วยมือ
- สนับสนุนการกำหนดลำดับการติดตามและ escalation ของรายการ risk

**OKR / iKPI Mapping**
- null

**Source Evidence**
- `risk_id` — ระบุรายการ risk
- `business_unit` — หน่วยงานที่ใช้วิเคราะห์การกระจุกตัว
- `risk_title` — รายละเอียดรายการ risk
- `likelihood` — input ที่อาจใช้ในการประเมิน priority
- `impact` — input ที่อาจใช้ในการประเมิน priority
- `status` — lifecycle state ของ risk
- `owner` — ผู้รับผิดชอบรายการ risk

**Definition Pending Confirmation**
- ความหมายอย่างเป็นทางการของ “unresolved risk”
- กฎการจัดลำดับรายการ risk
- numeric target ของ KPI

# KPI Hierarchy (CEO to Team Level)

| Level | KPI | Owner | Status |
|---|---|---|---|
| Management | Unresolved Cyber Risk Exposure | management | Proposed |
| Department | null | null | ยังไม่มี requirement |
| Team | null | null | ยังไม่มี requirement |

# Measurement Frequency

| KPI | Measurement Frequency | Trigger |
|---|---|---|
| Unresolved Cyber Risk Exposure | ทุกครั้งที่มีการ update ข้อมูล | Source data update |

หมายเหตุ: requirement นี้ระบุ business cadence เท่านั้น ยังไม่ได้กำหนด technical freshness SLA เป็นจำนวนนาทีหรือชั่วโมง

# KPI Owners

| KPI | Accountable Owner | Target Calibration Owner |
|---|---|---|
| Unresolved Cyber Risk Exposure | management | management |
