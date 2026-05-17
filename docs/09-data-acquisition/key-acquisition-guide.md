# 미수집 8개 신호 — API 키 발급 상세 절차

> **대상**: A-3, A-4, A-5, A-6, B-1, B-2, B-5, B-6 (총 8개)
> **소요 시간**: 가장 빠른 5개 키 발급 = 약 50분, 가장 느린 1개(관세청) = 1~3일 대기
> **공통 비용**: 모두 무료 또는 $0.10/년 (Anthropic)

---

## 📋 발급 우선순위 (ROI 순)

| 순서 | 키 | 소요 | 신호 추가 | 비용 |
|------|----|----|----------|------|
| 1 | **KOSIS_API_KEY** | 5분 | A-4 (1개) | 무료 |
| 2 | **GCP Service Account** | 15분 | B-2 (1개) | 1TB/월 무료 |
| 3 | **REDDIT_CLIENT_ID/SECRET** | 5분 | B-3 정확도↑ | 무료 |
| 4 | **ANTHROPIC_API_KEY** | 5분 + PDF 코딩 | B-1+B-5+B-6 (3개) | $0.10/년 |
| 5 | **AWS_ACCESS_KEY_ID/SECRET** | 10분 | A-5 (1개, 90일 한계) | 무료 |
| 6 | **KCS_API_KEY** | 1~3일 (승인) | A-3 (1개) | 무료 |
| - | A-6 Polymarket → Metaculus | 코드만 (10분) | A-6 (1개) | 무료 |

→ **총 50분 + 1~3일 대기로 모든 신호 자동화 가능**

---

# 1️⃣ KOSIS_API_KEY (5분, 가장 빠름)

**대상 신호**: A-4 KOSIS 광공업 재고지수
**비용**: 무료 (일 1만건 호출)
**승인**: 즉시

## 단계

### 1.1 회원가입

1. 브라우저: https://kosis.kr/openapi/index/index.jsp
2. 우상단 **[로그인]** 클릭
3. 로그인 페이지에서 **[회원가입]** 클릭
4. 일반회원 → 본인인증 (휴대폰 또는 아이핀)
5. 가입 완료

### 1.2 API 키 신청

1. 다시 https://kosis.kr/openapi 접속 → 로그인
2. 상단 메뉴 **[활용신청]** 클릭
3. **[OpenAPI 활용신청]** 클릭
4. 폼 입력:
   - **활용 사이트/시스템 명**: `Sixsense DRAM 가격 예측`
   - **활용 사이트/시스템 URL**: 본인 GitHub URL 또는 `http://localhost` 입력
   - **활용 목적**: `반도체 가격 예측을 위한 광공업 재고지수 수집`
   - **사용 통계표**: `광공업동향조사 (DT_1F31035)` 검색해서 선택
5. **[신청]** 클릭 → **즉시 승인**

### 1.3 키 확인

1. 마이페이지 → **[OpenAPI 키 관리]**
2. 신청 목록에서 본인 신청 건 → **[인증키]** 컬럼의 값 복사
   - 형식: `M2Y1ZjE2MDg0ZGI0YTdjNzQzMGY5...` (50~60자)

### 1.4 .env에 설정 + 검증

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend

# .env 파일에 추가
echo "KOSIS_API_KEY=여기에_복사한_키_붙여넣기" >> .env

# 로드 후 실행
source .env
.venv/bin/python3 pipelines/auto_collectors.py A-4
```

**성공 출력**:
```
  ✅ A-4   53주  | KOSIS 광공업동향 C26 재고지수 (월간→주간 forward-fill)
```

### 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| 401 Unauthorized | 키 오타 | .env 파일에서 키 앞뒤 공백 제거 |
| KOSIS API 응답 비어있음 | 통계표 ID 변경 | KOSIS 사이트에서 최신 시리즈 ID 확인 후 `auto_collectors.py` 의 `tblId` 수정 |
| 일일 호출 한도 초과 | 1만건 초과 | 다음날 재시도 또는 활용 변경 신청 |

---

# 2️⃣ GCP Service Account (BigQuery — 15분)

**대상 신호**: B-2 GDELT BigQuery
**비용**: 1TB/월 무료 (쿼리 50MB × 200회/월 가능)
**필수**: 결제카드 등록 (free tier 12개월)

## 단계

### 2.1 GCP 계정 생성

1. 브라우저: https://console.cloud.google.com
2. Google 계정으로 로그인 (또는 신규 가입)
3. 약관 동의 → **[무료로 시작하기]** 클릭
4. **결제카드 등록** (신용카드/체크카드, 인증용 $1 결제 후 환불)
5. **$300 무료 크레딧 90일** 제공 안내 → 동의

### 2.2 새 프로젝트 생성

1. 좌상단 **[프로젝트 선택]** 드롭다운 클릭
2. **[새 프로젝트]** 클릭
3. 프로젝트 이름: `sixsense-dram`
4. 위치: 조직 없음
5. **[만들기]** → 약 30초 대기

### 2.3 BigQuery API 활성화

1. 좌측 메뉴 → **[API 및 서비스]** → **[라이브러리]**
2. 검색창: `BigQuery API`
3. **[BigQuery API]** 클릭 → **[사용 설정]** 클릭

### 2.4 Service Account 생성

1. 좌측 메뉴 → **[IAM 및 관리자]** → **[서비스 계정]**
2. **[+ 서비스 계정 만들기]** 클릭
3. 서비스 계정 이름: `sixsense-bq-reader`
4. 설명: `BigQuery 읽기 전용 for Sixsense`
5. **[만들고 계속]** 클릭
6. **역할 선택** (2개 추가 — 두 번 반복):
   - **BigQuery 데이터 뷰어** (BigQuery Data Viewer)
   - **BigQuery 작업 사용자** (BigQuery Job User)
7. **[계속]** → **[완료]**

### 2.5 JSON 키 다운로드

1. 서비스 계정 목록 → 방금 만든 계정 클릭
2. 상단 탭 **[키]** 클릭
3. **[키 추가]** → **[새 키 만들기]**
4. **JSON** 선택 → **[만들기]**
5. JSON 파일이 자동으로 다운로드됨 (예: `sixsense-dram-12345-abc.json`)

### 2.6 키 파일 안전 보관

```bash
# 다운로드한 JSON을 안전한 위치로 이동
mkdir -p ~/.config/gcp
mv ~/Downloads/sixsense-dram-*.json ~/.config/gcp/sixsense-bq.json
chmod 600 ~/.config/gcp/sixsense-bq.json
```

### 2.7 패키지 설치 + .env 설정 + 검증

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend

# 패키지 설치
.venv/bin/pip install google-cloud-bigquery

# .env에 추가
echo "GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcp/sixsense-bq.json" >> .env

# 로드 후 실행
source .env
.venv/bin/python3 pipelines/auto_collectors.py B-2
```

**성공 출력**:
```
  ✅ B-2   53주  | GDELT BigQuery events_partitioned (TWN actor + TECH theme)
```

### 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| `google.api_core.exceptions.PermissionDenied: 403` | 역할 부족 | IAM에서 BigQuery Job User 추가 |
| `File not found` | 경로 오타 | `ls $GOOGLE_APPLICATION_CREDENTIALS`로 확인 |
| Billing not enabled | 결제카드 미등록 | 결제 설정 → 카드 추가 |

---

# 3️⃣ REDDIT_CLIENT_ID/SECRET (5분, B-3 정확도 향상)

**대상 신호**: B-3 Reddit (현재 HN 대체로 작동 중, Reddit 정식 추가 시 더 정확)
**비용**: 무료 (분당 60회)

## 단계

### 3.1 Reddit 앱 등록

1. https://www.reddit.com 가입/로그인
2. 우상단 프로필 → **[설정]** → 좌측 **[보안 및 개인정보]**
3. 또는 직접: https://www.reddit.com/prefs/apps
4. 페이지 하단 **[create another app...]** 클릭

### 3.2 앱 정보 입력

| 필드 | 값 |
|------|----|
| **name** | `Sixsense` |
| **type** | ⚪ **script** 선택 (개인용) |
| **description** | `반도체 가격 예측 연구` |
| **about url** | (비워두기) |
| **redirect uri** | `http://localhost:8080` |

→ **[create app]** 클릭

### 3.3 client ID + secret 복사

생성된 앱 카드에서:
- **client ID**: 앱 이름 바로 아래 14자 문자열 (예: `AbCdEf12345678`)
- **secret**: "secret" 단어 옆에 표시 (예: `XyZ-abc123-def456...`)

### 3.4 .env 설정 + 검증

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend

.venv/bin/pip install praw

cat >> .env <<EOF
REDDIT_CLIENT_ID=AbCdEf12345678
REDDIT_CLIENT_SECRET=XyZ-abc123-def456...
EOF

source .env
.venv/bin/python3 pipelines/auto_collectors.py B-3
```

**성공 출력**:
```
  ✅ B-3   53주  | Reddit PRAW (r/hardware + buildapc + memorymarket, 'memory price')
```

### 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| `401 unauthorized` | secret 복사 시 끝 글자 누락 | secret 전체 다시 복사 (마우스 더블클릭) |
| `403 forbidden` | user_agent 누락 | `auto_collectors.py`의 `user_agent='Sixsense Research v1.0'` 유지 |
| 결과 0건 | subreddit 활동 적음 | 키워드 변경 (예: 'DRAM' → 'memory') |

---

# 4️⃣ ANTHROPIC_API_KEY (5분, B-1/B-5/B-6 — 3개 한번에)

**대상 신호**: B-1 Earnings 감성, B-5 LTA 비율, B-6 HBM 비중 (1개 키로 3개 신호)
**비용**: 종량제 (claude-haiku 사용 시 $1/M input + $5/M output)
**예상 사용량**: 12회 PDF 분석 × 8K tokens = $0.10/년

## 단계

### 4.1 계정 생성

1. https://console.anthropic.com 접속
2. **[Sign up]** → 이메일 + 비밀번호 또는 Google 로그인
3. 이메일 인증 완료
4. 가입 후 자동으로 콘솔 진입

### 4.2 결제 정보 등록 (필수)

1. 좌측 메뉴 → **[Billing]**
2. **[Add Payment Method]** 클릭
3. 카드 정보 입력 → 등록 완료
4. 초기 크레딧 자동 충전 (보통 $5)

### 4.3 API 키 생성

1. 좌측 메뉴 → **[API Keys]**
2. **[+ Create Key]** 클릭
3. 키 이름: `Sixsense Production`
4. **[Create Key]** → 키 표시됨 (한 번만!)
5. **즉시 복사** (예: `sk-ant-api03-...`)

> ⚠️ 키는 화면을 닫으면 다시 볼 수 없음. 반드시 복사 후 안전한 곳에 저장.

### 4.4 .env 설정 + 기본 동작 검증

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend

echo "ANTHROPIC_API_KEY=sk-ant-api03-여기에_복사한_키" >> .env

source .env

# 키 검증 (간단 호출)
curl -s -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 50,
    "messages": [{"role":"user","content":"Hello, just verify API works. Respond OK."}]
  }' | python3 -m json.tool | head -10
```

**성공 출력**:
```json
{
    "content": [{"text": "OK"}],
    "model": "claude-haiku-4-5-20251001",
    ...
}
```

### 4.5 B-1/B-5/B-6 PDF 파이프라인 구현 (추가 코드 작업)

B-1/B-5/B-6는 PDF 다운로드 + 텍스트 추출 + Claude 호출 흐름이 필요. `auto_collectors.py`의 `collect_B1_earnings_sentiment()` 함수를 채워야 함:

```python
# auto_collectors.py 의 해당 함수 본문을 다음으로 교체:
import pypdf
from io import BytesIO

def _samsung_ir_pdfs():
    """Samsung IR PDF URL — 분기별 발표 자료."""
    # 패턴: https://images.samsung.com/is/content/samsung/p5/global/ir/docs/{Q}_qrf.pdf
    return [
        ("Samsung", "2025-04", "https://images.samsung.com/.../2025Q1_qrf.pdf"),
        ("Samsung", "2025-07", "https://images.samsung.com/.../2025Q2_qrf.pdf"),
        # ... 분기별
    ]

def collect_B1_earnings_sentiment():
    _ = need_env("ANTHROPIC_API_KEY", "...")
    quarterly = []
    for company, ym, url in _samsung_ir_pdfs():
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            pdf = pypdf.PdfReader(BytesIO(r.content))
            text = "\n".join(p.extract_text() for p in pdf.pages[:10])
            score = _claude_sentiment(text, f"{company} {ym} 메모리 가격 전망 (-1~+1)")
            q_date = date(int(ym[:4]), int(ym[5:]), 1)
            quarterly.append((q_date, score))
        except Exception as e:
            print(f"  ⚠️ {company} {ym}: {e}")
    if not quarterly:
        raise RuntimeError("IR PDF 분석 결과 비어있음")
    data = monthly_to_weekly(quarterly)
    return data, "real", f"Samsung/SK/Micron IR PDF + Claude haiku ({len(quarterly)} obs)"
```

```bash
.venv/bin/pip install pypdf
.venv/bin/python3 pipelines/auto_collectors.py B-1
```

> **현실적 권장**: B-1 PDF URL은 분기마다 변경됨 (samsung.com 사이트 구조). 직접 IR 페이지 방문해서 PDF URL 수동 확인이 가장 안정적.

### 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| `401 invalid_api_key` | 키 오타 또는 만료 | console에서 새 키 생성 |
| `429 rate_limit_exceeded` | 분당 호출 한도 | sleep 1초 추가 |
| `insufficient_quota` | 크레딧 소진 | Billing에서 충전 |
| PDF 404 | URL 패턴 변경 | Samsung IR 사이트 직접 방문해서 최신 URL 확인 |

---

# 5️⃣ AWS_ACCESS_KEY_ID/SECRET (10분, A-5 — 한계 있음)

**대상 신호**: A-5 AWS EC2 Spot Price
**비용**: 무료 (read-only)
**한계**: AWS Spot 가격 history는 **최대 90일**만 제공 → 1년 백필 불가

## 단계

### 5.1 AWS 계정 생성

1. https://aws.amazon.com 접속 → 우상단 **[AWS 콘솔에 로그인]** → **[새 AWS 계정 생성]**
2. 이메일 + 계정 이름: `sixsense-research`
3. 결제카드 등록 (free tier 12개월 자동 적용)
4. 본인 확인 (휴대폰 SMS 인증)
5. 가입 완료 → AWS Management Console 접속

### 5.2 IAM 사용자 생성

1. 콘솔 상단 검색창 → **IAM** 검색 → IAM 클릭
2. 좌측 메뉴 → **[Users]** → **[Create user]**
3. User name: `sixsense-readonly`
4. ☑ **Provide user access to the AWS Management Console** (비활성 가능, CLI만)
5. **[Next]** 클릭

### 5.3 권한 부여

1. **Set permissions** 화면:
   - ⚪ **Attach policies directly** 선택
   - 검색: `AmazonEC2ReadOnlyAccess` → ☑ 체크
2. **[Next]** → **[Create user]**

### 5.4 Access Key 생성

1. 사용자 목록 → 방금 만든 `sixsense-readonly` 클릭
2. 상단 탭 **[Security credentials]** 클릭
3. **Access keys** 섹션 → **[Create access key]**
4. **Use case**: `Command Line Interface (CLI)` 선택
5. ☑ 권장사항 확인 → **[Next]**
6. Description: `Sixsense local research` → **[Create access key]**
7. 표시 화면:
   - **Access key**: `AKIAIOSFODNN7EXAMPLE`
   - **Secret access key**: `wJalrXUtnFEMI/K7MDENG/...`
   - **[Download .csv]** 또는 즉시 복사

> ⚠️ Secret은 한 번만 표시. 반드시 즉시 복사.

### 5.5 .env 설정 + 검증

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend

.venv/bin/pip install boto3

cat >> .env <<EOF
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
EOF

source .env
.venv/bin/python3 pipelines/auto_collectors.py A-5
```

**성공 출력 (90일치만)**:
```
  ✅ A-5   13주  | AWS EC2 m6i.xlarge spot (us-east-1a, 최대 90일)
```

### 1년 백필 불가 — 대안

AWS는 spot history를 90일만 제공 → 1년치 일괄 수집 불가.

**해결**: 주간 cron으로 매주 90일치 받아서 누적 → 1년 차에 누적 데이터 확보:

```bash
# crontab -e
0 6 * * 2 cd /path/to/backend && .venv/bin/python3 pipelines/auto_collectors.py A-5
```

매주 화요일 06:00 자동 갱신 → 누적된 history를 별도 파일에 보존.

### 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| `UnauthorizedOperation` | EC2 권한 부족 | AmazonEC2ReadOnlyAccess 정책 재확인 |
| `InvalidClientTokenId` | Key ID 오타 | .env 다시 확인 |
| 결과 0건 | 인스턴스 타입 미존재 | `auto_collectors.py`에서 `m6i.xlarge` → 다른 타입 시도 |

---

# 6️⃣ KCS_API_KEY (1~3일 승인 대기)

**대상 신호**: A-3 관세청 메모리 IC 수출
**비용**: 무료 (일 1만건)
**대기**: 신청 후 1~3 영업일 승인

## 단계

### 6.1 회원가입

1. https://unipass.customs.go.kr/ets/index.do 접속
2. 우상단 **[회원가입]** → 일반회원
3. **실명 인증 필수** (휴대폰 또는 아이핀)
4. 약관 동의 → 정보 입력 → 가입 완료

### 6.2 OpenAPI 활용 신청

1. 로그인 후 상단 메뉴 **[정보공개]** → **[OpenAPI]**
2. 또는 직접: https://unipass.customs.go.kr/ets/index.do?menuId=ETS_MNU_00000122
3. **[활용신청]** 버튼 클릭
4. 폼 입력:
   - **신청기관/사용자명**: 본인 이름
   - **활용 시스템명**: `Sixsense DRAM 가격 예측 시스템`
   - **활용 목적**: `반도체 메모리(HS 854231) 월별 수출 데이터 수집을 통한 가격 예측 연구 (KAIST CAIO 졸업 프로젝트)`
   - **API 종류**: ☑ **수출입실적 조회** (FxchOcl 등 관련 항목 모두)
   - **연락처/이메일** 정확히 입력
5. **[신청]** 클릭

### 6.3 승인 대기 (1~3 영업일)

- 평일 신청 시 보통 1~2일
- 주말/공휴일 신청 시 다음 영업일부터 계산
- 승인 시 이메일 통보

### 6.4 키 확인

승인 후:
1. 로그인 → **마이페이지** → **[OpenAPI 발급내역]**
2. 신청 건의 **[인증키]** 컬럼 값 복사
   - 형식: 영문+숫자 30~40자

### 6.5 .env 설정 + 검증

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend

echo "KCS_API_KEY=발급받은_키" >> .env

source .env
.venv/bin/python3 pipelines/auto_collectors.py A-3
```

**성공 출력**:
```
  ✅ A-3   53주  | 관세청 무역통계 API HS 854231 월간 수출액 (USD)
```

### 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| 1주일 넘게 승인 안 됨 | 활용 목적 부족 | 마이페이지에서 신청 수정 → 더 구체적으로 |
| 응답 없음 | HS 코드 오타 | `854231` 6자리 정확히 확인 |
| 한글 깨짐 | charset | requests에 `r.encoding = 'utf-8'` 추가 |

---

# 7️⃣ A-6 Polymarket → Metaculus 대체 (키 불필요, 10분 코드 수정)

**대상 신호**: A-6 대만 봉쇄확률
**비용**: 무료 (Metaculus API 공개)
**필요한 것**: Metaculus question ID 1개

## 단계

### 7.1 적합한 Metaculus 질문 찾기

1. https://www.metaculus.com 접속
2. 검색창: `Taiwan invasion`
3. 결과 중 가장 활발한 질문 선택. 예시:
   - "Will China invade Taiwan before 2027?" → URL: `https://www.metaculus.com/questions/15356/`
   - "Will there be a military blockade of Taiwan in 2026?" → URL: `https://www.metaculus.com/questions/...`
4. URL 끝의 숫자 ID 복사 (예: `15356`)

### 7.2 auto_collectors.py 수정

```python
# auto_collectors.py 의 collect_A6_polymarket() 함수를 다음으로 교체:

def collect_A6_metaculus():
    """Metaculus 대만 침공/봉쇄 확률."""
    METACULUS_QID = "15356"  # ← 본인이 찾은 question ID로 교체
    url = f"https://www.metaculus.com/api2/questions/{METACULUS_QID}/"
    r = requests.get(url, timeout=30, headers={"User-Agent": "Sixsense Research"})
    r.raise_for_status()
    j = r.json()
    history = j.get("community_prediction", {}).get("history", [])
    if not history:
        # 대안: prediction_timeseries
        history = j.get("prediction_timeseries", [])
    weekly = defaultdict(list)
    for pt in history:
        try:
            t = datetime.fromtimestamp(pt.get("t") or pt.get("timestamp")).date()
            if not (START_D <= t <= END_D):
                continue
            wk = snap_to_monday(t).isoformat()
            val = pt.get("x") or pt.get("community_prediction") or pt.get("median")
            if val is not None:
                weekly[wk].append(float(val))
        except (KeyError, ValueError, TypeError):
            continue
    data = [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(weekly.items())]
    if not data:
        raise RuntimeError(f"Metaculus #{METACULUS_QID} history 비어있음")
    return data, "real", f"Metaculus question #{METACULUS_QID} community prediction"


# COLLECTORS 딕셔너리에서 교체:
COLLECTORS["A-6"] = collect_A6_metaculus
```

### 7.3 실행

```bash
.venv/bin/python3 pipelines/auto_collectors.py A-6
```

**성공 출력**:
```
  ✅ A-6   42주  | Metaculus question #15356 community prediction
```

(주수가 53보다 적을 수 있음 — Metaculus는 질문 등록 이후부터만 history 제공)

---

# 📋 종합 체크리스트 (50분 + 1~3일)

복사해서 사용:

```
□ 1. KOSIS (5분)
   □ kosis.kr/openapi 회원가입
   □ 활용신청 → 즉시 승인
   □ 인증키 복사 → .env에 KOSIS_API_KEY
   □ 검증: python3 pipelines/auto_collectors.py A-4

□ 2. GCP BigQuery (15분)
   □ console.cloud.google.com 가입 + 결제카드
   □ 프로젝트 생성 → BigQuery API 활성화
   □ Service Account 생성 → BigQuery Data Viewer + Job User
   □ JSON 키 다운로드 → ~/.config/gcp/sixsense-bq.json
   □ pip install google-cloud-bigquery
   □ .env에 GOOGLE_APPLICATION_CREDENTIALS
   □ 검증: python3 pipelines/auto_collectors.py B-2

□ 3. Reddit (5분)
   □ reddit.com/prefs/apps에서 script 앱 생성
   □ client ID + secret 복사 → .env
   □ pip install praw
   □ 검증: python3 pipelines/auto_collectors.py B-3

□ 4. Anthropic Claude (5분)
   □ console.anthropic.com 가입 + 결제카드
   □ API Keys → Create Key → 복사
   □ .env에 ANTHROPIC_API_KEY
   □ curl로 검증 (위 §4.4)
   □ (선택) PDF 파이프라인 구현 → B-1/B-5/B-6

□ 5. AWS (10분, A-5는 90일 한계)
   □ aws.amazon.com 계정 + 결제카드
   □ IAM 사용자 → AmazonEC2ReadOnlyAccess
   □ Access key 생성 → 즉시 복사
   □ pip install boto3
   □ .env에 AWS_ACCESS_KEY_ID + SECRET
   □ 검증: python3 pipelines/auto_collectors.py A-5

□ 6. 관세청 (1~3일 대기)
   □ unipass.customs.go.kr/ets 회원가입 (실명 인증)
   □ OpenAPI 활용신청 → 1~3일 승인 대기
   □ 마이페이지에서 인증키 복사 → .env
   □ 검증: python3 pipelines/auto_collectors.py A-3

□ 7. A-6 Metaculus (10분 코드 수정)
   □ metaculus.com에서 question ID 찾기
   □ auto_collectors.py 의 collect_A6_metaculus 함수 추가
   □ COLLECTORS["A-6"] = collect_A6_metaculus 교체
   □ 검증: python3 pipelines/auto_collectors.py A-6
```

---

# 🚀 모든 키 발급 후 일괄 실행

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend

# 모든 .env 키 로드
source .env

# 11개 신호 자동 수집 일괄
.venv/bin/python3 pipelines/auto_collectors.py --all

# Prophet 재학습 + 예측
.venv/bin/python3 pipelines/forecast.py

# 결과 확인
cat data/forecast/forecast_summary.txt
```

**예상 출력** (모든 키 발급 후):
```
  ✅ A-3   53주  | 관세청 무역통계
  ✅ A-4   53주  | KOSIS 광공업동향
  ✅ A-5   13주  | AWS EC2 m6i.xlarge spot (90일)
  ✅ A-6   42주  | Metaculus question
  ⏸ B-1   설정 필요 (PDF 파이프라인 구현 후 동작)
  ✅ B-2   53주  | GDELT BigQuery
  ✅ B-3   53주  | Reddit PRAW
  ✅ B-4   53주  | Caldara GPR
  ⏸ B-5   설정 필요 (B-1과 동일)
  ⏸ B-6   설정 필요 (B-1과 동일)
  ✅ B-7   53주  | Hacker News
```

→ 11개 중 8개 자동 수집 완료, B-1/B-5/B-6은 추가 코드 작업 후 동작.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | 8개 미수집 신호 API 키 발급 상세 절차 + 검증 명령어 |
