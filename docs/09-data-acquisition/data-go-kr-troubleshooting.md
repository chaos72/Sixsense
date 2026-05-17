# data.go.kr 관세청 API 401 Unauthorized 해결

> **현재 상황**: KCS_API_KEY 등록됨 (64자 hex), `getItemtradeList` 엔드포인트 존재 확인. 하지만 401.
> **원인**: data.go.kr 인증키가 **Itemtrade 서비스에 대한 권한 미부여**.

---

## 확인 단계 (사용자 액션, 5분)

### 1. data.go.kr 마이페이지 접속

1. https://www.data.go.kr 로그인
2. 우상단 본인 이름 → **[마이페이지]**
3. 좌측 메뉴 → **[오픈 API]** → **[활용신청 현황]**

### 2. Itemtrade 서비스 신청 상태 확인

**케이스 A — 신청 안 됨**:
- "관세청_무역통계서비스" 또는 "Itemtrade" 검색 → 활용신청
- 활용 목적 입력 → 신청
- **자동승인** 또는 **1~2시간 대기**

**케이스 B — 신청은 했으나 "심사중"**:
- 보통 1~2시간 → 자동 승인
- 새 API는 즉시 활성 (24시간 내)

**케이스 C — "승인" 상태**:
- 이미 사용 가능해야 함
- 마이페이지 → **[일반인증키]** 두 종류 확인:
  - **Encoding** (URL 인코딩됨, `%` 포함 가능)
  - **Decoding** (원본 hex 문자열)
- 사용자가 준 키 `e277...` 는 **decoding** 키로 보임
- → **encoding 키** 시도해보거나, encoding 키도 .env에 추가

### 3. 정확한 활용 신청 서비스 확인

data.go.kr → 관세청 → 무역통계 관련 서비스가 여러 개 있음:
- 관세청 수출입실적
- **관세청 무역통계서비스 (Itemtrade)** ← 우리가 쓰는 것
- 관세청 통합공고
- 관세청 환율정보

신청한 서비스가 정확히 "**Itemtrade**" 인지 확인 (서비스 ID `1220000`).

---

## 키 활성화 후 즉시 실행

활성화 확인되면 같은 명령 재실행:
```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend
.venv/bin/python3 pipelines/auto_collectors.py A-3
```

성공 시 출력:
```
✅ A-3   53주  | 관세청 data.go.kr Itemtrade HS 854231 월간 수출 (12개월)
```

---

## 디버그용 raw 호출 (필요 시)

```bash
KEY="e277a94de194583ff1f36af125f6053b3c5c5c7d91b8b6a88d5f306770352394"
curl -v "https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList?serviceKey=${KEY}&strtYymm=202505&endYymm=202505&hsSgn=854231"
```

응답 해석:
- **401 Unauthorized**: 활성화 대기 또는 권한 없음 → 위 1~3단계 확인
- **200 + items 비어있음**: HS 코드 조회 결과 없음 → hsSgn 값 변경
- **403 Forbidden**: 일일 호출 한도 초과
- **500 Server Error**: data.go.kr 측 일시 장애

---

## 대안 — encoding 키 시도

`.env`의 KCS_API_KEY를 encoding 버전으로 교체:
```bash
# 마이페이지에서 encoding 키 복사 (URL-safe Base64 같은 형식)
sed -i.bak 's/^KCS_API_KEY=.*/KCS_API_KEY=<encoding_키_여기에>/' /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/.env
rm /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/.env.bak
.venv/bin/python3 pipelines/auto_collectors.py A-3
```

---

## 코드는 준비됨 — 키만 활성화되면 동작

`backend/pipelines/auto_collectors.py` 의 `collect_A3_kcs()` 함수는 data.go.kr Itemtrade 사양에 맞게 작성됨:
- 월별 호출 12회 (2025-05 ~ 2026-04)
- JSON 우선 → XML fallback
- 결과를 주간으로 forward-fill
- 401 에러 시 명확한 안내 메시지

활성화 후 단일 명령으로 53주 데이터 수집 완료.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | data.go.kr 401 진단 + 활성화 절차 |
