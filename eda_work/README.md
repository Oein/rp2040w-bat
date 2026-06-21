# EasyEDA Pro 프로젝트 편집 (.eprj2)

업로드된 EasyEDA Pro 프로젝트 **`Alta.eprj2`** 에 **`RP2040W-BAT`** 보드를 추가합니다.

> `.eprj2` = SQLite DB. 스키매틱/PCB 내용은 `documents.dataStr` 에 **gzip+base64** 로 들어있고,
> 디코드하면 `["DOCTYPE","SCH",...]` 형태의 JSON-레코드 텍스트입니다.

## 결과물
`build_board.py` 실행 → **`RP2040W-BAT.eprj2`** 생성.

- 기존 Alta 4개 보드(alpha-rev2/3, alpha-rev3-cheaper, CH32V307-rev1)는 **그대로 보존**.
- **5번째 보드 `RP2040W-BAT`** 추가:
  - 스키매틱 = 검증된 RP2040 스키매틱(RP2040 C2040 / USB-C TYPE-C-31-M-12 / W25Q128 / 12MHz / USBLC6 ESD, 131개 부품) 재사용 + 보드명 변경.
  - 배터리/충전부 설계 노트(전력흐름·LCSC 부품번호·넷 결선·전원로직)를 **네이티브 TEXT 블록**으로 삽입.
  - 빈 PCB 문서 1개.

## 재생성
```bash
python3 build_board.py     # /root/.../Alta.eprj2 -> eda_work/RP2040W-BAT.eprj2
```

## 검증(스크립트가 자동 수행)
- ✅ `PRAGMA integrity_check = ok`, `foreign_key_check` 비어있음
- ✅ 새 시트/PCB `dataStr` gzip+base64 **디코드 라운드트립** 성공
- ✅ `projects.boards` JSON의 모든 sch/pcb 참조가 실제 행으로 **해소됨**(5보드)
- ✅ `project_structures` JSON 유효, 원본 4보드 보존 확인

## ⚠️ 직접 EasyEDA Pro에서 확인/완성할 것
EasyEDA를 띄워 렌더 검증은 못 하므로(블라인드 편집), 아래는 여신 뒤 처리:

1. **충전 IC 배치(권장 워크플로)**: EasyEDA Pro에서 **LCSC 검색 → 1클릭 배치**.
   - `BQ25180` → **C2682744** / `RT6150B` → **C2830944** / `JST PH 2P` → **C173752**
   - (오프라인에서 풋프린트를 자작하면 렌더/패드가 깨질 위험이 커서, 검증된 LCSC 부품 배치가 정석입니다.)
2. 노트 블록의 넷 결선대로 **배선/네트플래그** 연결 (상세 `../hardware/netlist.md`).
3. ERC → 핀맵 대조(`../docs/01-pin-compat.md`).
4. PCB는 비어 있음 → 부품 가져오기 후 레이아웃(`../docs/07-layout-mechanical.md`: 확장은 USB측으로만).

## 안전장치
- **원본 업로드 파일은 절대 수정하지 않음**(읽기 전용으로 복사해 작업).
- 대용량/타프로젝트 바이너리(`*.eprj2`)는 git에 커밋하지 않음(.gitignore). 산출물은 별도 전달.
