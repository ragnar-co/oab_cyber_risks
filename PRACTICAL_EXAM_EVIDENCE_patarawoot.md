# PRACTICAL_EXAM_EVIDENCE_patarawoot

> รายงานรวบรวมหลักฐานหลังสอบ (AFTER_EXAM) สร้างโดย Claude Code ตามคำสั่งผู้ใช้ เป็นไฟล์เดียวที่สร้างขึ้นในขั้นรวบรวม อยู่นอก repo งานสอบ
> ไม่มีการประเมินคะแนนหรือตัดสินผ่าน–ตก

---

## A. ข้อมูลผู้สอบและขอบเขตหลักฐาน

| รายการ | ค่า | สถานะ / Evidence |
|---|---|---|
| ชื่อผู้สอบ | `patarawoot` — เป็นชื่อ account ที่ปรากฏใน Git user, GitHub (`patarawoot/oab_cyber_risks`) และ Coolify ("Account menu for patarawoot") ไม่ใช่ชื่อ-นามสกุลจริง | VERIFIED เฉพาะว่าเป็นชื่อ account (E001, E022, E028); ชื่อจริง UNKNOWN |
| อีเมล | [REDACTED] (มีในบริบทระบบ ไม่เปิดเผยตามข้อกำหนด) | — |
| ตำแหน่ง | ไม่ทราบ — ไม่พบข้อมูลใน session หรือ repo | UNKNOWN |
| โจทย์ | "Client Cyber Risk Dashboard": รับ CSV → ตรวจสอบ → เก็บ DuckDB → แสดงจำนวนทั้งหมด/ปิด/ยังไม่ปิด, กราฟตามหน่วยงานและระดับความเสี่ยง, Top 3, filter รายหน่วยงาน | VERIFIED ว่าผู้ใช้วางโจทย์นี้ใน session (E010) |
| โจทย์ DDD ที่เลือก | ไม่ทราบ — ไม่พบคำว่า DDD / Domain-Driven / Data-Driven ใน repo (E040) ชุดเอกสาร spec 12 ไฟล์มีอยู่ตั้งแต่เริ่ม session (E002) แต่ไม่มีหลักฐานว่าเป็น "เอกสาร DDD" ที่โจทย์หมายถึง | UNKNOWN |
| เครื่องมือที่ใช้ | Claude Code (model Opus 5.5) ทำงานผ่าน tool calls; Python/uv, DuckDB (Python + CLI), Streamlit, Altair, pytest, Docker/Compose, cmux browser, Git/GitHub (SSH), Coolify (เข้าถึงผ่าน Cloudflare Access) | VERIFIED จาก tool calls (E011, E013, E023, E028) |
| Repo | `git@github.com:ragnar-co/oab_cyber_risks.git` (เดิม `git@github.com:patarawoot/oab_cyber_risks.git`) | VERIFIED ว่ามี push (E022, E027) |
| URL แอป | local: `http://localhost:8599` (dev server), `http://localhost:8501` (Docker) — ไม่มี URL production | VERIFIED เฉพาะ local (E015, E023); production UNKNOWN |
| เวลาเริ่ม/หมดเวลาสอบ | ไม่ทราบ — ไม่มีข้อมูลเวลาสอบใน session หรือ repo | UNKNOWN |
| Commit ที่ส่งสอบ | ไม่ทราบ — ไม่มีหลักฐานว่าผู้สอบระบุ commit ส่งสอบ | UNKNOWN |
| เวลาเริ่มรวบรวมรายงาน | 2026-10-02 12:10:32 +07 (UTC+0700) | VERIFIED (E033) |

### แหล่งหลักฐานที่เข้าถึงได้
- บทสนทนาและผล tool calls ของ session นี้ตั้งแต่ต้นจนถึงคำสั่งรวบรวมรายงาน ไม่พบว่า context ถูกย่อ/สรุป ผล tool บางรายการที่ยาวถูกเก็บเป็นไฟล์ชั่วคราวและอ่านกลับได้ในขณะนั้น
- Repo `ws-exam` (working tree, Git history 2 commits, reflog)
- Screenshot จาก cmux browser (ไฟล์ชั่วคราวในเครื่อง; ชื่อไฟล์มี epoch ms ซึ่งแปลงเป็นเวลาได้ — E041)

### แหล่งที่ขาด / ข้อจำกัด
- ไม่มีเวลาเริ่ม–หมดสอบ และไม่มี commit ที่ประกาศส่งสอบ
- ผล tool calls ไม่มี timestamp ในตัว เวลาที่ระบุได้มาจาก Git commit time, ค่า `snapshot_at` ในแอป, ชื่อไฟล์ screenshot และพารามิเตอร์ `iat` ใน redirect ของ Cloudflare Access เท่านั้น
- ไม่มีหลักฐานการ deploy บน Coolify สำเร็จ (ไม่มี deployment ID/URL) — E028–E030
- ไม่ทราบสิ่งที่ผู้สอบทำนอก tool calls ของ AI (เช่น การสร้าง GitHub repo, การย้าย repo, การ login, การอัปโหลดไฟล์ผ่านหน้าเว็บ) ยกเว้นที่ผู้สอบแจ้งหรือมีร่องรอยในผลลัพธ์
- ไม่ทราบว่ามี session อื่นก่อนหน้านี้ที่สร้างเอกสาร spec หรือไม่

---

## B. สภาพงานที่พบ (ณ เวลารวบรวม 2026-10-02 12:10:32 +07)

| รายการ | ค่า | Evidence |
|---|---|---|
| Repo root | `~/coding/ws-exam` (Git repo แยก สร้างระหว่าง session) | E021, E033 |
| Branch | `main` tracking `origin/main` | E033 |
| HEAD | `ea5534da4a78b356a32a19bdd831497ee847caf8` | E033 |
| Remote | `origin = git@github.com:ragnar-co/oab_cyber_risks.git` | E027, E033 |
| Staged | ไม่มี | E033 |
| Unstaged (modified) | `.streamlit/config.toml`, `app.py`, `tests/test_pipeline.py` (+178/−195) | E033 |
| Untracked | `src/cyber_risk/theme.py` | E033 |
| Ignored ที่มีอยู่ | `.DS_Store`, `.pytest_cache/`, `.venv/`, `data/cyber_risk.duckdb`, `__pycache__/` | E033 |
| Process ที่ยังรันอยู่ | Streamlit dev server port 8599 ที่ AI เปิดไว้ (ไม่ได้หยุดในขั้นรวบรวม) | E031 |

### สภาพที่ยืนยันได้เมื่อหมดเวลาสอบ
ไม่ทราบ — ไม่มีเวลาหมดสอบ จึงแยกไม่ได้ว่า commit/การเปลี่ยนแปลงใดเกิดก่อนหรือหลังหมดเวลา

### แยกงานตามสถานะ
| กลุ่ม | รายละเอียด | Evidence |
|---|---|---|
| อยู่ใน commit `fcfb06f` (2026-10-02 11:30:54 +07) | แอปหลัก, pipeline, queries, tests, spec 12 ไฟล์ (ย้ายไป `docs/specs/`), sample CSV zip, README, pyproject/uv.lock — 23 ไฟล์ | E021 |
| อยู่ใน commit `ea5534d` (2026-10-02 11:41:29 +07) | Dockerfile, .dockerignore, docker-compose.yml, README (Docker/Coolify), app.py (lock retry, AUTOLOAD_SAMPLE) | E026 |
| ยังไม่ commit | งานปรับหน้าตา dashboard (theme.py, app.py), filter ผ่าน URL `?bu=`, smoke test ใหม่ 1 ตัว | E031, E032, E033 |
| มีอยู่ก่อน session (ไม่ทราบที่มา/ผู้เขียน) | spec 12 ไฟล์ (เดิมอยู่ที่ root) และ `inputs/Pasted 2026-10-02 at 10.28.11 AM.textClipping` | E001, E002, E003 |
| ผู้สอบนำมาวางระหว่าง session | `inputs/oab_cyber_risks_2_5mb.csv.zip` (ต่อมา AI ย้ายไป `data/sample/`) | E005 |

หมายเหตุ: spec 12 ไฟล์ **ถูกแก้ไขโดย AI ระหว่าง session** (E008, E017, E019) เนื้อหาใน commit จึงไม่ใช่ฉบับดั้งเดิมทั้งหมด

---

## C. ลำดับการทำงาน

เวลาที่ระบุมาจากแหล่งในคอลัมน์ Evidence เท่านั้น แถวที่ไม่มีเวลาเรียงตามลำดับใน session (ไม่ทราบเวลาจริง)

| ลำดับ | เวลา/ช่วงเวลา | สิ่งที่ทำ | ผู้ดำเนินการที่ยืนยันได้ | ผลที่พบ | Evidence ID |
|---|---|---|---|---|---|
| 1 | ไม่ทราบ (ก่อนข้อ 2) | ขอให้ "analysis repo นี้" | ผู้สอบ (คำสั่ง) / AI (ดำเนินการ) | พบเอกสาร spec 12 ไฟล์ ไม่มีโค้ด ไม่มี commit; AI รายงานข้อขัดแย้ง 10 ข้อ | E001, E002, E004 |
| 2 | ไม่ทราบ | สั่ง "แก้เลย" และวาง CSV ใน inputs | ผู้สอบ | พบไฟล์ `.csv.zip` (ไม่ใช่ `.csv`) | E005 |
| 3 | ไม่ทราบ | Profile ข้อมูลและตรวจ golden values ด้วย DuckDB CLI | AI | ค่าตรงกับ TESTING_STRATEGY ทั้งหมด | E006, E007 |
| 4 | ไม่ทราบ | แก้ spec ข้อ 1–5 (snapshot_registry, NULL score, BU filter, share unit) และทดสอบ SQL | AI | SQL ใหม่ทำงานตามที่ออกแบบใน DuckDB | E008, E009 |
| 5 | ไม่ทราบ | วางโจทย์สอบ | ผู้สอบ | — | E010 |
| 6 | ไม่ทราบ | ตั้งโปรเจกต์ uv, เขียน pipeline/queries/tests | AI | `19 passed` หลังแก้ ModuleNotFoundError | E011, E012, E013 |
| 7 | snapshot แรกของแอป 2026-10-02 11:17:32; screenshot 11:18:09 | สร้าง Streamlit app, smoke test, เปิดใน browser, แก้ chart | AI | แสดง 10,507 / 2,528 / 7,979 | E014, E015, E016 |
| 8 | ไม่ทราบ | ผู้สอบถามกราฟเพิ่ม → AI ทำ EDA และเสนอ 5 กราฟ | ผู้สอบ / AI | ผู้สอบเลือก "เอาแค่ 1 2 3 พอ" | E018, E019 |
| 9 | screenshot 11:27:34 | เพิ่ม METRIC-06/07/08 + เอกสาร + tests | AI | `24 passed` | E019 |
| 10 | ก่อน 11:30:54 | จัดโครงสร้าง repo, `git init` แยก, commit | ผู้สอบสั่ง / AI ดำเนินการ | commit `fcfb06f` 11:30:54 | E020, E021 |
| 11 | หลัง 11:30:54 (เวลาจริงไม่ทราบ) | push ไป `patarawoot/oab_cyber_risks` | ผู้สอบให้ URL / AI push | `* [new branch] main -> main` | E022 |
| 12 | ระหว่าง 11:30:54–11:41:29 | สร้าง Docker image, ทดสอบ local, ทดสอบ persistence และ lock | AI | `healthy`, ข้อมูลคงอยู่, รอ lock 11s สำเร็จ | E023, E024, E025 |
| 13 | 11:41:29 | commit Docker | AI | `ea5534d` | E026 |
| 14 | หลัง 11:41:29 (ก่อน 11:47:32) | ผู้สอบแจ้งย้าย repo ไป `ragnar-co`; AI เปลี่ยน remote และ push | ผู้สอบ (แจ้ง) / AI (push) | `fcfb06f..ea5534d main -> main` | E027 |
| 15 | redirect `iat` 11:47:32 | เปิด Coolify; ผู้สอบ login (Cloudflare Access + GitHub) | ผู้สอบ (login) / AI (สำรวจ) | team ส่วนตัวไม่มี server | E028 |
| 16 | screenshot 11:52:58 | ผู้สอบเปลี่ยนเป็น Root Team; AI กด Validate server `localhost` | ผู้สอบ / AI | `Error: WARNING: Your password has expired.` | E029 |
| 17 | หลังข้อ 16 | ผู้สอบตัดสินใจ "ไม่เป็นไร กลับมา app ดีกว่า" | ผู้สอบ | ไม่มีการ deploy | E030 |
| 18 | snapshot 12:02:04; screenshot 12:03:16–12:08:59 | ปรับ UI dashboard, filter ผ่าน URL, smoke test | AI (มีร่องรอยว่าผู้สอบอัปโหลด CSV ผ่าน UI — INFERRED) | `25 passed`; ไม่ commit | E031, E032 |
| 19 | 12:10:32 | เริ่มรวบรวมหลักฐาน (อ่านอย่างเดียว) | AI | รายงานนี้ | E033 |

---

## D. คำสั่งและเครื่องมือที่ใช้

### D1. คำสั่งที่มีหลักฐานว่า execute แล้ว (สรุปรวมคำสั่งซ้ำ)
คอลัมน์ "ผล/exit code": tool แสดง `Exit code 1` เฉพาะกรณีล้มเหลว กรณีอื่นไม่แสดง exit code จึงระบุเป็น "ไม่แสดง exit code"

| ลำดับ | คำสั่ง/tool ที่พบ | จุดประสงค์ที่มีหลักฐาน | ผล/exit code ที่พบ | ช่วงเวลา | Evidence ID |
|---|---|---|---|---|---|
| 1 | `ls -la`, `find`, `cat *.md`, `plutil -p <textClipping>` | สำรวจ repo | ไฟล์ 14 รายการ; `fatal: your current branch 'main' does not have any commits yet` | TIME_UNKNOWN (ก่อน 11:17) | E002, E003 |
| 2 | `unzip <csv.zip>` (ไปยัง scratchpad) | แตกไฟล์ข้อมูลโดยไม่แตะ inputs | สำเร็จ, ไม่แสดง exit code | TIME_UNKNOWN | E006 |
| 3 | `duckdb < eda.sql` / `duckdb -c ...` (หลายครั้ง) | profile, golden values, EDA | ผลตาราง; 2 ครั้งแรก `Parser Error: syntax error at or near "share"` และ `"."` (Exit code 1) แล้วแก้ | TIME_UNKNOWN | E006, E007, E009, E018 |
| 4 | `uv sync` | ติดตั้ง dependencies | สำเร็จ | TIME_UNKNOWN | E011 |
| 5 | `uv run pytest -q` (≥10 ครั้ง) | รัน tests | ครั้งแรก `ModuleNotFoundError: No module named 'cyber_risk'`; หลังเพิ่ม `pythonpath` → `19 passed`; ต่อมา `24 passed`; ครั้งสุดท้าย `25 passed in 3.07s` | TIME_UNKNOWN (ก่อน 12:10) | E013, E019, E021, E026, E032 |
| 6 | `uv run python` + `streamlit.testing.v1.AppTest` | smoke test dashboard | ค่า metric และ Top 3 ตามคาด; ครั้งหนึ่งได้ `IO Error: Could not set lock on file ...` | TIME_UNKNOWN | E014, E016, E019, E031 |
| 7 | `uv run streamlit run app.py --server.port 8599` (รันซ้ำหลายรอบ) | dev server | `/_stcore/health` → `ok` | 11:17 ถึง 12:08 | E015, E031 |
| 8 | `cmux browser open/wait/screenshot/scroll/click` | ตรวจ UI และ Coolify | screenshot หลายภาพ; หลายครั้ง `Error: invalid_params: Surface is not a browser` | 11:18–12:09 | E015, E028, E029, E031, E036 |
| 9 | `git init -b main`, `git add -A`, `git commit` (2 ครั้ง) | สร้าง repo และ commit | `fcfb06f`, `ea5534d` | 11:30:54, 11:41:29 | E021, E026 |
| 10 | `git remote add origin git@github.com:patarawoot/oab_cyber_risks.git`, `git ls-remote`, `git push -u origin main` | push ครั้งแรก | `* [new branch] main -> main`; ls-remote `fcfb06f…` | หลัง 11:30:54 | E022 |
| 11 | `git remote set-url origin git@github.com:ragnar-co/oab_cyber_risks.git`, `git ls-remote`, `git push origin main` | push ไป repo ใหม่ | `fcfb06f..ea5534d  main -> main`; ls-remote `ea5534d…` | หลัง 11:41:29 | E027 |
| 12 | `docker compose build`, `docker compose up -d`, `curl /_stcore/health`, `docker compose ps` | build/run local | `Image ws-exam-dashboard Built`; `ok`; `Up 8 seconds (healthy)` | ระหว่าง 11:30–11:41 | E023 |
| 13 | `docker compose exec ...`, `docker compose restart/stop`, `docker run --rm -v ws-exam_cyber_risk_data:/data ...` | ตรวจ volume, persistence, lock contention | `[('published', 10507)]`; `exception: False \| waited 11s` | ระหว่าง 11:30–11:41 | E024, E025 |
| 14 | `gh auth status` | เช็ค GitHub CLI | `command not found: gh` | TIME_UNKNOWN | E020 |
| 15 | Coolify UI (cmux): เปิดหน้า project, New resource, Servers, Validate connection | เตรียม deploy | No available servers; Validation error | 11:47–11:53 | E028, E029 |

### D2. คำสั่งที่เสนอหรือกล่าวถึง แต่ไม่มีหลักฐานว่า execute
| คำสั่ง | บริบท | Evidence ID |
|---|---|---|
| `sudo chage -l coolify` / `sudo chage -d "$(date +%F)" -M -1 coolify` | AI เสนอให้ผู้ดูแล server รันเพื่อแก้ปัญหารหัสผ่านหมดอายุ ไม่มีหลักฐานว่ารัน | E029, E030 |
| `brew install gh`, `gh auth login` | ตัวเลือกใน AskUserQuestion ผู้สอบไม่ได้เลือก | E022 |
| ขั้นตอน Coolify (Build Pack Dockerfile, Port 8501, Persistent Storage `/data`) | เขียนในคำตอบและ README ไม่ได้ดำเนินการบน Coolify | E026, E030 |
| Basic auth / Cloudflare Access สำหรับแอป | AI เสนอ ไม่ได้ทำ | E026, E030 |

### D3. คำสั่งอ่านอย่างเดียวที่ใช้รวบรวมรายงาน (AFTER_EXAM)
`date`, `pwd`, `git rev-parse`, `git branch -vv`, `git remote -v`, `git status --porcelain=v1 -uall`, `git status --ignored`, `git diff --stat`, `git diff --cached --stat`, `git log`, `git reflog`, `git show --stat`, `git show HEAD:<file> | rg -n ...`, `rg -n -i ...`, `ls -la`, `date -r <epoch>` — E033, E040, E041

---

## E. การตัดสินใจและการใช้ AI

| การตัดสินใจ | ผู้ตัดสินใจ (ตามหลักฐาน) | เหตุผลที่ปรากฏในหลักฐาน | Evidence |
|---|---|---|---|
| แก้ spec ข้อ 1–5 ก่อน | ผู้สอบสั่ง "แก้เลย" หลัง AI เสนอ | กระทบตัวเลข dashboard โดยตรง (เหตุผลของ AI) | E004, E005 |
| Stack: Python + DuckDB + Streamlit + uv | AI (ผู้สอบไม่ได้คัดค้าน) | โจทย์กำหนด DuckDB; AI ไม่ได้อธิบายเหตุผลเลือก Streamlit เพิ่มเติม | E010, E011 |
| ระดับความเสี่ยง = Risk Priority Score (likelihood × impact) ไม่แบ่ง bucket | AI ตาม spec | `DASHBOARD_SPEC.md` ห้ามแปลงคะแนนเป็น Low/Medium/High/Critical; โจทย์ที่วางไม่มีตารางเกณฑ์; AI ขอให้ผู้สอบส่งเกณฑ์หากมี — ไม่มีหลักฐานว่าผู้สอบยืนยัน | E010, E038 |
| ไม่ใช้ heatmap; Risk Matrix เป็นตารางตัวเลข | AI ตาม spec | `VIZ_DESIGN_SPEC.md` จัด heatmap เป็น `intermediate` ยังไม่อนุญาต | E018, E019 |
| เลือกกราฟเพิ่มเฉพาะข้อ 1, 2, 3 (ตัด owner workload และประเภทปัญหา) | ผู้สอบ ("เอาแค่ 1 2 3 พอ") | AI ระบุความเสี่ยง PDPA ของ owner_id และการ parse free text | E018, E019 |
| ไม่แสดงกราฟตามระบบ/สาขา | AI | ระบบผูก 1:1 กับหน่วยงาน; สาขา 180 แห่งกระจายสม่ำเสมอ | E018 |
| Git repo แยกใน `ws-exam` แทน repo แม่ | AI (ผู้สอบไม่คัดค้าน) | repo แม่ `~/coding` มีโปรเจกต์อื่นหลายตัว | E020, E021 |
| push ผ่าน URL ที่ผู้สอบสร้าง | ผู้สอบ (AskUserQuestion) | ไม่มี `gh` CLI | E020, E022 |
| หยุดงาน Coolify กลับไปทำแอป | ผู้สอบ | ไม่มีเหตุผลระบุ | E030 |
| ปรับ UI | ผู้สอบขอ; รายละเอียดโดย AI | ตาม typography/palette ใน VIZ_DESIGN_SPEC | E031 |

### หลักฐานการตรวจ/ปรับ output ของ AI โดยผู้สอบ
- ผู้สอบเลือกขอบเขตจากข้อเสนอของ AI (E019) และตอบ AskUserQuestion (E022)
- ผู้สอบแก้ข้อมูลที่ AI ใช้ (แจ้งว่า repo ย้ายแล้ว — E027)
- ผู้สอบทำขั้นตอนที่ AI ทำแทนไม่ได้ (login, เปลี่ยน team — E028, E029)
- ไม่พบหลักฐานว่าผู้สอบอ่าน diff/review โค้ดที่ AI เขียน หรือรัน tests เอง
- ไม่สามารถสรุประดับความเข้าใจของผู้สอบจากหลักฐานที่มี

### สัดส่วนงาน
โค้ด เอกสารที่แก้ไข และคำสั่งทั้งหมดใน D1 ถูกดำเนินการผ่าน tool calls ของ AI (VERIFIED) ผู้สอบให้คำสั่ง ข้อมูล และการตัดสินใจ

### Token/quota
ไม่พบหลักฐานการใช้ token/quota ใน session

---

## F. ปัญหาและสิ่งที่ติด

| ปัญหา | อาการ/error ที่พบ | วิธีที่ลอง | ผลที่ยืนยันได้ | ยังไม่ทราบ/ยังค้าง | Evidence ID |
|---|---|---|---|---|---|
| Git root เป็นโฟลเดอร์แม่ | `git rev-parse --show-toplevel` → `~/coding`; repo แม่ไม่มี commit | `git init -b main` ใน `ws-exam` | repo แยก, commit ได้ | — | E001, E020, E021 |
| ข้อมูลส่งมาเป็น zip | ไม่พบ `.csv`; พบ `oab_cyber_risks_2_5mb.csv.zip` | unzip ไป scratchpad; pipeline รองรับ `.zip` | อ่านได้ 10,507 แถว | — | E005, E006 |
| SQL alias ชนคำสงวน | `Parser Error: syntax error at or near "share"` | เปลี่ยนชื่อ alias | query ผ่าน | — | E006, E009 |
| import package ไม่ได้ | `ModuleNotFoundError: No module named 'cyber_risk'` (ซ้ำหลัง `uv sync`) | เพิ่ม `pythonpath = ["src"]` | `19 passed` | สาเหตุ (AI ระบุว่า macOS ข้ามไฟล์ `.pth` ที่ถูกซ่อน) เป็น REPORTED ไม่ได้ตรวจยืนยัน | E013 |
| DuckDB lock ระหว่าง process | `IO Error: Could not set lock on file ... Conflicting lock is held` | เพิ่ม env `CYBER_RISK_DB`; ภายหลังเพิ่ม retry รอ lock | AppTest ผ่าน; จำลองแล้ว `waited 11s` | พฤติกรรมบน Coolify จริงยังไม่ทราบ | E016, E025 |
| Streamlit deprecation | `use_container_width will be removed after 2025-12-31` | เปลี่ยนเป็น `width="stretch"` | ไม่มีคำเตือนใน output ถัดไปที่ถูกกรอง | — | E037 |
| Label/แกนกราฟถูกตัด | ตรวจจาก screenshot; การเพิ่ม `padding` ทำให้แท่งหายและแกนซ้อน `0120` | ขยาย domain, เปลี่ยนกราฟรายหน่วยงานเป็น HTML bar list | screenshot 12:08:59 ไม่มีการล้น ที่ viewport แคบ | ยังไม่ตรวจที่ความกว้าง desktop | E015, E031 |
| `theme.py` ไม่ reload | CSS ใหม่ไม่ทำงานหลังแก้ไฟล์ | restart server | CSS ทำงาน | — | E031 |
| Browser pane ถูกปิด | `Error: invalid_params: Surface is not a browser` (หลายครั้ง) | เปิด surface ใหม่ | ทำงานต่อได้ | สาเหตุที่ pane ปิดไม่ทราบ | E036 |
| ไม่มี GitHub CLI | `command not found: gh` | ผู้สอบสร้าง repo เองและส่ง URL | push สำเร็จ | — | E020, E022 |
| Coolify team ส่วนตัวไม่มี server | "No available servers", "No servers yet" | ผู้สอบเปลี่ยนเป็น Root Team | พบ server `localhost` สถานะ "Validation required" | — | E028, E029 |
| Validate server ไม่ผ่าน | `Error: WARNING: Your password has expired.` | กด Validate 3 ครั้ง; AI เสนอคำสั่ง `chage` | ยังขึ้น Unavailable | **ยังค้าง** ไม่มีหลักฐานว่ามีการแก้; ไม่มี deploy | E029, E030 |
| ทดสอบหลังแก้ล่าสุด | แก้ CSS (grid) หลัง `25 passed` ครั้งสุดท้าย | ตรวจด้วย screenshot | screenshot 12:08:59 | ไม่ได้รัน pytest หลังการแก้ CSS ครั้งสุดท้าย | E032 |

---

## G. งานที่ส่งมอบ

### G1. Implementation ที่พบ (VERIFIED ว่าโค้ดมีอยู่ใน HEAD `ea5534d` เว้นที่ระบุ)
| ฟังก์ชัน | ตำแหน่ง | Evidence |
|---|---|---|
| รับ CSV/zip, ตัด BOM, เทียบ schema กับ contract (DQ-020) | `src/cyber_risk/pipeline.py` `extract_csv` (155), `_load_raw` (171), `_check_schema` (188) | E034 |
| Validation ระดับแถว (DQ-001/003/004/005/010/021/022) + quarantine | `STAGING_RULES` (217), `_run_staging_rules` (245) | E034 |
| สร้าง dims/facts/aggregates ใน DuckDB | `_build_semantic` (289) | E034 |
| ตรวจหลัง build (DQ-002/006/007/011–016, IT-003) | `SEMANTIC_RULES` (398) | E034 |
| Publication gate + `snapshot_registry` | `ingest` (480), `_finish` (467) | E034 |
| Metric queries (นับรวม/ปิด/ไม่ปิด, ราย BU, ตามคะแนน, Top 3, METRIC-06/07/08) | `src/cyber_risk/queries.py` (34–281) | E034 |
| Dashboard + upload + filter หน่วยงาน | `app.py` | E034 |
| UI ใหม่ + filter ผ่าน URL | `app.py`, `src/cyber_risk/theme.py` — **ยังไม่ commit** | E031, E032, E033 |

### G2. เส้นทางข้อมูล
CSV/zip → `raw_cyber_risk_source` (VARCHAR) → `stg_cyber_risk` → quality rules → `dim_business_unit`, `dim_owner`, `fact_risk_snapshot` → `fact_unresolved_risk_unit_snapshot`, `fact_unresolved_risk_score_snapshot` → `snapshot_registry` (`published`/`failed`) → query → Streamlit (E034)

### G3. ฐานข้อมูลและ persistence
- DuckDB file: local `data/cyber_risk.duckdb` (ignored); Docker `CYBER_RISK_DB=/data/cyber_risk.duckdb` + named volume `cyber_risk_data:/data` (E034)
- พิสูจน์ใน local Docker: หลัง restart → `[('published', 10507)]`, `(10507,)` (E024)

### G4. เอกสาร
spec 12 ไฟล์ใน `docs/specs/` (มีอยู่ก่อน session และถูกแก้ไขระหว่าง session), README (วิธีรัน, Docker, Coolify) (E021, E026)

### G5. หลักฐานใช้งานสำเร็จ (แยกจาก implementation)
| สิ่งที่ยืนยัน | หลักฐาน | สถานะ |
|---|---|---|
| Dashboard แสดงผลด้วยข้อมูลตัวอย่าง | AppTest metrics `10,507 / 2,528 / 7,979`; screenshot | VERIFIED (local) E014, E015 |
| Filter รายหน่วยงาน | AppTest HR `1,031 / 391 / 640`; Top 3 HR `R000608, R001210, R002115`; screenshot `?bu=HR` | VERIFIED (local) E014, E031 |
| Validation หยุด publish เมื่อพบ error | tests `test_error_rules_block_publication`, `test_ut009...` ผ่านใน pytest | VERIFIED เฉพาะผลรัน pytest E013 |
| อัปโหลด CSV ผ่าน UI | sidebar แสดง `oab_cyber_risks_2_5mb.csv · 2026-10-02 12:02:04 · 10,507 rows PUBLISHED` ขณะที่ไฟล์ที่ AI ใช้คือ `.csv.zip`; AI ไม่ได้อัปโหลดผ่าน UI ใน tool calls | INFERRED ว่าผู้สอบอัปโหลดเอง E031 |
| ใช้งานบน production | ไม่มี | UNKNOWN |

### G6. ข้อจำกัดที่พบ (จากหลักฐาน ไม่ได้ทดลองใหม่)
- ไม่มี authentication ในแอป (AI ระบุ; spec `Authentication Method = null`) — E026
- รันได้ 1 instance (DuckDB 1 writer process) — E023, E025
- นิยาม `open` = "ยังไม่เริ่ม" ยัง pending ใน glossary — E019
- Top 3 ถูกตัดสินด้วย tie-break (`score 25` = 471 รายการ) — E007

---

## H. หลักฐาน Test / Validation

### H1. ผลรันจริงใน session
| กรณี | คำสั่ง/ขั้นตอน | Expected | Actual | ผล | ช่วงเวลา/commit | Evidence |
|---|---|---|---|---|---|---|
| Golden values vs CSV | DuckDB CLI query | 10,507 / 7,979 / BU / 471 / Top 3 ตาม TESTING_STRATEGY | ตรงทุกค่า | ผ่าน | ก่อนมีโค้ดแอป | E007 |
| SQL ใหม่ (NULL score, registry, BU filter) | DuckDB CLI + ข้อมูลทดสอบที่ใส่เพิ่ม | NULL ไม่ขึ้นอันดับ 1; ใช้เฉพาะ snapshot published | เดิม `R000000 NULL` ขึ้นอันดับ 1; ใหม่ HR top 3 ถูก; total 7,980 | ผ่าน | ก่อนมีโค้ดแอป | E009 |
| pytest ชุดแรก | `uv run pytest -q` | ผ่าน | `19 passed in 9.73s` | ผ่าน | ก่อน `fcfb06f` | E013 |
| pytest + METRIC-06/07/08 | `uv run pytest -q` | ผ่าน | `24 passed in 3.21s` | ผ่าน | ก่อน `fcfb06f` | E019 |
| pytest หลังย้ายไฟล์ | `uv run pytest -q` | ผ่าน | `24 passed in 2.31s` | ผ่าน | ก่อน `fcfb06f` (สอดคล้องกับเนื้อหา commit) | E021 |
| pytest ก่อน commit Docker | `uv run pytest -q` | ผ่าน | `24 passed in 2.60s` | ผ่าน | ก่อน `ea5534d` | E026 |
| pytest + smoke test UI | `uv run pytest -q` | ผ่าน | `25 passed in 2.92s`, `25 passed in 3.07s` | ผ่าน | working tree ที่ยังไม่ commit | E032 |
| Docker healthcheck | `curl /_stcore/health`, `docker compose ps` | ok / healthy | `ok`, `Up 8 seconds (healthy)` | ผ่าน | ระหว่าง `fcfb06f`–`ea5534d` | E023 |
| Persistence | restart → อ่าน volume | ข้อมูลอยู่, ไม่โหลดซ้ำ | 1 snapshot, 10,507 แถว | ผ่าน | เดียวกัน | E024 |
| Lock ระหว่าง redeploy | container A ถือ lock 12s, B เปิดแอป | B รอแล้วเปิดได้ | `exception: False \| waited 11s` | ผ่าน | เดียวกัน | E025 |

### H2. Test code ที่พบ
`tests/test_pipeline.py`: HEAD มี 20 ฟังก์ชัน (1 ตัว parametrize 5 กรณี = 24 tests) working tree มี 21 ฟังก์ชัน (25 tests) ครอบคลุม golden values (MV-001–008), UT-001/002/008/009, error/warning rules, schema drift, BOM, idempotency และ dashboard smoke (E035)

### H3. ข้อจำกัด
- ผล pytest ครั้งสุดท้าย (`25 passed`) รันก่อนการแก้ CSS ครั้งสุดท้าย และอยู่บน working tree ที่ไม่ได้ commit (E032)
- ไม่มีผล test บน Coolify/production
- ไม่ได้รัน test ใหม่ในขั้นรวบรวมตามข้อกำหนด

---

## I. หลักฐาน Repo และ Coolify

| รายการ | ค่า | สถานะ | Evidence |
|---|---|---|---|
| Repo URL ปัจจุบัน | `git@github.com:ragnar-co/oab_cyber_risks.git` | VERIFIED (ใน session) | E027 |
| Repo เดิม | `git@github.com:patarawoot/oab_cyber_risks.git` (ผู้สอบแจ้งว่าย้ายแล้ว) | การย้าย: REPORTED; repo ใหม่มี `fcfb06f` อยู่แล้ว: VERIFIED | E022, E027 |
| Push `fcfb06f` | `* [new branch] main -> main`; `git ls-remote` = `fcfb06fef549…` | VERIFIED ว่า push สำเร็จในขณะนั้น | E022 |
| Push `ea5534d` | `fcfb06f..ea5534d  main -> main`; `git ls-remote` = `ea5534da4a78…` | VERIFIED ว่า push สำเร็จในขณะนั้น | E027 |
| เวลา push | หลัง commit time ของแต่ละ commit; ไม่มี timestamp ใน output | INFERRED ช่วงเวลา; เทียบเวลาสอบไม่ได้ (UNKNOWN) | E022, E027 |
| งานที่ไม่ได้ push | งาน UI (unstaged + untracked) | VERIFIED | E033 |
| Coolify instance | `https://coolify.ecs1.ragnar-ai.dev/` (อยู่หลัง Cloudflare Access) | VERIFIED ว่าเข้าถึงได้หลังผู้สอบ login | E028 |
| Coolify project | `oab_cyber_risks` / env `production` ใน team ส่วนตัว มี 0 resources (มีอยู่ก่อน AI เข้าดู ผู้สร้างไม่ทราบ) | VERIFIED | E028 |
| Server | Root Team `localhost` — "Validation required" / validate error "Your password has expired." | VERIFIED | E029 |
| Deployment ID / URL / commit ที่ deploy | ไม่พบ | UNKNOWN | E030 |
| Deploy ระดับ local | Docker image build + run healthy | VERIFIED (local เท่านั้น ไม่ใช่ Coolify) | E023 |

---

## J. หลักฐาน AI workflow โบนัส

- **Runtime AI workflow ในแอป:** ไม่พบหลักฐาน ค้น `anthropic|openai|claude|llm|gpt` ใน `src`, `app.py`, `tests`, `Dockerfile`, `docker-compose.yml`, `pyproject.toml` แล้วไม่พบ (E040) dependencies ใน pyproject มีแค่ duckdb, pandas, streamlit, altair
- **การใช้ AI ช่วยพัฒนา:** ใช้ Claude Code ทั้ง session (D1) ซึ่งไม่ใช่ runtime AI workflow ของแอป

---

## K. ตารางหลักฐานตามเกณฑ์สอบ

| หัวข้อ | หลักฐานที่รองรับ | Evidence ID | สถานะหลักฐาน | สิ่งที่ยังยืนยันไม่ได้ |
|---|---|---|---|---|
| ประโยชน์และฟังก์ชันหลัก | โค้ดครบตามโจทย์; AppTest และ screenshot แสดงตัวเลขและ filter | E014, E015, E031, E034 | VERIFIED (local) | การใช้งานบน production |
| การใช้ DDD | ใช้ spec 12 ไฟล์ (มีอยู่ก่อน session) เป็นฐาน; แก้ spec ให้ตรงกับ implementation | E002, E004, E008, E019 | UNKNOWN ว่า "DDD" หมายถึงอะไร / INFERRED ว่าใช้ spec ชุดนี้ | ผู้เขียนและที่มาของ spec; ความหมายของ DDD ในเกณฑ์ |
| ฐานข้อมูลและ persistence | DuckDB schema/ingest; Docker volume คงข้อมูลหลัง restart | E024, E034 | VERIFIED (local Docker) | persistence บน Coolify |
| Test / Validation | pytest 19→24→25 passed; golden values ตรง; Docker health | E007, E013, E019, E023, E032 | VERIFIED (ผลรันใน session) | ผลหลังแก้ CSS ครั้งสุดท้าย; ผลบน commit ที่ส่งสอบ (ไม่ทราบ commit) |
| Push repo และ Coolify deployment | push 2 commits สำเร็จ; Coolify ติด server validation | E022, E027, E028, E029, E030 | Push: VERIFIED / Deploy: UNKNOWN | เวลา push เทียบเวลาสอบ; deployment ใดๆ |
| การใช้งานและส่งมอบ | README วิธีรัน; Dockerfile/compose; งาน UI ยังไม่ commit | E021, E026, E033 | VERIFIED (สภาพ repo) | commit ที่ส่งสอบ |
| AI workflow โบนัส | ไม่พบ | E040 | ไม่พบหลักฐาน | — |

### เงื่อนไขบังคับ
| เงื่อนไข | สถานะ | Evidence | หมายเหตุ |
|---|---|---|---|
| ฟังก์ชันหลักใช้ได้ | VERIFIED (local) | E014, E015, E031 | ไม่ทราบเวลาเทียบกับเวลาสอบ |
| ใช้ DB จริง | VERIFIED | E024, E034 | DuckDB file + Docker volume |
| มี Test/Validation ผ่าน | VERIFIED (ผลรันใน session) | E013, E019, E032 | รันครั้งสุดท้ายบน working tree ที่ไม่ได้ commit |
| push ทันเวลา | UNKNOWN | E022, E027 | push สำเร็จ แต่ไม่ทราบเวลาสอบ/เวลา push จริง |
| deploy เปิดใช้ทันเวลา | UNKNOWN | E028, E029, E030 | ไม่พบหลักฐานการ deploy บน Coolify |

---

## L. Evidence Index

| ID | แหล่งข้อมูล / ตำแหน่ง | Excerpt (ปกปิดแล้ว) | ช่วงเวลา | ข้อเท็จจริงที่รองรับ |
|---|---|---|---|---|
| E001 | บริบทระบบตอนเริ่ม session (gitStatus) | `Current branch: main` · `?? ./` · `Recent commits:` (ว่าง) · Git user `patarawoot` | TIME_UNKNOWN (เริ่ม session) | repo แม่ `~/coding` ไม่มี commit; `ws-exam` เป็น untracked |
| E002 | Session tool: `ls`/`find` ใน `ws-exam` | 12 ไฟล์ `.md` + `.DS_Store` + `inputs/Pasted 2026-10-02 at 10.28.11 AM.textClipping`; `fatal: your current branch 'main' does not have any commits yet` | TIME_UNKNOWN | สภาพก่อนเริ่มงาน: มีแต่เอกสาร |
| E003 | Session tool: `plutil -p <textClipping>` | `"public.utf8-plain-text" => "oab_cyber_risks_2_5mb"` | TIME_UNKNOWN (ชื่อไฟล์ระบุ 10:28:11 แต่ไม่ใช่หลักฐานเด็ดขาด) | clipping มีแค่ชื่อไฟล์ |
| E004 | Session: คำตอบ AI วิเคราะห์ repo | ข้อขัดแย้ง 10 ข้อ เช่น METRIC-05 ไม่กรอง NULL, `MAX(snapshot_at)` ขัด DASHBOARD_SPEC | TIME_UNKNOWN | AI ทำการวิเคราะห์ (REPORTED โดย AI; ส่วนที่ยืนยันกับไฟล์ได้อยู่ใน E008/E009) |
| E005 | Session: ข้อความผู้สอบ + `ls inputs` | "แก้เลย CSV oab_cyber_risks_2_5mb.csv เอามาวางใน inputs แล้ว"; พบ `oab_cyber_risks_2_5mb.csv.zip` 168k | TIME_UNKNOWN | ผู้สอบให้ข้อมูลเป็น zip |
| E006 | Session: DuckDB profile | `10507 / 10507 ids / 0 null`; status `open 4277, in_progress 3702, closed 2528`; likelihood/impact 1–5; owners 48 | TIME_UNKNOWN | ข้อมูลสะอาด |
| E007 | Session: DuckDB golden check | `unresolved 7979`; Operations 2123 … HR 640; `s25 471`; Top3 `R000004/Owner-39, R000007/Owner-48, R000008/Owner-04` | TIME_UNKNOWN | golden values ตรง |
| E008 | Session: Edit/Write บน spec (METRIC_LOGIC, DATA_MODEL_SPEC, PIPELINE_SPEC, DASHBOARD_SPEC, TESTING_STRATEGY) | "has been updated successfully" / `ok` | TIME_UNKNOWN | AI แก้ spec |
| E009 | Session: DuckDB `t.sql` | เดิม `R000000 NULL` อันดับ 1; ใหม่ HR `R000608, R001210, R002115`; total `7980` | TIME_UNKNOWN | SQL ใหม่ทำงานถูกต้อง |
| E010 | Session: ข้อความผู้สอบ (โจทย์) | "จงสร้างแอป “Client Cyber Risk Dashboard” รับ CSV ตัวอย่าง ตรวจสอบข้อมูล และจัดเก็บลง DuckDB …" | TIME_UNKNOWN | เนื้อหาโจทย์ |
| E011 | Session: env check + `uv sync` | `Python 3.14.7`, `uv 0.12.18`, `ModuleNotFoundError: No module named 'duckdb'` → ติดตั้งสำเร็จ | TIME_UNKNOWN | ตั้งค่า environment |
| E012 | Session: Write `src/cyber_risk/pipeline.py`, `queries.py`, `tests/test_pipeline.py` | "File created successfully" | TIME_UNKNOWN | AI สร้างโค้ด |
| E013 | Session: pytest | `ModuleNotFoundError: No module named 'cyber_risk'` → `19 passed in 9.73s` | TIME_UNKNOWN | tests ผ่านหลังแก้ |
| E014 | Session: AppTest | `('ความเสี่ยงทั้งหมด','10,507'), ('ปิดแล้ว (closed)','2,528'), ('ยังไม่ปิด …','7,979')`; HR `1,031 / 391 / 640`; HR owners `Owner-11, Owner-13, Owner-10` | snapshot ในแอป 11:17:32 | dashboard ทำงาน |
| E015 | Session: cmux screenshot (ไฟล์ชั่วคราว epoch 1790914689 = 11:18:09 +07 และภาพถัดไป) | Dashboard แสดง KPI, กราฟ, Top 3 | 11:18:09 เป็นต้นไป | UI render บน localhost:8599 |
| E016 | Session: AppTest error | `IO Error: Could not set lock on file ".../data/cyber_risk.duckdb": Conflicting lock is held …` → เพิ่ม `CYBER_RISK_DB` | TIME_UNKNOWN | ปัญหา lock และวิธีแก้ |
| E017 | Session: แก้ `DATA_QUALITY.md` (DQ-021/022), README, `.gitignore` | `ok` | TIME_UNKNOWN | AI เพิ่ม rule ในเอกสาร |
| E018 | Session: EDA (`eda.sql`, `eda2.sql`, `eda3.sql`) + คำตอบ AI | close rate Operations 15.2% … HR 37.9%; issue/owner ผูก 1 BU; matrix 5×5 | TIME_UNKNOWN | ที่มาของข้อเสนอกราฟ |
| E019 | Session: "เอาแค่ 1 2 3 พอ" + tests + AppTest matrix + screenshot epoch 1790915254 (11:27:34) | `24 passed in 3.21s`; matrix `Likelihood 5: 0 449 497 505 471`; `HR sum 640` | 11:27:34 | METRIC-06/07/08 |
| E020 | Session: git/gh check | `git rev-parse --show-toplevel` → `~/coding`; `command not found: gh` | TIME_UNKNOWN (ก่อน 11:30:54) | ต้องสร้าง repo แยก |
| E021 | Session: reorg + `git init` + commit; `git show --stat fcfb06f` (รวบรวม) | `24 passed in 2.31s`; staged 23 ไฟล์; `fcfb06f … 2026-10-02 11:30:54 +0700 … feat: Client Cyber Risk Dashboard` | 11:30:54 | commit แรก |
| E022 | Session: AskUserQuestion + push | คำตอบ "มี repo ว่างแล้ว ส่ง URL ให้"; URL `git@github.com:patarawoot/oab_cyber_risks.git`; `* [new branch] main -> main`; ls-remote `fcfb06fef549…` | หลัง 11:30:54 | push ครั้งแรก |
| E023 | Session: Docker | `29.4.3`; `Image ws-exam-dashboard Built`; `ok`; `ws-exam-dashboard-1 Up 8 seconds (healthy)` | ระหว่าง 11:30:54–11:41:29 | local container ทำงาน |
| E024 | Session: volume/persistence | `/data` owner `app`; หลัง restart `[('published', 10507)]` `(10507,)` | เดียวกัน | persistence ใน volume |
| E025 | Session: lock simulation | `exception: False \| waited 11s \| metrics: ['10,507', '2,528', '7,979']` | เดียวกัน | retry lock ทำงาน |
| E026 | Session: pytest + commit; `git log` (รวบรวม) | `24 passed in 2.60s`; `ea5534d … 2026-10-02 11:41:29 +0700 … build: add Docker image and Coolify deployment guide` | 11:41:29 | commit ที่สอง |
| E027 | Session: ข้อความผู้สอบ + set-url + push | "push เลย แต่ว่าย้ายไป git@github.com:ragnar-co/oab_cyber_risks.git แล้ว"; ls-remote ก่อน push `fcfb06f…`; `fcfb06f..ea5534d  main -> main`; หลัง push `ea5534da4a78…` | หลัง 11:41:29 | push ไป repo ใหม่ |
| E028 | Session: cmux บน Coolify | redirect ไป GitHub login ของ Cloudflare Access (พารามิเตอร์ `iat` = 11:47:32; token [REDACTED]); หลัง login: `patarawoot's Team`, project `oab_cyber_risks` "0 resources", "No available servers", "No servers yet" | 11:47:32 เป็นต้นไป | สภาพ Coolify team ส่วนตัว |
| E029 | Session: cmux Root Team server page + screenshot epoch 1790916778 (11:52:58) | `localhost` "Validation required"; Ubuntu 24.04.4, x86_64, 8 cores, 31.3 GB; `Error: WARNING: Your password has expired.` | 11:52:58 | validate server ไม่ผ่าน |
| E030 | Session: ข้อความผู้สอบ | "ไม่เป็นไร กลับมา app ดีกว่า …" | หลัง 11:52:58 | หยุดงาน deploy; ไม่มี deployment |
| E031 | Session: ปรับ UI — Write `theme.py`, แก้ `app.py`, restart server, screenshots epoch 1790917396 (12:03:16) ถึง 1790917739 (12:08:59) | sidebar: `oab_cyber_risks_2_5mb.csv · 2026-10-02 12:02:04 · 10,507 rows` `PUBLISHED`; `?bu=HR` → KPI `1,031 / 391 / 640` | 12:02:04–12:08:59 | UI ใหม่ทำงาน (local); ร่องรอยการอัปโหลดผ่าน UI |
| E032 | Session: pytest หลังเพิ่ม smoke test | `25 passed in 2.92s`; `25 passed in 3.07s`; จากนั้นแก้ CSS grid อีกครั้งโดยไม่รัน pytest | ก่อน 12:10:32 | ผล test ล่าสุดและข้อจำกัด |
| E033 | หลังสอบ: คำสั่งอ่านอย่างเดียว | `2026-10-02 12:10:32 +07`; `* main ea5534d [origin/main]`; ` M .streamlit/config.toml`, ` M app.py`, ` M tests/test_pipeline.py`, `?? src/cyber_risk/theme.py` | AFTER_EXAM | สภาพตอนรวบรวม |
| E034 | Repo HEAD: `git show HEAD:<file>` | `pipeline.py`: `REQUIRED_FIELDS` 23, `ingest` 480, `SEMANTIC_RULES` 398; `queries.py`: 34–281; Dockerfile: `ENV CYBER_RISK_DB=/data/cyber_risk.duckdb`, `HEALTHCHECK`, `EXPOSE 8501`, `USER app`; compose: `cyber_risk_data:/data` | AFTER_EXAM (อ่านจาก commit) | implementation และ persistence ที่ commit |
| E035 | Repo: `rg -c '^def test_'` | HEAD `20`; working tree `21` | AFTER_EXAM | จำนวน test functions |
| E036 | Session: cmux error | `Error: invalid_params: Surface is not a browser` (หลายครั้ง) | TIME_UNKNOWN | browser pane ถูกปิดระหว่างงาน |
| E037 | Session: AppTest output | ``use_container_width` will be removed after 2025-12-31.`` | TIME_UNKNOWN | deprecation และการแก้ |
| E038 | Repo: `docs/specs/DASHBOARD_SPEC.md` (CHART-04) | "Dashboard ห้ามแปลงคะแนนเป็น: Low Medium High Critical จนกว่าจะมี approved/calibrated bucket rule" | ไฟล์มีอยู่ก่อน session | ที่มาของการไม่แบ่ง bucket |
| E039 | Session: system context | Model `Opus 5.5` (Claude Code); hook "CAVEMAN MODE ACTIVE" | ตลอด session | เครื่องมือ AI ที่ใช้ |
| E040 | หลังสอบ: `rg -n -i 'anthropic\|openai\|claude\|llm\|gpt' …` และ `rg -n -i '\bddd\b\|domain[- ]driven\|data[- ]driven'` | ไม่มีผลลัพธ์ทั้งสองคำสั่ง | AFTER_EXAM | ไม่พบ runtime AI และไม่พบคำว่า DDD |
| E041 | หลังสอบ: `date -r <epoch>` แปลงชื่อไฟล์ screenshot / `iat` | `1790914689 -> 11:18:09`, `1790915254 -> 11:27:34`, `1790916452 -> 11:47:32`, `1790916778 -> 11:52:58`, `1790917396 -> 12:03:16`, `1790917739 -> 12:08:59` (+07) | AFTER_EXAM | ที่มาของเวลาที่ใช้ในตาราง C |

---

## ข้อมูลที่กรรมการต้องตรวจเพิ่ม
1. เวลาเริ่มและหมดเวลาสอบ และ commit ที่ผู้สอบประกาศส่ง
2. เวลาที่ GitHub บันทึก push ของ `fcfb06f` และ `ea5534d` บน `ragnar-co/oab_cyber_risks` (ดูจากหน้า GitHub หรือ audit log) และยืนยันการย้ายจาก `patarawoot/oab_cyber_risks`
3. สถานะ Coolify: มี resource/deployment ของแอปนี้หรือไม่ นอกเหนือจากที่เห็นใน session
4. ที่มาและผู้เขียนเอกสาร spec 12 ไฟล์ และความหมายของ "โจทย์ DDD" ในเกณฑ์
5. การตรวจงานที่ยังไม่ commit (UI) ว่าอยู่ในขอบเขตการให้คะแนนหรือไม่
6. ชื่อจริงและตำแหน่งของผู้สอบ
