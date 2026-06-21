# 전체 결선표 (Netlist) — net 단위

> EasyEDA/KiCad에서 **이 표대로 배선(또는 네트라벨)** 하면 회로가 완성된다.
> 부품 지정자는 `hardware/bom.csv`와 일치. **IC 핀번호는 데이터시트로 확정** 후 배선(여기선 핀 *기능명* 사용).

## 범례
- `→` 연결, `∥` 병렬, `[val]` 부품값. **net**은 같은 이름끼리 모두 연결됨.

---

## 1. 전원 레일 (net)
| net | 의미 |
|---|---|
| **VBUS_USB** | USB-C 5V 입력 (= BQ25180 VIN) |
| **VSYS** | 파워패스 출력 (= BQ25180 SYS = Pico 39핀 = 벅부스트 VIN) |
| **3V3** | 시스템 3.3V (벅부스트 VOUT = Pico 36핀) |
| **VBAT** | 1셀 리포 단자 (= BQ25180 BAT) |
| **GND** | 공통 그라운드 |
| **AGND** | 아날로그 그라운드 (단일점에서 GND 결합) |

---

## 2. USB-C 커넥터 (J1)
| 핀(기능) | net / 연결 |
|---|---|
| VBUS ×4 (A4,A9,B4,B9) | **VBUS_USB** |
| GND ×4 (A1,A12,B1,B12) + 쉴드 | GND |
| CC1 (A5) | R_CC1 [5.1k] → GND |
| CC2 (B5) | R_CC2 [5.1k] → GND |
| D+ (A6∥B6) | **USB_DP** |
| D- (A7∥B7) | **USB_DM** |
| SBU1/SBU2 (A8/B8) | NC |

보호:
- VBUS_USB → TVS D_TVS [SMF5.0A] → GND
- USB_DP/USB_DM → ESD U_ESD [USBLC6-2SC6] → GND
- VBUS_USB → C_VIN [1µF] → GND

데이터 직렬저항:
- USB_DP → R_DP [27Ω] → RP2040 USB_DP
- USB_DM → R_DM [27Ω] → RP2040 USB_DM

---

## 3. 충전 IC BQ25180 (U3)  ※ 볼/핀맵 데이터시트 확정
| 기능 | net / 연결 |
|---|---|
| IN | **VBUS_USB** (+ C_VIN 1µF) |
| SYS | **VSYS** (+ C_SYS 1µF) |
| BAT | **VBAT** (+ C_BAT 1µF) |
| GND / 열패드 | GND |
| SDA | **I2C_SDA** (→ RP2040 GPIO20) + R [4.7k]→3V3 |
| SCL | **I2C_SCL** (→ RP2040 GPIO21) + R [4.7k]→3V3 |
| /INT | **BQ_INT** (→ RP2040 GPIO22) + R [100k]→3V3 |
| CE/버튼 | **PWR_BTN** (§7) |
| TS | NTC [10k]→GND (미사용 시 데이터시트 고정전압 분압) |
| ILIM/PROG | R_ILIM (충전전류, 셀 용량 확정 후) 또는 I2C 설정 |

---

## 4. 배터리 커넥터 (J2, JST PH 2핀)
| 핀 | net |
|---|---|
| + | **VBAT** |
| - | GND |

---

## 5. 벅부스트 RT6150 (U4)  ※ 핀맵 데이터시트 확정
| 기능 | net / 연결 |
|---|---|
| VIN | **VSYS** (+ C [10µF]→GND) |
| VOUT | **3V3** (+ C [22µF]→GND) |
| SW / L | 인덕터 L1 [2.2µH] |
| EN | **EN_3V3** ← 3V3_EN(37핀), R [100k]→VSYS (기본 ON) |
| PS (파워세이브) | **WL_GPIO1** (CYW43439) 또는 RP2040 GPIO23 |
| GND | GND |

---

## 6. RP2040 (U1)  ※ QFN-56 핀번호 RP2040 데이터시트/Pico W 회로도 대조
### 6.1 전원
| 레일 | 연결 | 디커플 |
|---|---|---|
| IOVDD ×N | 3V3 | 각 100nF |
| USB_VDD | 3V3 | 100nF |
| ADC_AVDD | 3V3 (페라이트비드 FB1) | 100nF (+선택 RC) → AGND |
| VREG_VIN | 3V3 | 1µF |
| VREG_VOUT (DVDD 코어1.1V) | 내부LDO 출력 → DVDD | 1µF + 100nF |
| GND/열패드 | GND | |

### 6.2 크리스탈 (Y1 12MHz)
| RP2040 | 연결 |
|---|---|
| XIN | Y1 → C_L1 [≈15pF] → GND |
| XOUT | Y1 → C_L2 [≈15pF] → GND |

### 6.3 QSPI 플래시 (U2 W25Q128)
| RP2040 | U2 |
|---|---|
| QSPI_SS_n | /CS |
| QSPI_SCLK | CLK |
| QSPI_SD0 | DI/IO0 |
| QSPI_SD1 | DO/IO1 |
| QSPI_SD2 | /WP/IO2 |
| QSPI_SD3 | /HOLD/IO3 |
| 3V3 | VCC (+100nF) |
| GND | GND |

### 6.4 USB
| RP2040 | 연결 |
|---|---|
| USB_DP | R_DP[27Ω] → USB_DP(J1) |
| USB_DM | R_DM[27Ω] → USB_DM(J1) |

### 6.5 부팅/리셋/디버그
| 신호 | 연결 |
|---|---|
| QSPI_SS_n | SW_BOOT 버튼 → GND (BOOTSEL) |
| RUN | 30핀, R[10k]→3V3, SW_RUN→GND, C[100nF]→GND |
| SWDIO/SWCLK/GND | 디버그 패드 |

### 6.6 무선 SPI (Pico W 동일)
| 신호 | RP2040 | CYW43439(U5) |
|---|---|---|
| WL_CLK | GPIO29 | SPI_CLK |
| WL_CS | GPIO25 | SPI_CS_n |
| WL_DAT | GPIO24 | SPI_D (양방향) / IRQ |
| WL_REG_ON | GPIO23 | REG_ON (풀다운) |

### 6.7 외부 40핀 GPIO (docs/01 매핑)
GPIO0~22, 26~28 → 캐슬레이션 핀. (매트릭스/주변 배정은 docs/06)

---

## 7. 전원 버튼 (SW_PWR)
| 연결 |
|---|
| BQ25180 CE/버튼 핀 ↔ SW_PWR ↔ GND, 풀업 R[100k]→VSYS, (선택)C[100nF] 디바운스 |
| 동작: 길게(≥3s) 누름 → wake. 정확한 핀/타이밍 데이터시트 확정 |
| 펌웨어가 동일 버튼 상태를 보조 GPIO로도 읽어 3초 검증 가능(선택 배선) |

---

## 8. CYW43439 (U5) + 안테나  ※ Pico W 회로도/거버 복제
| 신호 | 연결 |
|---|---|
| VBAT/VDDIO | 3V3 (+100nF∥1µF) |
| SPI | §6.6 |
| WL_GPIO0 | 상태 LED |
| WL_GPIO1 | 벅부스트 PS |
| WL_GPIO2 | VBUS 감지 |
| RF_OUT | π매칭 → PCB 안테나 (키프아웃) |

---

## 9. VBUS 감지 보조(선택)
| 연결 |
|---|
| VBUS_USB → R[100k] → SENSE노드 → R[100k] → GND |
| SENSE노드 → RP2040 미사용 ADC(GPIO26~28 중 1) |

---

## 10. net 요약(주요)
`VBUS_USB, VSYS, 3V3, VBAT, GND, AGND, USB_DP, USB_DM, I2C_SDA, I2C_SCL, BQ_INT, PWR_BTN, EN_3V3, WL_CLK, WL_CS, WL_DAT, WL_REG_ON, QSPI_SS_n, QSPI_SCLK, QSPI_SD0..3, GPIO0..22/26..28`
