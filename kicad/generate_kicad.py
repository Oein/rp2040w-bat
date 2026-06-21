#!/usr/bin/env python3
"""
RP2040W-BAT -> KiCad 8 프로젝트 생성기.

산출:
  kicad/rp2040w-bat.kicad_sch   (전체 보드 스키매틱; 심볼 임베드 + 글로벌라벨 결선)
  kicad/rp2040w-bat.kicad_pro   (프로젝트 파일)
  kicad/rp2040w_bat.kicad_sym   (편집용 심볼 라이브러리)
  kicad/sym-lib-table           (프로젝트 라이브러리 등록)

설계 원칙(블라인드 생성의 신뢰성 확보):
  - 모든 심볼을 직접 정의 -> 핀 좌표를 정확히 안다.
  - 넷 연결은 '글로벌 라벨(이름 기반)'로 -> 같은 이름끼리 자동 연결, 배선 좌표 의존 최소.
  - 부품은 충분히 떨어뜨려 배치 -> 서로 다른 핀이 같은 좌표에 겹쳐 오연결되는 것 방지.

주의: 핀 '번호'는 복잡 IC의 경우 기능명을 그대로 사용(데이터시트로 풋프린트 패드와 매핑 필요).
      KiCad에서 열어 ERC/풋프린트 확인 후 사용하는 '시작점' 프로젝트다.
"""
import uuid

GRID = 2.54
L = 3.81          # 핀 길이
NS = "rp2040w_bat"  # 심볼 라이브러리 이름

def U():            # uuid 생성
    return str(uuid.uuid4())

ROOT = U()

# ─────────────────────────── 부품 정의 ───────────────────────────
# comp = dict(ref, prefix, value, fp, left=[(name,net)], right=[(name,net)])
# net=None 이면 No-Connect.
comps = []
def add(ref, prefix, value, fp, left=None, right=None):
    comps.append(dict(ref=ref, prefix=prefix, value=value, fp=fp,
                      left=left or [], right=right or []))

# --- MCU ---
add("U1", "U", "RP2040", "Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm",
    left=[("VREG_VIN","3V3"),("VREG_VOUT","DVDD"),("IOVDD","3V3"),("USB_VDD","3V3"),
          ("ADC_AVDD","3V3_ADC"),("GND","GND"),
          ("XIN","XIN"),("XOUT","XOUT"),("USB_DP","RP_DP"),("USB_DM","RP_DM"),
          ("QSPI_SS","QSPI_SS"),("QSPI_SCLK","QSPI_SCLK"),
          ("QSPI_SD0","QSPI_SD0"),("QSPI_SD1","QSPI_SD1"),
          ("QSPI_SD2","QSPI_SD2"),("QSPI_SD3","QSPI_SD3"),
          ("RUN","RUN"),("SWDIO","SWDIO"),("SWCLK","SWCLK"),
          ("WL_CLK","WL_CLK"),("WL_CS","WL_CS"),("WL_DAT","WL_DAT"),("WL_REGON","WL_REG_ON")],
    right=[("GP0","GP0"),("GP1","GP1"),("GP2","GP2"),("GP3","GP3"),("GP4","GP4"),
           ("GP5","GP5"),("GP6","GP6"),("GP7","GP7"),("GP8","GP8"),("GP9","GP9"),
           ("GP10","GP10"),("GP11","GP11"),("GP12","GP12"),("GP13","GP13"),("GP14","GP14"),
           ("GP15","GP15"),("GP16","GP16"),("GP17","GP17"),("GP18","GP18"),("GP19","GP19"),
           ("GP20_SDA","I2C_SDA"),("GP21_SCL","I2C_SCL"),("GP22_INT","BQ_INT"),
           ("GP26_VBUS","VBUS_SENSE"),("GP27","GP27"),("GP28","GP28")])

# --- 플래시 (W25Q128 SOIC-8 실제 핀번호) ---
add("U2", "U", "W25Q128", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
    left=[("1_CS","QSPI_SS"),("2_DO_IO1","QSPI_SD1"),("3_WP_IO2","QSPI_SD2"),("4_GND","GND")],
    right=[("8_VCC","3V3"),("7_HOLD_IO3","QSPI_SD3"),("6_CLK","QSPI_SCLK"),("5_DI_IO0","QSPI_SD0")])

# --- 충전 IC BQ25180 (핀=기능명; 볼맵 데이터시트 확정 필요) ---
add("U3", "U", "BQ25180", "Package_BGA:Texas_DSBGA-9_1.41x1.46mm_Layout3x3_P0.4mm",
    left=[("IN","VBUS_USB"),("SDA","I2C_SDA"),("SCL","I2C_SCL"),("INT","BQ_INT"),
          ("CE_BTN","PWR_BTN"),("TS","BAT_TS")],
    right=[("SYS","VSYS"),("BAT","VBAT"),("GND","GND")])

# --- 벅부스트 RT6150 (핀=기능명; 데이터시트 확정 필요) ---
add("U4", "U", "RT6150B", "Package_DFN_QFN:WDFN-10-1EP_3x3mm_P0.5mm_EP1.5x2.4mm",
    left=[("VIN","VSYS"),("EN","EN_3V3"),("PS","PS_CTRL"),("GND","GND")],
    right=[("VOUT","3V3"),("SW1","SW1_BB"),("SW2","SW2_BB")])

# --- 무선 CYW43439 (핀=기능명; Pico W 복제) ---
add("U5", "U", "CYW43439", "Package_BGA:CYW43439_FBGA",
    left=[("VBAT","3V3"),("VDDIO","3V3"),("GND","GND"),("REG_ON","WL_REG_ON"),
          ("SPI_CLK","WL_CLK"),("SPI_CS","WL_CS"),("SPI_D","WL_DAT")],
    right=[("WL_GPIO0_LED","LED_A"),("WL_GPIO1_PS","PS_CTRL"),
           ("WL_GPIO2_VBUS","VBUS_SENSE2"),("RF","ANT")])

# --- USB-C 16P (병렬핀 통합 표기) ---
add("J1", "J", "USB_C_Receptacle", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
    left=[("VBUS","VBUS_USB"),("GND","GND"),("CC1","CC1"),("CC2","CC2"),("SHIELD","GND")],
    right=[("DP_A6B6","USB_DP"),("DM_A7B7","USB_DM"),("SBU1","None"),("SBU2","None")])

# --- 배터리 커넥터 ---
add("J2", "J", "Battery_1S", "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm",
    left=[("1_BATP","VBAT"),("2_GND","GND")])

# --- ESD/TVS ---
add("U6", "U", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6",
    left=[("IO1","USB_DP"),("VBUS","VBUS_USB"),("IO2","USB_DM")],
    right=[("GND1","GND"),("GND2","GND"),("VBUS2","VBUS_USB")])
add("D1", "D", "SMF5.0A_TVS", "Diode_SMD:D_SOD-123",
    left=[("A","VBUS_USB")], right=[("K","GND")])

# --- 크리스탈 ---
add("Y1", "Y", "12MHz", "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm",
    left=[("1","XIN")], right=[("2","XOUT")])

# --- 인덕터 ---
add("L1", "L", "2.2uH", "Inductor_SMD:L_1210_3225Metric",
    left=[("1","SW1_BB")], right=[("2","SW2_BB")])

# --- 페라이트 비드 (ADC 분리) ---
add("FB1", "FB", "FerriteBead", "Resistor_SMD:R_0402_1005Metric",
    left=[("1","3V3")], right=[("2","3V3_ADC")])

# --- 저항 ---
for ref, val, na, nb in [
    ("R1","5.1k","CC1","GND"),      ("R2","5.1k","CC2","GND"),
    ("R3","27","RP_DP","USB_DP"),   ("R4","27","RP_DM","USB_DM"),
    ("R5","4.7k","I2C_SDA","3V3"),  ("R6","4.7k","I2C_SCL","3V3"),
    ("R7","100k","BQ_INT","3V3"),   ("R8","100k","EN_3V3","VSYS"),
    ("R9","10k","RUN","3V3"),       ("R10","100k","PWR_BTN","VSYS"),
    ("R11","100k","VBUS_USB","VBUS_SENSE"), ("R12","100k","VBUS_SENSE","GND"),
    ("R13","1k","LED_A","LED_K"),   ("R14","10k","BAT_TS","GND")]:
    add(ref, "R", val, "Resistor_SMD:R_0402_1005Metric",
        left=[("1",na)], right=[("2",nb)])

# --- 커패시터 ---
for ref, val, na, nb in [
    ("C1","1uF","VBUS_USB","GND"), ("C2","1uF","VSYS","GND"), ("C3","1uF","VBAT","GND"),
    ("C4","10uF","VSYS","GND"),    ("C5","22uF","3V3","GND"),
    ("C6","1uF","3V3","GND"),      ("C7","1uF","DVDD","GND"),
    ("C8","15pF","XIN","GND"),     ("C9","15pF","XOUT","GND"),
    ("C10","100nF","3V3","GND"),   ("C11","100nF","3V3","GND"),
    ("C12","100nF","3V3","GND"),   ("C13","100nF","3V3","GND"),
    ("C14","100nF","3V3_ADC","GND")]:
    add(ref, "C", val, "Capacitor_SMD:C_0402_1005Metric",
        left=[("1",na)], right=[("2",nb)])

# --- 스위치 ---
add("SW1", "SW", "PWR_BTN", "Button_Switch_SMD:SW_SPST_PTS645",
    left=[("1","PWR_BTN")], right=[("2","GND")])
add("SW2", "SW", "BOOTSEL", "Button_Switch_SMD:SW_SPST_PTS645",
    left=[("1","QSPI_SS")], right=[("2","GND")])
add("SW3", "SW", "RUN", "Button_Switch_SMD:SW_SPST_PTS645",
    left=[("1","RUN")], right=[("2","GND")])

# --- LED ---
add("D2", "D", "LED", "LED_SMD:LED_0603_1608Metric",
    left=[("A","LED_K")], right=[("K","GND")])

# --- 안테나 패드 ---
add("AE1", "AE", "PCB_Antenna", "RF_Antenna:Texas_2.4GHz_Antenna",
    left=[("1","ANT")])

# ─────────────────────────── 지오메트리 ───────────────────────────
def geom(c):
    nL, nR = len(c["left"]), len(c["right"])
    rows = max(nL, nR, 1)
    span = (rows - 1) * GRID
    BH = span / 2 + GRID
    maxl = max([len(n) for n,_ in c["left"]] or [1])
    maxr = max([len(n) for n,_ in c["right"]] or [1])
    BW = max(7.62, round(((maxl + maxr) * 0.7 + GRID) / GRID) * GRID)
    return nL, nR, rows, BH, BW

def pin_local_y(n, i):
    top = (n - 1) / 2 * GRID
    return top - i * GRID

# ─────────────────────────── 심볼 정의 텍스트 ───────────────────────────
def sym_body(topname, c):
    nL, nR, rows, BH, BW = geom(c)
    s = []
    s.append(f'  (symbol "{topname}"')
    s.append('    (pin_names (offset 1.016))')
    s.append('    (in_bom yes) (on_board yes)')
    s.append(f'    (property "Reference" "{c["prefix"]}" (at 0 {BH+2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
    s.append(f'    (property "Value" "{c["value"]}" (at 0 {-(BH+2.54):.2f} 0) (effects (font (size 1.27 1.27))))')
    s.append(f'    (property "Footprint" "{c["fp"]}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    s.append(f'    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    bare = topname.split(":")[-1]
    s.append(f'    (symbol "{bare}_0_1"')
    s.append(f'      (rectangle (start {-BW:.2f} {BH:.2f}) (end {BW:.2f} {-BH:.2f})')
    s.append('        (stroke (width 0.254) (type default)) (fill (type background)))')
    s.append('    )')
    s.append(f'    (symbol "{bare}_1_1"')
    for i,(name,_) in enumerate(c["left"]):
        y = pin_local_y(nL, i)
        s.append(f'      (pin passive line (at {-(BW+L):.2f} {y:.2f} 0) (length {L})')
        s.append(f'        (name "{name}" (effects (font (size 1.27 1.27))))')
        s.append(f'        (number "{name}" (effects (font (size 1.27 1.27)))))')
    for i,(name,_) in enumerate(c["right"]):
        y = pin_local_y(nR, i)
        s.append(f'      (pin passive line (at {BW+L:.2f} {y:.2f} 180) (length {L})')
        s.append(f'        (name "{name}" (effects (font (size 1.27 1.27))))')
        s.append(f'        (number "{name}" (effects (font (size 1.27 1.27)))))')
    s.append('    )')
    s.append('  )')
    return "\n".join(s)

# ─────────────────────────── 배치 ───────────────────────────
# 컬럼별 x, 세로 커서. 부품 간 넉넉히 띄워 핀좌표 충돌 방지.
columns = {
    "io":    50,    # USB-C, 배터리, 보호
    "chg":   300,   # BQ25180 + 주변
    "buck":  520,   # RT6150 + 주변
    "mcu":   760,   # RP2040
    "mem":  1050,   # 플래시/크리스탈/스위치/디커플
    "rf":   1300,   # CYW43439/안테나/LED
}
layout = {
    "io":   ["J1","J2","U6","D1","R1","R2","R3","R4","R11","R12"],
    "chg":  ["U3","C1","C2","C3","SW1","R10","R14","R7"],
    "buck": ["U4","L1","C4","C5","R8"],
    "mcu":  ["U1"],
    "mem":  ["U2","Y1","C8","C9","SW2","SW3","R9","C6","C7","FB1","C14",
             "C10","C11","C12","C13"],
    "rf":   ["U5","AE1","D2","R13","R5","R6"],
}
byref = {c["ref"]: c for c in comps}
pos = {}
for col, refs in layout.items():
    x = columns[col]
    y = 40.0
    for ref in refs:
        c = byref[ref]
        _,_,_,BH,_ = geom(c)
        y += BH + 6
        pos[ref] = (round(x/GRID)*GRID, round(y/GRID)*GRID)
        y += BH + 18

# ─────────────────────────── 스키매틱 인스턴스 + 라벨 ───────────────────────────
def placed_symbol(c):
    ref = c["ref"]; PX, PY = pos[ref]
    nL, nR, rows, BH, BW = geom(c)
    out = []
    out.append('  (symbol')
    out.append(f'    (lib_id "{NS}:{ref}_{san(c["value"])}")')
    out.append(f'    (at {PX:.2f} {PY:.2f} 0) (unit 1)')
    out.append('    (in_bom yes) (on_board yes) (dnp no)')
    out.append(f'    (uuid "{U()}")')
    out.append(f'    (property "Reference" "{ref}" (at {PX:.2f} {PY-(BH+2.54):.2f} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Value" "{c["value"]}" (at {PX:.2f} {PY+(BH+2.54):.2f} 0) (effects (font (size 1.27 1.27))))')
    out.append(f'    (property "Footprint" "{c["fp"]}" (at {PX:.2f} {PY:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    out.append(f'    (property "Datasheet" "" (at {PX:.2f} {PY:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
    for name,_ in c["left"] + c["right"]:
        out.append(f'    (pin "{name}" (uuid "{U()}"))')
    out.append('    (instances')
    out.append(f'      (project "{NS}"')
    out.append(f'        (path "/{ROOT}" (reference "{ref}") (unit 1))')
    out.append('      )')
    out.append('    )')
    out.append('  )')
    # 글로벌 라벨 / No-Connect
    labels = []
    for i,(name,net) in enumerate(c["left"]):
        gx = PX - (BW + L); gy = PY - pin_local_y(nL, i)
        labels.append(label_or_nc(net, gx, gy, 180))
    for i,(name,net) in enumerate(c["right"]):
        gx = PX + (BW + L); gy = PY - pin_local_y(nR, i)
        labels.append(label_or_nc(net, gx, gy, 0))
    return "\n".join(out) + "\n" + "\n".join(labels)

def san(v):
    return "".join(ch if ch.isalnum() else "_" for ch in v)

def label_or_nc(net, x, y, ang):
    if net is None or net == "None":
        return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{U()}"))'
    return (f'  (global_label "{net}" (shape bidirectional) (at {x:.2f} {y:.2f} {ang})\n'
            f'    (effects (font (size 1.27 1.27)) (justify {"left" if ang==0 else "right"})) (uuid "{U()}")\n'
            f'    (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
            f'  )')

# ─────────────────────────── 파일 출력 ───────────────────────────
# lib_symbols (스키매틱 임베드용; 이름에 ns: 접두)
lib_embed = "\n".join(sym_body(f"{NS}:{c['ref']}_{san(c['value'])}", c) for c in comps)
instances = "\n".join(placed_symbol(c) for c in comps)

sch = f'''(kicad_sch
  (version 20230121)
  (generator "rp2040w_bat_gen")
  (uuid "{ROOT}")
  (paper "A1")
  (title_block
    (title "RP2040W-BAT  (generated starting point)")
    (comment 1 "결선=글로벌라벨(이름기반). ERC/풋프린트/핀번호 검증 후 사용")
    (comment 2 "충전부 IC=BQ25180  벅부스트=RT6150  무선=CYW43439(Pico W 복제)")
  )
  (lib_symbols
{lib_embed}
  )
{instances}
  (sheet_instances
    (path "/" (page "1"))
  )
)
'''

# 외부 심볼 라이브러리 (.kicad_sym; 이름 bare)
lib_only = "\n".join(sym_body(f"{c['ref']}_{san(c['value'])}", c) for c in comps)
ksym = f'''(kicad_symbol_lib
  (version 20230121)
  (generator "rp2040w_bat_gen")
{lib_only}
)
'''

pro = '''{
  "board": {"design_settings": {}},
  "meta": {"filename": "rp2040w-bat.kicad_pro", "version": 1},
  "schematic": {},
  "sheets": [],
  "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []}
}
'''

symtab = f'''(sym_lib_table
  (version 7)
  (lib (name "{NS}")(type "KiCad")(uri "${{KIPRJMOD}}/rp2040w_bat.kicad_sym")(options "")(descr "RP2040W-BAT project symbols"))
)
'''

import os
os.makedirs("kicad", exist_ok=True)
open("kicad/rp2040w-bat.kicad_sch","w",encoding="utf-8").write(sch)
open("kicad/rp2040w_bat.kicad_sym","w",encoding="utf-8").write(ksym)
open("kicad/rp2040w-bat.kicad_pro","w",encoding="utf-8").write(pro)
open("kicad/sym-lib-table","w",encoding="utf-8").write(symtab)
print(f"components: {len(comps)}")
print("wrote kicad/rp2040w-bat.kicad_sch, .kicad_sym, .kicad_pro, sym-lib-table")
