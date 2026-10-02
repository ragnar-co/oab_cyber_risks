# Chart Type Matrix

เอกสารนี้เป็น owner ของ enum ต่อไปนี้

## `chart_type`

ค่าที่ใช้ใน Project นี้:

- `kpi_card`
- `bar`
- `table`

## `complexity_level`

ค่าที่อนุญาต:

- `basic`
- `intermediate`
- `advanced`

กฎ:

`animated`, `multi-axis`, `custom visualization` และ visualization ที่มี interaction ซับซ้อนระดับเดียวกัน ต้องถือเป็น `advanced`

Project version ปัจจุบันใช้เฉพาะ `basic`

## Visualization Matrix

| Viz ID | Metric | Metric Shape | chart_type | complexity_level | Grain | Purpose | Anti-pattern Reference |
|---|---|---|---|---|---|---|---|
| VIZ-01 | `METRIC-01 — Unresolved Risk Count` | categorical count | `bar` | `basic` | `business_unit × snapshot` | เปรียบเทียบจำนวน unresolved risk ระหว่างหน่วยงาน | `null — pending references/data-to-viz validation` |
| VIZ-02 | `METRIC-02 — Unresolved Risk Share by Business Unit` | categorical proportion | `bar` | `basic` | `business_unit × snapshot` | แสดงสัดส่วน unresolved risk ของแต่ละหน่วยงาน | `null — pending references/data-to-viz validation` |
| VIZ-03 | `METRIC-03 — Risk Priority Score` | record-level score | `table` | `basic` | `risk_id × snapshot` | แสดงคะแนนระดับ Risk record เมื่อต้อง inspect รายการ | `null — pending references/data-to-viz validation` |
| VIZ-04 | `METRIC-04 — Unresolved Risk Count by Priority Score` | categorical count by ordered score | `bar` | `basic` | `business_unit × risk_priority_score × snapshot` | เห็นจำนวน unresolved risk แยกตามคะแนนความเสี่ยง | `null — pending references/data-to-viz validation` |
| VIZ-05 | `METRIC-05 — Top Risk Follow-up Rank` | ranking | `table` | `basic` | `risk_id × snapshot` | แสดง Top 3 รายการที่ควรติดตาม | `null — pending references/data-to-viz validation` |
| VIZ-06 | `METRIC-06 — Closed Risk Ratio by Business Unit` | categorical proportion | `bar` | `basic` | `business_unit × snapshot` | เปรียบเทียบความคืบหน้าการปิด Risk ระหว่างหน่วยงาน | `null — pending references/data-to-viz validation` |
| VIZ-07 | `METRIC-07 — Not Started Share of Unresolved Risk` | categorical proportion | `bar` | `basic` | `business_unit × snapshot` | เห็นว่างานค้างเพราะยังไม่เริ่มหรือเริ่มแล้วยังไม่เสร็จ | `null — pending references/data-to-viz validation` |
| VIZ-08 | `METRIC-08 — Unresolved Risk Matrix` | two-dimensional count | `table` | `basic` | `likelihood × impact × snapshot` | แยก Risk ที่ score เท่ากันแต่ต่างโอกาสเกิด/ผลกระทบ | `null — pending references/data-to-viz validation` |

## Recommended Dashboard Composition

### VIZ-01 — Unresolved Risk by Business Unit

**Chart**
- horizontal `bar`

**Category**
- `business_unit`

**Value**
- `unresolved_risk_count`

**Sort**
- `unresolved_risk_count DESC`

**Business Question**
- ความเสี่ยงที่ยังไม่ปิดกระจุกอยู่ที่หน่วยงานใด

**Label**
- แสดง count บน/ปลาย bar

---

### VIZ-02 — Share of Unresolved Risk

**Chart**
- horizontal `bar`

**Category**
- `business_unit`

**Value**
- `unresolved_risk_share`

**Format**
- percentage

**Sort**
- `unresolved_risk_share DESC`

ใช้ bar แทนการบังคับใช้ part-to-whole chart เพื่อให้ management เปรียบเทียบอันดับระหว่างหน่วยงานได้โดยตรง

---

### VIZ-03 — Risk Priority Detail

**Chart**
- `table`

**Columns**
- `risk_title`
- `business_unit`
- `risk_priority_score`
- `owner`

**Default Sort**
- `risk_priority_score DESC`

ใช้สำหรับ record-level inspection ไม่ใช้ aggregate visualization เพราะ metric grain คือ `risk_id × snapshot`

---

### VIZ-04 — Unresolved Risk by Priority Score

**Chart**
- `bar`

**X**
- `risk_priority_score`

**Y**
- `unresolved_risk_count`

**Filter**
- `business_unit`

**Sort**
- `risk_priority_score DESC`

Version ปัจจุบันแสดง score โดยตรง

ห้ามแปลง score เป็น:

- Low
- Medium
- High
- Critical

จนกว่าจะมี calibrated bucket rule ที่ได้รับการอนุมัติ

---

### VIZ-05 — Top 3 Risk Follow-up

**Chart**
- `table`

**Rows**
- 3

**Columns**
1. Rank
2. `risk_title`
3. `risk_priority_score`
4. `owner`

**Ranking**
- `risk_priority_score DESC`
- technical tie-break: `risk_id ASC`

`risk_id` ไม่จำเป็นต้องแสดงต่อ management แต่ใช้เพื่อให้ ordering deterministic

### VIZ-06 / VIZ-07 — Progress Bars

**Chart**
- horizontal `bar`, x-axis 0–100%

**Sort**
- ค่า metric DESC

**Label**
- `xx.x% (numerator/denominator)` เพื่อให้เห็นขนาดฐาน ไม่ใช่แค่ %

แสดงทุก Business Unit เสมอ Business Unit filter ใช้ highlight (สี + ข้อความ "◀ เลือกอยู่")

---

### VIZ-08 — Risk Matrix Table

**Chart**
- `table` แถว = likelihood (มาก→น้อย), คอลัมน์ = impact (น้อย→มาก), ค่า = จำนวน Unresolved Risk

ห้ามระบายสีช่องเป็น heatmap (`intermediate`) และห้ามใช้สีแดง/เหลือง/เขียวแทนระดับ จนกว่าจะมี approved bucket rule และ literacy reconciliation

# Color & Theme Spec

## Design Principle

สีต้องช่วยแยกข้อมูลและสถานะ ไม่ใช้สีเพื่อสร้างความหมายของ risk threshold ที่ยังไม่ได้ calibrate

ดังนั้นใน version นี้:

- ห้ามใช้สีแดงเพื่อหมายถึง “Critical Risk Score”
- ห้ามใช้สีเหลืองเพื่อหมายถึง “Warning Risk Score”
- ห้ามใช้สีเขียวเพื่อหมายถึง “Safe”

จนกว่า Action Thresholds จะได้รับการอนุมัติ

## Palette

| Purpose | Value |
|---|---|
| Primary | `#1F4E79` |
| Secondary | `#5B6573` |
| Accent | `#2F75B5` |
| Background | `#FFFFFF` |
| Surface | `#F5F7F9` |
| Text Primary | `#1F2933` |
| Text Secondary | `#52606D` |
| Border | `#CBD2D9` |
| Positive Semantic | `#2E7D32` |
| Warning Semantic | `#9A6700` |
| Alert Semantic | `#B42318` |

Semantic colors มีไว้รองรับสถานะที่มี business rule แล้วเท่านั้น

## Typography

- Dashboard title: 20–24 px, semibold
- Section title: 16–18 px, semibold
- Chart title: 14–16 px, semibold
- Axis / labels: ≥ 12 px
- Table text: ≥ 12 px
- หลีกเลี่ยง italic สำหรับค่าที่ต้องอ่านเร็วใน executive dashboard

## Reusable `viz_theme`

```python
COLOR_PALETTE = {
    "primary": "#1F4E79",
    "secondary": "#5B6573",
    "accent": "#2F75B5",
    "background": "#FFFFFF",
    "surface": "#F5F7F9",
    "text_primary": "#1F2933",
    "text_secondary": "#52606D",
    "border": "#CBD2D9",
    "positive": "#2E7D32",
    "warning": "#9A6700",
    "alert": "#B42318",
}

FONT_RULES = {
    "dashboard_title_px": 22,
    "section_title_px": 17,
    "chart_title_px": 15,
    "label_min_px": 12,
    "table_min_px": 12,
    "dashboard_title_weight": 600,
    "section_title_weight": 600,
}

CHART_DEFAULTS = {
    "show_title": True,
    "show_source_timestamp": True,
    "show_tooltip": True,
    "show_legend": False,
    "show_data_labels": True,
    "animation": False,
    "zero_baseline_for_count_bar": True,
    "sort_categorical_bars_desc": True,
}
```

# Interaction Spec

## Global Filters

Dashboard visualization layerควรรองรับ:

- `business_unit`
- snapshot / latest data context

ไม่เพิ่ม filter ที่ source/metric ยังไม่มี definition

## VIZ-01 — Business Unit Bar

**Hover / Tooltip**
- Business Unit
- Unresolved Risk Count
- source snapshot time

**Click**
- เลือก Business Unit เพื่อ filter VIZ-03, VIZ-04 และ VIZ-05

**Cross-chart Sync**
- Business Unit selection ต้องใช้ค่าเดียวกันทุก chart

---

## VIZ-02 — Share Bar

**Tooltip**
- Business Unit
- Unresolved Risk Share
- Unresolved Risk Count
- Total Unresolved Risk Count

**Click**
- filter dashboard ตาม Business Unit

---

## VIZ-03 — Risk Detail Table

**Interaction**
- sortable
- filterable by Business Unit
- default sort by `risk_priority_score DESC`

ไม่มี animation

---

## VIZ-04 — Priority Score Bar

**Tooltip**
- Risk Priority Score
- Unresolved Risk Count
- Business Unit filter context

**Click**
- เลือก score เพื่อ filter Risk Detail Table

**Crosshair**
- ไม่ใช้ใน version ปัจจุบัน

---

## VIZ-05 — Top 3 Table

**Interaction**
- ไม่มี user-controlled sort ใน default executive view
- ต้องรักษา canonical ranking จาก `METRIC-05`
- click row สามารถเปิด Risk detail view ภายหลังได้เมื่อ drill-down target ถูกกำหนดใน `DASHBOARD_SPEC.md`

## Animation

Default:

`animation = false`

หากมีการเพิ่ม animation ภายหลัง ให้จัดเป็น `complexity_level = advanced` เท่านั้น

# Accessibility Guidelines

## Contrast

ข้อความปกติต้องตั้งเป้าอย่างน้อย WCAG 2.1 AA contrast ratio `4.5:1`

ข้อความขนาดใหญ่ต้องตั้งเป้าอย่างน้อย `3:1`

## Color Independence

ห้ามใช้สีเพียงอย่างเดียวเพื่อสื่อ:

- ranking
- warning
- status
- selected state

ต้องมีอย่างน้อยหนึ่งอย่างประกอบ เช่น:

- text label
- icon
- pattern
- numeric value

## Colorblind Safety

เมื่อใช้ semantic state ต้องมี textual state กำกับเสมอเพื่อให้ผู้ใช้ที่มี protanopia, deuteranopia หรือ tritanopia ไม่ต้องพึ่งการแยกสีอย่างเดียว

## Screen Reader

Chart ทุกตัวต้องมี:

- chart title
- concise alt text
- metric name
- current filter context
- snapshot timestamp

ตัวอย่าง alt text:

`จำนวน Unresolved Risk แยกตาม Business Unit เรียงจากจำนวนมากไปน้อย ณ snapshot ล่าสุด`

## Tables

Table ต้องมี:

- semantic column headers
- keyboard-focusable rows/controls
- sort state ที่อ่านได้ผ่าน accessibility metadata
- ตัวเลขไม่สื่อความหมายผ่านสีอย่างเดียว

## Keyboard Navigation

Interactive filter และ selectable chart element ต้องสามารถใช้งานได้โดยไม่พึ่ง mouse

# Data Literacy Guard Rails

## Audience

Primary audience:

`management`

ค่าที่บันทึกก่อนหน้านี้ใน `STAKEHOLDERS.md`:

`data_literacy_level = high`

แต่ template structure ปัจจุบันกำหนด vocabulary เป็น:

`basic / intermediate / advanced`

ดังนั้น mapping:

`high → ?`

ยังไม่ถูกอนุมัติ และห้ามแปลงโดยอัตโนมัติ

## Conservative Gate for Current Version

จนกว่าจะ reconcile `data_literacy_level` ให้ตรงกับ template:

**อนุญาตเฉพาะ `complexity_level = basic`**

Visualization ปัจจุบันจึงใช้เฉพาะ:

- bar
- table
- KPI card หากเพิ่มใน Dashboard Spec

และไม่ใช้:

- heatmap
- scatter
- crosshair
- grouped bar
- pie/donut
- multi-axis
- animated visualization
- custom visualization
- Sankey

## Complexity Mapping

| complexity_level | Visualization Family |
|---|---|
| `basic` | bar, line, KPI card, table |
| `intermediate` | heatmap, scatter, grouped bar, pie/donut, crosshair interaction |
| `advanced` | multi-axis, animated, custom visualization, Sankey |

## Gate Rule

Visualization ห้ามมี `complexity_level` สูงกว่า audience `data_literacy_level`

ถ้าต้อง override ต้องมี:

1. sign-off จาก stakeholder group
2. training plan
3. บันทึกการเปลี่ยนแปลงใน `ANALYTICS_CHANGELOG.md`

## Current Project Gate

| Visualization | complexity_level | Allowed Now |
|---|---|---|
| Business Unit bar | `basic` | Yes |
| Unresolved Share bar | `basic` | Yes |
| Risk Detail table | `basic` | Yes |
| Priority Score bar | `basic` | Yes |
| Top 3 table | `basic` | Yes |
| Closed Risk Ratio bar | `basic` | Yes |
| Not Started Share bar | `basic` | Yes |
| Risk Matrix as numeric table (ไม่ระบายสี) | `basic` | Yes |
| Heatmap Business Unit × Score | `intermediate` | No — pending literacy reconciliation |
| Animated risk transition | `advanced` | No |
