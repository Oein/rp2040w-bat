# RP2040W-BAT — Pico W 핀호환 무선/유선 키보드 메인보드

> RP2040 + CYW43439 무선 + **단일 USB-C(데이터+충전)** + **1셀 리포 배터리 전원부**를
> 직접 올린 **Raspberry Pi Pico W 핀호환** 커스텀 보드.

이 저장소는 **회로(스키매틱) 설계 산출물**입니다. PCB 아트워크/거버는 포함하지 않으며,
EasyEDA(또는 KiCad)에서 바로 회로를 그릴 수 있도록 아래를 제공합니다.

- 전체 블록별 회로 설계 문서 (`docs/`)
- 네트(net) 단위 결선표 — 그대로 배선 가능 (`hardware/netlist.md`)
- LCSC 부품번호가 들어간 BOM — EasyEDA에서 바로 검색/배치 (`hardware/bom.csv`)
- EasyEDA 임포트용 네이티브 스키매틱 JSON **초안** (`easyeda/`)

---

## 1. 설계 철학 — "검증된 건 복제, 추가분만 새로 설계"

| 블록 | 전략 | 근거 |
|---|---|---|
| RP2040 코어 (플래시·크리스탈·전원·USB) | **Pico W 레퍼런스 그대로 복제** | 부팅/USB 타이밍 검증됨 |
| 무선 (CYW43439 + 안테나) | **Pico W 레이아웃 통째 복제** (또는 인증 모듈) | RF가 최대 난관 |
| 전원/배터리 (USB-C·충전·파워패스·전원로직) | **신규 설계** (본 보드의 핵심) | Pico W에 없는 기능 |
| 키 매트릭스 | 핀맵 제약 안에서 GPIO 배정 | 외부 노출 핀 호환 유지 |

> ⚠️ **충전부는 반드시 IC로** (BQ25180). 리튬셀 CC/CV·과충전·보호를 직접 설계하면 발화 위험.

---

## 2. 시스템 블록도

```
                 ┌──────────────────── 보드 본체 (Pico W 풋프린트 고정) ────────────────────┐
                 │                                                                          │
  USB-C  ──D±──► │  ┌─────────┐    QSPI   ┌──────────┐                                      │
 (충전+데이터)    │  │ RP2040  │◄────────► │ W25Q128  │   12MHz XTAL                          │
   │             │  │  코어   │           └──────────┘                                      │
   │             │  │         │◄──SPI──► CYW43439 ──RF──► PCB 안테나 (키프아웃)               │
   │             │  └────┬────┘                                                             │
   │             │   3V3 │ ▲                                                                │
   │             │       │ │3V3                                                             │
   │ ┌───────────┴───┐   │ │      ┌──────────────┐                                          │
   └►│ BQ25180       │   │ └──────┤ RT6150 벅부스트│◄── VSYS                                 │
     │ 충전+파워패스  │   │        │  VSYS→3V3     │     ▲                                    │
     │ +ship+버튼+I2C │   │        └──────────────┘     │                                    │
     │           SYS ─┼───┴────────────────────────────┘  (= Pico 39번 VSYS)                │
     │           BAT ─┼──► 1셀 리포 (JST)                                                    │
     └───────────────┘                                                                      │
                 │                                                                          │
                 └──────────────────────────────────────────────────────────────────────────┘
   ◄── 이 방향(USB-C/충전부)으로만 보드가 길어짐. 나머지 3면은 Pico W와 동일 ──►
```

---

## 3. 핵심 전원 로직 (요구사항)

| 동작 | 트리거 | 구현 |
|---|---|---|
| **유선 = 켜짐** | USB-C VBUS 인가 | BQ25180가 VIN 감지 → ship 모드 자동 해제 → SYS 출력 → 보드 기동 |
| **버튼 3초 = 켜짐** | 전원 버튼 길게 | BQ25180 푸시버튼 입력 → 콜드스타트 → SYS 래치 |
| **소프트웨어 종료** | 펌웨어 명령 | RP2040가 I2C로 BQ25180 **ship 모드** 진입 → 배터리 차단(초저전류) |
| **무입력 자동 슬립 / 키 웨이크** | 타이머 / 매트릭스 인터럽트 | RP2040 dormant + GPIO 웨이크 (배터리 유지, ship 아님) |

자세한 시퀀스/레지스터는 [`docs/05-power-logic.md`](docs/05-power-logic.md).

---

## 4. 레이아웃 제약 (중요)

요구사항: **충전 포트 방향으로만 보드가 길어져도 되고, 다른 방향으로는 절대 길어지면 안 됨.**

- Pico W 외곽( **21.0 mm 폭 × 51.0 mm 길이**, 1.0 mm 두께, 0.1" 캐슬레이션 40핀) 유지.
- 40핀 캐슬레이션 좌표·번호를 **비트 단위로 Pico W와 동일**하게.
- **USB-C·BQ25180·배터리 커넥터·인덕터** 등 신규 전원부는 **USB가 있던 짧은 변(상단) 바깥으로만** 확장.
- 좌/우/하단 3면은 폭·핀 위치 그대로 → 기존 Pico W 소켓/캐리어에 드롭인.

상세: [`docs/07-layout-mechanical.md`](docs/07-layout-mechanical.md).

---

## 5. 문서 색인

| 파일 | 내용 |
|---|---|
| [`docs/01-pin-compat.md`](docs/01-pin-compat.md) | 40핀 매핑 (Pico W 1:1), WL_GPIO, VBUS 센스 |
| [`docs/02-core-rp2040.md`](docs/02-core-rp2040.md) | RP2040 코어: 플래시·크리스탈·전원·USB·디버그 |
| [`docs/03-wireless-cyw43439.md`](docs/03-wireless-cyw43439.md) | 무선부: CYW43439 SPI·안테나·복제 전략 |
| [`docs/04-power-battery.md`](docs/04-power-battery.md) | **전원부: USB-C·BQ25180·벅부스트** (본론) |
| [`docs/05-power-logic.md`](docs/05-power-logic.md) | 전원 온/오프/ship/슬립 로직 |
| [`docs/06-keyboard-matrix.md`](docs/06-keyboard-matrix.md) | 키 매트릭스·다이오드·웨이크 |
| [`docs/07-layout-mechanical.md`](docs/07-layout-mechanical.md) | 외곽·확장 방향 제약 |
| [`docs/08-easyeda-manual-build.md`](docs/08-easyeda-manual-build.md) | **EasyEDA Pro 수동 작업 가이드** (배터리/충전부 추가) |
| [`hardware/netlist.md`](hardware/netlist.md) | **전체 결선표 (net 단위)** |
| [`hardware/bom.csv`](hardware/bom.csv) | BOM (LCSC 부품번호) |
| [`kicad/README.md`](kicad/README.md) | **열리는 KiCad 프로젝트** (45부품, 글로벌라벨 결선) |
| [`easyeda/README.md`](easyeda/README.md) | EasyEDA 임포트/작도 방법 |

> **바로 열리는 EDA 파일이 필요하면** → [`kicad/rp2040w-bat.kicad_pro`](kicad/) (KiCad 7/8/9).
> 자가검증(문법·오연결0·핀↔라벨일치) 통과. 단, 풋프린트·복잡IC 핀번호·RF는 여신 뒤 확인 필요.

---

## 6. EasyEDA로 옮기는 법 (요약)

가장 신뢰성 높은 경로(권장):
1. EasyEDA Standard/Pro에서 새 프로젝트 → 새 스키매틱.
2. `hardware/bom.csv`의 LCSC 부품번호로 **부품 검색 → 배치** (EasyEDA의 LCSC 라이브러리 그대로).
3. `hardware/netlist.md`의 net 결선표대로 **배선/네트라벨** 연결.
4. ERC 실행 → 핀맵을 `docs/01-pin-compat.md`와 1:1 대조.

추가로 `easyeda/power-section.schematic.json` (전원부 **시각 초안**, 임포트 가능)을 제공합니다.
네이티브 손작성 JSON은 심볼/핀 렌더가 깨질 수 있어, **BOM+netlist가 정본**입니다.

---

## ⚠️ 검증 주의 (반드시 데이터시트 대조)

이 산출물은 **회로 설계안**이며, 아래는 제작 전 **데이터시트로 핀번호/패키지 확정**이 필요합니다.

- BQ25180 정확한 볼/핀 맵, ship/wake 레지스터·핀 동작
- RP2040 QFN-56 전원 핀 그룹 디커플링 (Pico W 회로도 대조)
- USB-C 16핀 리셉터클 핀 번호 (선정 부품 데이터시트)
- CYW43439 RF 매칭·안테나 — **반드시 Pico W 거버 복제**, 직접 그리지 말 것
