# 01. 핀호환 제약 — 외부 40핀을 Pico W와 1:1

> **최우선 규칙**: 외부에서 보이는 40핀의 **위치·번호·기능을 Pico W와 비트 단위로 동일**하게.
> 하나라도 바뀌면 GPIO 26개/핀맵 호환이 깨지고 드롭인 교체가 불가능.

## 1. 40핀 매핑 (Raspberry Pi Pico / Pico W 동일 배열)

좌측(1~20, 위→아래), 우측(21~40, 아래→위). USB 커넥터가 상단(1·40번 쪽).

| 핀 | 이름 | 본 보드 연결 | 핀 | 이름 | 본 보드 연결 |
|---:|---|---|---:|---|---|
| 1 | GP0 | RP2040 GPIO0 | 40 | VBUS | **주의: 직결 금지** (아래 §3) |
| 2 | GP1 | GPIO1 | 39 | VSYS | **BQ25180 SYS 출력** |
| 3 | GND | GND | 38 | GND | GND |
| 4 | GP2 | GPIO2 | 37 | 3V3_EN | 벅부스트 EN (풀업→VSYS) |
| 5 | GP3 | GPIO3 | 36 | 3V3(OUT) | 3V3 레일 |
| 6 | GP4 | GPIO4 | 35 | ADC_VREF | ADC 기준 (필터) |
| 7 | GP5 | GPIO5 | 34 | GP28/ADC2 | GPIO28 |
| 8 | GND | GND | 33 | GND/AGND | 아날로그 GND |
| 9 | GP6 | GPIO6 | 32 | GP27/ADC1 | GPIO27 |
| 10 | GP7 | GPIO7 | 31 | GP26/ADC0 | GPIO26 |
| 11 | GP8 | GPIO8 | 30 | RUN | RP2040 RUN (리셋) |
| 12 | GP9 | GPIO9 | 29 | GP22 | GPIO22 |
| 13 | GND | GND | 28 | GND | GND |
| 14 | GP10 | GPIO10 | 27 | GP21 | GPIO21 |
| 15 | GP11 | GPIO11 | 26 | GP20 | GPIO20 |
| 16 | GP12 | GPIO12 | 25 | GP19 | GPIO19 |
| 17 | GP13 | GPIO13 | 24 | GP18 | GPIO18 |
| 18 | GND | GND | 23 | GND | GND |
| 19 | GP14 | GPIO14 | 22 | GP17 | GPIO17 |
| 20 | GP15 | GPIO15 | 21 | GP16 | GPIO16 |

> GPIO0~22, 26~28만 외부 노출(26개). GPIO23/24/25/29는 Pico W에서 **무선칩 전용으로 재배치**됨(아래).

## 2. WL_GPIO / 무선칩 전용 신호 (Pico W 고유)

Pico W는 일반 Pico에서 GPIO23/24/25/29가 하던 일을 **CYW43439로 옮겼다.** 호환을 위해 그대로 복제:

| 신호 | Pico(비-W) | **Pico W (본 보드 따름)** | 설명 |
|---|---|---|---|
| 온보드 LED | GPIO25 | **WL_GPIO0** | CYW43439 GPIO0 |
| 벅부스트 PS(파워세이브) 제어 | GPIO23 | **WL_GPIO1** | SMPS 모드 제어 |
| VBUS 감지 | GPIO24 | **WL_GPIO2** | USB 연결 감지 (§3) |
| (예약) | GPIO29/ADC3 | CYW43 SPI와 공유 | RP2040 GPIO29 = WL SPI 데이터 겸용 |

- WL_GPIO0~3은 **펌웨어에서 무선칩 드라이버 통해 접근** → 외부 40핀에는 안 나옴. 회로상 CYW43439 쪽에 그대로 둠.
- **임의 변경 금지.** 바꾸면 LED/VBUS감지/SMPS제어 동작과 SDK 호환이 깨짐.

## 3. VBUS / VSYS 연결 규칙 (역류 방지 — 매우 중요)

본 보드는 충전 IC가 들어가므로 **표준 Pico와 결선이 다르다.** 핀 "위치/번호"는 같게, "내부 연결"만 안전하게:

- **40번 VBUS 핀**: Pico에서는 USB 5V 직결. 본 보드는 USB-C VBUS를 **BQ25180 VIN으로** 보냄.
  - 40번 핀은 BQ25180 VIN과 같은 노드(USB 5V)에 연결해도 되나, **VSYS(39)로 역류시키지 말 것.** 파워패스는 IC 내부에서만.
  - 권장: 40번 핀 = USB 5V 표시용(선택). 내부적으로는 USB-C VBUS → BQ25180 VIN 경로가 본선.
- **39번 VSYS 핀**: **BQ25180 SYS(파워패스 출력)** 에 연결. 여기서 벅부스트가 3V3 생성.
  - 외부에서 39번에 전원을 넣어도(예: 캐리어 보드) SYS 노드로 들어가 정상 동작.
- **USB 연결 감지**: Pico W 방식대로 **WL_GPIO2** 사용(펌웨어). 보조로 USB 5V → 100k/100k 분압 → 여분 ADC(GPIO26~28 중 미사용)도 가능(§docs/04).

> ⚠️ 외부 USB-C와 (남아 있다면) 다른 USB **동시 연결 금지.** 본 보드는 USB-C 단일.
