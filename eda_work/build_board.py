#!/usr/bin/env python3
"""
Alta(.eprj2) EasyEDA Pro 프로젝트에 'RP2040W-BAT' 보드를 추가한다.

전략(블라인드 편집 신뢰성):
  - 원본은 절대 수정 안 함. 복사본에서만 작업.
  - 검증된 기존 보드(RP2040 schematic1)의 '구조 패턴'을 그대로 복제 -> 새 보드 등록.
  - 스키매틱 내용 = 검증된 RP2040 스키매틱(RP2040/USB-C/플래시/크리스탈/ESD)을 재사용,
    보드명만 RP2040W-BAT 로 바꾸고 배터리/충전부 설계 노트(LCSC 부품/넷)를 네이티브 TEXT로 추가.
  - 충전 IC(BQ25180/RT6150/JST)는 EasyEDA에서 LCSC 검색으로 1클릭 배치(검증된 심볼+풋프린트).
    -> 오프라인 풋프린트 자작(렌더 깨질 위험)을 피하는 정석 워크플로.
  - 빈 PCB 문서 추가.
모든 단계 후 DB 무결성/디코드 라운드트립/FK 정합성 검증.
"""
import sqlite3, base64, gzip, io, json, uuid, time, shutil, os

SRC = "/root/.claude/uploads/ec9aac89-1629-56ca-91a4-9679bb8b8dc5/26e1f5ff-Alta.eprj2"
OUT = "eda_work/RP2040W-BAT.eprj2"

def decode(s):
    return gzip.decompress(base64.b64decode(s[6:])).decode("utf-8") if isinstance(s,str) and s.startswith("base64") else s
def encode(text):
    buf=io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as g:
        g.write(text.encode("utf-8"))
    return "base64"+base64.b64encode(buf.getvalue()).decode("ascii")

os.makedirs("eda_work", exist_ok=True)
shutil.copyfile(SRC, OUT)
db=sqlite3.connect(OUT); c=db.cursor()

PROJ = c.execute("SELECT uuid FROM projects").fetchone()[0]
SRC_SHEET = 'f078243594864b1b840060c13b105b86'   # 검증된 RP2040 스키매틱 시트

# 새 uuid
S   = uuid.uuid4().hex   # schematics.uuid (= boards.sch)
DOC = uuid.uuid4().hex   # 시트 document.uuid
PCB = uuid.uuid4().hex   # pcb document.uuid (= boards.pcb)
now = int(time.time())
now_dt = time.strftime("%Y-%m-%d %H:%M:%S")

# ── 1) 스키매틱 내용: 검증된 시트 재사용 + 보드명 변경 + 배터리/충전 노트 ──
sch = decode(c.execute("SELECT dataStr FROM documents WHERE uuid=?", (SRC_SHEET,)).fetchone()[0])
sch = sch.replace('"@Board Name","RP2040",', '"@Board Name","RP2040W-BAT",')
sch = sch.replace('"@Schematic Name","Schematic1",', '"@Schematic Name","RP2040W-BAT",')

notes = [
  ["FONTSTYLE","ns_t",None,"#C00000",None,28,None,None,None,None,None,None],
  ["FONTSTYLE","ns_h",None,"#000080",None,16,None,None,None,None,None,None],
  ["FONTSTYLE","ns_b",None,None,None,12,None,None,None,None,None,None],
  ["TEXT","nt0", 900,1640,0,"=== RP2040W-BAT : 배터리/충전부 추가 설계 (EasyEDA에서 LCSC 배치) ===","ns_t",0],
  ["TEXT","nt1", 900,1680,0,"전력흐름: USB-C VBUS -> BQ25180 VIN -> (파워패스) SYS -> VSYS(39) -> RT6150 벅부스트 -> 3V3","ns_h",0],
  ["TEXT","nt2", 900,1710,0,"          BQ25180 BAT -> 1S LiPo(JST PH 2P).  3V3는 항상 VSYS에서 생성.","ns_b",0],
  ["TEXT","nt3", 900,1745,0,"추가 부품(LCSC 검색해 배치):","ns_h",0],
  ["TEXT","nt4", 900,1772,0,"  - BQ25180  충전+파워패스+ship+I2C  (LCSC C2682744)","ns_b",0],
  ["TEXT","nt5", 900,1796,0,"  - RT6150B  VSYS->3V3 벅부스트       (LCSC C2830944)","ns_b",0],
  ["TEXT","nt6", 900,1820,0,"  - JST PH 2P 배터리 커넥터           (LCSC C173752)","ns_b",0],
  ["TEXT","nt7", 900,1844,0,"  - L 2.2uH(C167219), NTC 10k(TS), 1uF x3, 10uF/22uF, 5.1k CC x2 등","ns_b",0],
  ["TEXT","nt8", 900,1878,0,"넷 결선(상세 hardware/netlist.md):","ns_h",0],
  ["TEXT","nt9", 900,1905,0,"  VBUS_USB=BQ.IN  | SYS=VSYS=RP2040 39 | BAT=VBAT=JST+ | VOUT=3V3=RP2040 36","ns_b",0],
  ["TEXT","nt10",900,1929,0,"  SDA/SCL->GPIO20/21(4.7k 풀업) | INT->GPIO22 | EN<-37핀 | PS<-WL_GPIO1","ns_b",0],
  ["TEXT","nt11",900,1953,0,"  CC1/CC2 각각 5.1k->GND(따로!) | D+/- 양 페어 묶기 | VBUS핀 직결 금지(역류)","ns_b",0],
  ["TEXT","nt12",900,1987,0,"전원로직: 유선=켜짐 / 버튼3초=켜짐 / 소프트웨어 종료=ship(배터리 차단)","ns_h",0],
]
sch = sch.rstrip("\n") + "\n" + "\n".join(json.dumps(r, ensure_ascii=False) for r in notes) + "\n"
SCH_ENC = encode(sch)

# ── 2) 빈 PCB 문서 ──
pcb_empty = '["DOCTYPE","PCB","1.8"]\n["HEAD",{"editorVersion":"2.2.40.8","importFlag":0}]\n["CANVAS",1015.3822,-574.6178,"mm",5,5,5,5,1,1,2,0,5]\n'
PCB_ENC = encode(pcb_empty)

# ── 3) schematics 행 ──
c.execute("""INSERT INTO schematics
 (uuid,description,ticket,sheet_count,project_uuid,name,display_name,createtime,updatetime,created_at,updated_at,sort)
 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
 (S,"",1,1,PROJ,"schematic5","RP2040W-BAT",now,now,now_dt,now_dt,DOC))

# ── 4) documents 행 (시트 + PCB) ──
c.execute("""INSERT INTO documents
 (uuid,title,display_title,description,docType,dataStr,sheet_id,ticket,sort_ticket,created_at,updated_at,creator_uuid,schematic_uuid,project_uuid,image,parent_uuid)
 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
 (DOC,"p1","P1","",1,SCH_ENC,1,1,0,now_dt,now_dt,None,S,PROJ,None,None))
c.execute("""INSERT INTO documents
 (uuid,title,display_title,description,docType,dataStr,sheet_id,ticket,sort_ticket,created_at,updated_at,creator_uuid,schematic_uuid,project_uuid,image,parent_uuid)
 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
 (PCB,"pcb5","PCB5","",3,PCB_ENC,1,1,0,now_dt,now_dt,None,"",PROJ,None,None))

# ── 5) projects.boards JSON 추가 ──
boards = json.loads(c.execute("SELECT boards FROM projects").fetchone()[0])
boards.append({"sch":S,"name":"RP2040W-BAT","pcb":PCB})
c.execute("UPDATE projects SET boards=? WHERE uuid=?", (json.dumps(boards), PROJ))

# ── 6) project_structures 에도 추가(트리 표시용; 모든 동일 행 갱신) ──
BID  = uuid.uuid4().hex[:16]
SHID = uuid.uuid4().hex[:16]
rows = c.execute("SELECT id,structure FROM project_structures").fetchall()
for rid, st in rows:
    obj=json.loads(st)
    zb = max([b.get("zIndex",0) for b in obj.get("boards",{}).values()] or [0])+1
    obj.setdefault("boards",{})[BID]={"uuid":BID,"title":"RP2040W-BAT","zIndex":zb}
    obj.setdefault("schematics",{})[S]={"uuid":S,"name":"RP2040W-BAT","board":BID,"source":"","version":str(now*1000),"updateTime":now*1000}
    obj.setdefault("sheets",{})[SHID]={"uuid":SHID,"title":"P1","schematic_uuid":S,"zIndex":1,"source":"","version":str(now*1000),"updateTime":now*1000}
    c.execute("UPDATE project_structures SET structure=? WHERE id=?", (json.dumps(obj, ensure_ascii=False), rid))

db.commit()
print(f"새 보드 등록: name=RP2040W-BAT  sch={S}  pcb={PCB}  doc={DOC}")

# ── 7) 검증 ──
print("integrity_check:", c.execute("PRAGMA integrity_check").fetchone()[0])
print("foreign_key_check:", c.execute("PRAGMA foreign_key_check").fetchall())
# 디코드 라운드트립
back=decode(c.execute("SELECT dataStr FROM documents WHERE uuid=?", (DOC,)).fetchone()[0])
print("sheet decode ok:", back.split(chr(10))[0], "| has board name:", '"RP2040W-BAT"' in back, "| notes:", '배터리/충전부' in back)
bp=decode(c.execute("SELECT dataStr FROM documents WHERE uuid=?", (PCB,)).fetchone()[0])
print("pcb decode ok:", bp.split(chr(10))[0])
# boards JSON FK 정합성: 모든 sch/pcb 가 존재하는가
boards=json.loads(c.execute("SELECT boards FROM projects").fetchone()[0])
allsch={r[0] for r in c.execute("SELECT uuid FROM schematics")}
alldoc={r[0] for r in c.execute("SELECT uuid FROM documents")}
ok=all(b["sch"] in allsch and b["pcb"] in alldoc for b in boards)
print("boards JSON refs resolve:", ok, "| total boards:", len(boards))
# JSON 유효성
for rid,st in c.execute("SELECT id,structure FROM project_structures").fetchall()[:1]:
    json.loads(st); print("structure JSON valid (sample row", rid, ")")
db.close()
print("OUT:", OUT, os.path.getsize(OUT), "bytes")
