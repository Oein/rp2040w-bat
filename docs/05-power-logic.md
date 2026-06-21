# 05. 전원 로직 — 켜짐/꺼짐/ship/슬립

> 요구사항: **유선=켜짐 / 버튼 3초=켜짐 / 소프트웨어 종료(배터리 차단)** + 무입력 슬립/키 웨이크.
> 핵심은 BQ25180의 **ship 모드(배터리 초저전류 차단)** 와 **웨이크 경로**.

## 1. 상태 정의

| 상태 | 배터리 소모 | 설명 | 진입 | 탈출 |
|---|---|---|---|---|
| **OFF (ship)** | nA~µA | BQ25180가 BAT→SYS 완전 차단. 보드 무전원 | I2C ship 명령(소프트 종료) | ① USB 연결 ② 버튼 3초 |
| **ON (active)** | mA급 | 정상 동작(무선/유선) | 위 탈출 트리거 | — |
| **SLEEP (dormant)** | µA~수백µA | RP2040 dormant, 3V3 유지(ship 아님). 키 입력 대기 | 무입력 타이머 | 매트릭스 GPIO 인터럽트 |

> **OFF vs SLEEP 구분**: OFF는 BQ25180가 전원을 끊음(콜드). SLEEP은 전원 살아있고 RP2040만 저전력.
> 장기 미사용=OFF(ship)로 배터리 보존, 잠깐 미사용=SLEEP로 즉시 복귀.

## 2. 켜짐 경로

### 2.1 유선 = 켜짐 (자동)
```
USB-C 연결 → VBUS 5V → BQ25180 VIN 인가
   → BQ25180 ship 자동 해제 → SYS 출력(파워패스)
   → RT6150 3V3 → RP2040 부팅
   → 펌웨어: WL_GPIO2(또는 ADC 분압)로 "유선" 감지 → USB-HID 모드
```
- 부품/별도 로직 없이 **IC 동작만으로** 충족. USB 꽂으면 무조건 켜짐.

### 2.2 버튼 3초 = 켜짐 (콜드스타트 래치)
```
OFF(ship) 상태에서 전원버튼 누름
   → BQ25180 푸시버튼 입력 감지(길게 누름 ≥ wake 시간)
   → 콜드스타트: BAT→SYS 연결 래치 → 3V3 → RP2040 부팅
   → 펌웨어가 부팅 후 "전원 ON" 상태로 진입, 버튼 핸들러 등록
```
- "3초 유지" 검증은 ① BQ25180 자체 wake 타이머 + ② **펌웨어가 부팅 직후 버튼이 계속 눌려있는지 재확인**(원치 않는 기동 방지)으로 이중화.
  - 펌웨어: 부팅 후 버튼 GPIO를 읽어 3초 미만이면 다시 ship 진입(오작동 방지).

> ⚠️ BQ25180의 정확한 **버튼/CE/wake 동작과 타이밍**은 데이터시트로 확정. 칩이 버튼 길게-누름 wake를 직접 지원하지 않으면, 버튼을 **CE/wake 핀 + RC**로 구성하거나 별도 래치(예 부하스위치+버튼)로 보강.

## 3. 꺼짐 경로

### 3.1 소프트웨어 종료 → ship 모드 (배터리 차단)
```
펌웨어 "전원 끄기" 명령(키 조합/명령)
   → 저장/정리(설정 flush, 무선 disconnect)
   → I2C로 BQ25180 ship 모드 레지스터 세트
   → BQ25180: BAT→SYS 차단 → 보드 전원 OFF(nA~µA)
```
- 이후 BAT 소모 거의 0 → 장기 보관 가능.
- **단, USB 연결 중엔 ship 들어가도 VIN이 SYS를 다시 살림**(유선=켜짐 규칙 우선). USB 빼야 완전 OFF.

### 3.2 하드 컷(선택)
- 비상시 **3V3_EN(37핀)** 을 GND로 → RT6150 OFF → 3V3 차단. (배터리 자체 차단은 아님 → 평상시엔 ship 사용)

## 4. 슬립 / 웨이크 (배터리 유지)

```
무입력 N초 → 펌웨어: 무선 저전력 + RP2040 dormant 진입
   → 매트릭스 "웨이크 라인" 1개를 인터럽트로 설정
   → 아무 키 → GPIO 엣지 → dormant 해제 → 복귀(수 ms)
```
- 웨이크용 매트릭스 라인 1개 확보(docs/06). 슬립 중 행/열을 웨이크 가능 상태로 구성.
- BLE 연결 유지가 필요하면 무선칩은 저전력 연결 유지 모드, RP2040만 dormant.

## 5. 펌웨어 의사코드

```c
void on_boot() {
    init_clocks_flash();
    bq25180_init_i2c();
    if (vbus_present())            // WL_GPIO2 또는 ADC 분압
        mode = WIRED;
    else {
        if (!button_held_for(3000))  // 콜드스타트 오작동 방지 재확인
            bq25180_enter_ship();    // 다시 끔
        mode = WIRELESS;
    }
    hid_init(mode);
}

void on_power_off_command() {       // 소프트웨어 종료
    settings_flush();
    wireless_disconnect();
    bq25180_enter_ship();           // BAT→SYS 차단
    // USB 연결 중이면 VIN이 SYS 유지 → 사실상 재부팅 대기
}

void idle_loop() {
    if (idle_ms > SLEEP_TIMEOUT) {
        configure_wake_on_matrix();
        rp2040_dormant();           // 키 입력 시 복귀
    }
}
```

## 6. 진리표

| USB | ship 레지스터 | 결과 |
|---|---|---|
| 연결 | 무관 | **ON**(VIN→SYS). 충전 동시 진행 |
| 분리 | clear | ON (BAT→SYS) |
| 분리 | set(ship) | **OFF**(BAT 차단). 버튼3초/USB로만 기동 |

> 정확한 레지스터 비트·버튼 타이밍은 BQ25180 데이터시트로 확정.
