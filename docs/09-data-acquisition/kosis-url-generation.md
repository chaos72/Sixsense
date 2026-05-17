# KOSIS API URL 생성 — 사용자 직접 단계

> **상황**: KOSIS_API_KEY는 발급됨 (인증 성공 ✅). 그러나 KOSIS는 통계표마다 `objL1`/`itmId` 분류 코드가 다르고, 사용자 등록 표만 접근 가능 → 사용자가 직접 KOSIS 웹사이트에서 정확한 URL 생성 필요.
>
> **소요 시간**: 5~10분
> **결과물**: collector가 즉시 사용할 수 있는 KOSIS API URL

---

## 📋 우리가 알고 있는 정보

| 항목 | 값 |
|------|-----|
| 우리 API 키 | `MDc...BU=` (.env에 저장됨, 인증 성공) |
| 우리가 원하는 표 | **광업·제조업동향조사** → 생산·출하·**재고** 지수 |
| KOSIS 분류 | L_4 > 101_G131 > DT_1F02XXX 시리즈 |
| 후보 표 ID | `DT_1F02001`, `DT_1F02003`, `DT_1F02011`, `DT_1F02012`, `DT_1F02013` 등 11개 |
| 막힌 부분 | 각 표의 정확한 `objL1` (분류 코드) + `itmId` (항목 코드) |

---

## ✅ 방법 1: KOSIS 사용자정의표 사용 (가장 권장)

### 1.1 KOSIS 통계표 검색 + 조건 설정

1. https://kosis.kr 접속 (이미 가입 + 로그인 된 상태)
2. 상단 검색창: **"전자부품 재고지수"** 입력 → 검색
3. 결과에서 **"광업·제조업동향조사 > 생산, 출하, 재고지수 (2020=100)"** 클릭
   - 또는 직접 URL: https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1F02012
4. 표가 열리면 화면 좌측의 **[항목]/[분류]/[시점]** 선택 패널

### 1.2 원하는 조건 선택

- **항목**: ☑ **재고지수** (다른 것 모두 해제)
- **산업분류**: ☑ **전자부품·컴퓨터·영상·음향 및 통신장비 (C26)** 1개만
- **시점**: 시작=`202505`, 끝=`202604`, 단위=`월간`

→ **[조회]** 클릭하여 데이터가 나오는지 확인

### 1.3 사용자정의표 저장 → 사용자 통계 ID 얻기

1. 표 우상단 **[즐겨찾기 추가]** 또는 **[저장]** 버튼 클릭
2. 또는 **[설정 → 사용자 통계 추가]** 클릭
3. 이름: `Sixsense_재고지수` 등으로 저장
4. 마이페이지 → **나의 사용자정의 통계** → 저장된 항목 확인
5. **URL 또는 사용자 통계 ID** 복사 (예: `xyz123abc...`)

### 1.4 .env에 추가

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend
echo "KOSIS_USER_STATS_ID=복사한_ID" >> .env
source .env

# 즉시 실행
.venv/bin/python3 pipelines/auto_collectors.py A-4
```

---

## ✅ 방법 2: KOSIS OpenAPI URL 생성기 사용 (대안)

### 2.1 URL 생성기 접속

1. KOSIS 로그인
2. 위쪽 **[OpenAPI]** 메뉴 → **[활용가이드]** → **[데이터 추출]** 또는 **[OpenAPI 통계자료]**
3. 또는 직접: https://kosis.kr/openapi/devGuide/devGuide_0202.jsp?menuId=M_0102

### 2.2 표 선택 + 조건 입력

1. 좌측 트리에서 **광업·제조업** → **광업제조업동향조사** → **생산, 출하, 재고**
2. 표 클릭: `DT_1F02012` 등
3. 우측에 자동으로 파라미터 폼 표시:
   - 항목 선택 (재고지수)
   - 분류 선택 (전자부품·컴퓨터…)
   - 시점 입력 (202505 ~ 202604)
4. 하단 **[URL 생성]** 또는 **[조회 URL]** 버튼 클릭
5. 생성된 URL 복사

### 2.3 .env에 추가

```bash
echo 'KOSIS_FULL_URL=https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=...&...' >> .env
source .env
.venv/bin/python3 pipelines/auto_collectors.py A-4
```

> ⚠️ URL에 키가 포함되어 있을 수 있음 — 키 부분을 `apiKey=$KOSIS_API_KEY` 같은 변수로 바꾸거나, 그냥 그대로 사용 (이미 .env 차단됨).

---

## ✅ 방법 3: KOSIS GUI에서 정확한 분류 코드 확인

표를 열어둔 상태에서:

1. 화면 좌측 **[분류]** 트리를 펼치고 마우스 오른쪽 클릭 → **요소 검사** (개발자 도구)
2. 각 분류 항목의 `value` 속성이 `objL1` 값입니다
3. 예시:
   - "전자부품…": `value="13102641"` → objL1 후보
   - "반도체": `value="13102642"` 가능성

이 값을 `.env`에 `KOSIS_OBJL1=13102641` 로 추가하면 collector가 자동 활용. (단, 현재 collector는 ID 우선이므로 추가 코드 수정 필요)

---

## 🔄 작동 확인 후

성공 출력 예시:
```
  ✅ A-4   12주  | KOSIS 광공업동향 C26 재고지수 (월간→주간 forward-fill)
```

그 다음 Prophet 재실행:
```bash
.venv/bin/python3 pipelines/forecast.py
```

→ regressor에 A-4 자동 추가됨, MAPE 변화 측정 가능.

---

## 🆘 막힐 때 — 가장 빠른 해결

KOSIS UI가 너무 복잡하면 **수동 CSV 업로드**로 우회:

1. KOSIS 표 화면 → 우상단 **[다운로드]** → **CSV** 또는 **Excel**
2. 파일 열어서 `week,value` 두 열만 남기고 저장
3. 우리 시스템에 1회 업로드:
   ```bash
   .venv/bin/python3 pipelines/upload_manual.py A-4 data/manual/A-4.csv \
     --source "KOSIS DT_1F02012 재고지수 (수동 다운로드)"
   ```

자동화는 다음 사이클 (월 1회 갱신)에서 다시 시도.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | KOSIS URL 생성 절차 — 키 인증 성공 후 정확한 표 ID 획득 가이드 |
