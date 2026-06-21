# EasyEDA 산출물

> 사용자 선택: **BOM+netlist(정본) + 네이티브 JSON(편의 초안) 둘 다.**

## 정본(권장) — LCSC BOM + 결선표

EasyEDA의 실제 작업 흐름과 1:1로 맞습니다. 가장 신뢰성 높음.

1. EasyEDA Standard 또는 Pro → 새 프로젝트 → 새 스키매틱.
2. `../hardware/bom.csv`의 **LCSC 부품번호**로 부품 검색 → 배치
   (EasyEDA 좌측 라이브러리 검색창에 `C2040` 등 입력 → "Place").
3. `../hardware/netlist.md`의 net 결선표대로 **배선 또는 네트라벨(Net Label)** 연결.
   - 같은 net 이름을 쓰면 멀어도 연결됨 → 전원/I2C 등은 네트라벨이 편함.
4. **ERC** 실행 → `../docs/01-pin-compat.md`로 40핀 매핑 최종 대조.
5. PCB 변환 후 `../docs/07-layout-mechanical.md`의 외곽/확장 제약 적용.

> ⚠️ IC 핀번호(BQ25180/RT6150/CYW43439)는 EasyEDA가 가져오는 **LCSC 심볼의 실제 핀**으로
> 배선하세요. `netlist.md`는 *기능명* 기준이므로 심볼 핀이름과 대조 필요.

## 편의 초안 — 네이티브 스키매틱 JSON

`power-section.schematic.json` : **전원부 블록 시각 초안.**
EasyEDA Standard에서 `파일 → 열기 → EasyEDA`로 임포트할 수 있는 형식입니다.

- 손으로 만든 JSON이라 **심볼/핀 렌더가 일부 깨질 수 있고, 기능 핀·넷 연결은 없습니다**
  (블록·라벨·연결선 위주의 *그림 초안*).
- **회로의 정본은 BOM+netlist**입니다. 이 JSON은 배치 감 잡기용.

### 재생성
```bash
python3 generate_schematic.py
```
`generate_schematic.py`를 고쳐 블록/라벨/위치를 바꿀 수 있습니다.

## 왜 네이티브 풀 스키매틱을 자동생성하지 않았나
EasyEDA 네이티브 포맷은 부품마다 **정확한 라이브러리 심볼·핀 좌표·gge ID**가 필요해,
손으로 쓰면 임포트 시 렌더가 깨지기 쉽습니다. 그래서 **검증된 LCSC 심볼을 EasyEDA에서
직접 배치**하는 BOM+netlist 경로를 정본으로 제공합니다.
