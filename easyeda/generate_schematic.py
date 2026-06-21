#!/usr/bin/env python3
"""
RP2040W-BAT 전원부 — EasyEDA Standard 스키매틱 '시각 초안' 생성기.

EasyEDA Standard 의 'Open EasyEDA File' 로 임포트 가능한 schematic 문서(JSON)를 만든다.
부품은 라벨 붙은 사각형 블록, 연결은 net 이름이 붙은 선으로 표현한 *블록 초안*이다.
(기능 핀/심볼은 없음 — 회로 정본은 ../hardware/netlist.md + bom.csv)

사용: python3 generate_schematic.py  ->  power-section.schematic.json
"""
import json
import uuid

shapes = []
_gid = 0


def gid():
    global _gid
    _gid += 1
    return f"gge{_gid}"


def rect(x, y, w, h, stroke="#000000"):
    shapes.append(f"R~{x}~{y}~0~0~{w}~{h}~{stroke}~1~0~none~{gid()}~")


def text(x, y, s, color="#000000", size="12px"):
    # T~comp~x~y~rot~fill~~font~~size~~~~string~~gid~start
    shapes.append(f"T~comp~{x}~{y}~0~{color}~~~~{size}~~~~{s}~~{gid()}~start")


def wire(pts, color="#0066CC"):
    coords = " ".join(f"{x} {y}" for x, y in pts)
    shapes.append(f"W~{coords}~{color}~1~0~none~{gid()}~0")


def block(x, y, w, h, ref, name, pins_left=None, pins_right=None):
    """부품 블록: 사각형 + 지정자/이름 + 좌/우 핀 라벨."""
    rect(x, y, w, h)
    text(x + 6, y + 16, ref, color="#CC0000", size="13px")
    text(x + 6, y + 32, name, color="#000000", size="11px")
    pins_left = pins_left or []
    pins_right = pins_right or []
    step = 22
    anchors = {}
    for i, p in enumerate(pins_left):
        py = y + 50 + i * step
        text(x + 6, py, p, size="10px")
        # 핀 스텁(왼쪽으로 12px)
        wire([(x, py - 3), (x - 12, py - 3)], color="#000000")
        anchors[p] = (x - 12, py - 3)
    for i, p in enumerate(pins_right):
        py = y + 50 + i * step
        text(x + w - 6 - len(p) * 6, py, p, size="10px")
        wire([(x + w, py - 3), (x + w + 12, py - 3)], color="#000000")
        anchors[p] = (x + w + 12, py - 3)
    return anchors


def netlabel(x, y, net, color="#0066CC"):
    text(x, y, net, color=color, size="11px")


# ───────────────────────── 블록 배치 ─────────────────────────
# 흐름: USB-C → BQ25180(VIN/SYS/BAT) → VSYS → RT6150 → 3V3
#                                   └ BAT → 배터리

usbc = block(60, 80, 150, 220, "J1", "USB-C 16P",
             pins_right=["VBUS x4", "CC1>5.1k", "CC2>5.1k", "D+ (A6/B6)", "D- (A7/B7)", "GND x4"])

bq = block(360, 80, 170, 260, "U3", "BQ25180\n충전+파워패스+ship",
           pins_left=["IN", "SDA", "SCL", "/INT", "CE/BTN", "TS"],
           pins_right=["SYS", "BAT", "GND"])

rt = block(700, 80, 160, 170, "U4", "RT6150\nVSYS->3V3",
           pins_left=["VIN", "EN", "PS"],
           pins_right=["VOUT=3V3", "SW(L)", "GND"])

bat = block(360, 420, 150, 90, "J2", "1S LiPo (JST)",
            pins_left=["BAT+", "BAT-"])

rp = block(700, 360, 170, 150, "U1", "RP2040 (USB)",
           pins_left=["USB_DP", "USB_DM", "VREG_VIN=3V3"])

# ───────────────────────── 연결 (net 라벨 + 선) ─────────────────────────
# VBUS_USB: USB-C VBUS -> BQ25180 IN
wire([usbc["VBUS x4"], (300, 89), (300, 133), bq["IN"]])
netlabel(255, 78, "VBUS_USB")

# D± : USB-C -> 직렬27 -> RP2040 USB
wire([usbc["D+ (A6/B6)"], (250, 177), (250, 372), rp["USB_DP"]], color="#9900AA")
netlabel(255, 360, "USB_DP >27R")
wire([usbc["D- (A7/B7)"], (240, 199), (240, 394), rp["USB_DM"]], color="#9900AA")
netlabel(255, 392, "USB_DM >27R")

# SYS -> VSYS -> RT6150 VIN
wire([bq["SYS"], (600, 133), (600, 133), rt["VIN"]])
netlabel(560, 120, "VSYS (=39핀)")

# BAT -> 배터리
wire([bq["BAT"], (560, 155), (560, 470), bat["BAT+"]], color="#008800")
netlabel(560, 300, "VBAT")

# 3V3 -> RP2040 VREG_VIN
wire([rt["VOUT=3V3"], (900, 133), (900, 416), rp["VREG_VIN=3V3"]], color="#CC6600")
netlabel(905, 250, "3V3 (=36핀)")

# I2C
netlabel(300, 155, "I2C_SDA->GPIO20")
netlabel(300, 177, "I2C_SCL->GPIO21")
netlabel(300, 199, "BQ_INT->GPIO22")
netlabel(300, 221, "PWR_BTN(3s)")

# EN / PS
netlabel(640, 155, "EN_3V3<-37핀")
netlabel(640, 177, "PS<-WL_GPIO1")

# 주석
text(60, 40, "RP2040W-BAT  Power Section  (VISUAL DRAFT — 정본: hardware/netlist.md)",
     color="#000000", size="14px")
text(60, 560, "주의: CC 5.1k x2 따로 / D+- 양 페어 묶기 / SYS->VSYS, VBUS핀 직결금지 / 충전부는 IC로",
     color="#CC0000", size="11px")
text(60, 580, "IC 핀번호는 데이터시트 확정 후 배선. 이 파일은 배치 감용 블록 그림.",
     color="#888888", size="10px")

# ───────────────────────── 문서 래핑 ─────────────────────────
doc = {
    "editorVersion": "6.5.46",
    "docType": "1",
    "title": "RP2040W-BAT Power Section (DRAFT)",
    "description": "Visual block draft. Authoritative netlist: hardware/netlist.md",
    "colors": {},
    "canvas": "CA~1100~700~#FFFFFF~yes~#CCCCCC~10~1100~700~line~1~pixel~5~0~~0~",
    "head": {
        "docType": "1",
        "editorVersion": "6.5.46",
        "newgId": True,
        "c_para": {"Prefix Start": "1"},
        "x": 0,
        "y": 0,
        "uuid": uuid.uuid4().hex,
        "importFlag": 0,
        "transformList": "",
    },
    "shape": shapes,
    "BBox": {"x": 0, "y": 0, "width": 1100, "height": 700},
}

with open("power-section.schematic.json", "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)

print(f"wrote power-section.schematic.json  ({len(shapes)} shapes)")
