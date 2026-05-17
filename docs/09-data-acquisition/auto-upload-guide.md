# Sixsense 11개 미수집 신호 — 자동 업로드 가이드

> **목적**: 수동 CSV 작성 대신 코드로 자동 수집/적재.
> **도구**: `backend/pipelines/auto_collectors.py` — 신호별 함수 자동 호출
> **자격증명**: 신호별 무료 API 키 (대부분 즉시~3일 발급)
>
> **단일 명령 사용법**:
> ```bash
> cd backend
> .venv/bin/python3 pipelines/auto_collectors.py B-4        # 단일
> .venv/bin/python3 pipelines/auto_collectors.py --all      # 전체 11개 일괄
> ```

---

## 📊 신호별 자동화 상태 (검증 완료)

| 신호 | 키 필요 | 즉시 동작 | 수집 결과 (검증) |
|------|--------|----------|---------------|
| **B-4** GPR Index | ❌ 없음 | ✅ | **53주 자동 수집 성공** (Caldara CSV 자동 다운로드) |
| **B-7** BOM 신호 | ❌ 없음 | ✅ | **53주 자동 수집 성공** (HN API) |
| **B-3** Reddit/HN | ⚠️ Reddit 키 권장 | ✅ HN 대체 | **53주 자동 수집 성공** (HN 대체 사용) |
| **A-6** Polymarket | ❌ 없음 | ⚠️ | 시장은 찾음, history 비어있음 (시장 ID 수동 큐레이션 필요) |
| **A-4** KOSIS | KOSIS_API_KEY | ⏸ | 키 발급 즉시 가능, 발급 후 즉시 작동 |
| **A-3** 관세청 | KCS_API_KEY | ⏸ | 키 발급 1~3일 |
| **A-5** AWS Spot | AWS IAM | ⏸ | 계정+IAM 설정 후 작동 (최대 90일 history) |
| **B-2** GDELT | GCP 서비스 계정 | ⏸ | BigQuery 설정 후 작동 (1TB/월 무료) |
| **B-1** Earnings 감성 | ANTHROPIC_API_KEY | ⏸ + 추가 코드 | 스켈레톤 완성, PDF 파이프라인 구현 필요 |
| **B-5** LTA 비율 | ANTHROPIC_API_KEY | ⏸ + 추가 코드 | B-1 파이프라인 재사용 |
| **B-6** HBM 비중 | ANTHROPIC_API_KEY | ⏸ + 추가 코드 | B-1 파이프라인 재사용 |

→ **즉시 동작 가능**: 3개 (B-4, B-7, B-3)
→ **키만 발급하면**: 4개 (A-3, A-4, A-5, B-2)
→ **키 + 추가 구현**: 3개 (B-1, B-5, B-6 — PDF 파이프라인 필요)
→ **수동 큐레이션**: 1개 (A-6)

---

## 0. 사전 준비

```bash
cd backend

# 1. 환경변수 템플릿 복사
cp .env.example .env

# 2. .env 편집 (사용할 키만 채우면 됨)
nano .env   # 또는 vim, code 등

# 3. 환경변수 로드 (또는 export로 개별 설정)
source .env

# 4. 추가 Python 패키지 설치 (사용할 collector에 따라)
.venv/bin/pip install boto3                       # A-5용
.venv/bin/pip install google-cloud-bigquery       # B-2용
.venv/bin/pip install praw                        # B-3용 (HN 대체로도 가능)
.venv/bin/pip install pypdf                       # B-1/5/6용
```

`.env.example` 파일에 모든 키 발급 URL + 단계가 명시되어 있습니다.

---

## 1. ✅ B-4 지정학 리스크 (GPR Index) — 키 불필요, 즉시 동작

**소스**: Caldara & Iacoviello GPR Index (학술, 무료, 1985년부터 매월 갱신)

**자동화 동작 검증됨**:
```bash
.venv/bin/python3 pipelines/auto_collectors.py B-4
```

**출력**:
```
  ✅ B-4    53주  | Caldara & Iacoviello GPR Index (https://...)
```

**구현 위치**: [auto_collectors.py L57-110](backend/pipelines/auto_collectors.py)
- xls/csv 후보 URL 순차 시도
- pandas + xlrd로 자동 파싱
- 월간 데이터 → 주간 forward-fill

**의존성**:
```bash
.venv/bin/pip install xlrd openpyxl     # 이미 설치되어 있을 가능성 높음
```

---

## 2. ✅ B-7 BOM 신호 (HN Algolia) — 키 불필요, 즉시 동작

**소스**: Hacker News Algolia Search API (무료, 무제한)

**자동화 동작 검증됨**:
```bash
.venv/bin/python3 pipelines/auto_collectors.py B-7
```

**출력**:
```
  ✅ B-7    53주  | Hacker News Algolia API (queries: 4건)
```

**구현 로직**:
- 검색 쿼리: "HBM memory", "DRAM price", "NVIDIA H100", "Apple silicon memory"
- 각 검색의 weekly 게시물 점수 합산
- 주간 정규화

**커스터마이징**: `auto_collectors.py` 의 `collect_B7_bom_hn()` 내 `queries` 리스트 수정.

---

## 3. ✅ B-3 Reddit (HN 대체로 즉시 동작, Reddit는 권장 사항)

### 옵션 A: 즉시 동작 (HN 대체)
```bash
.venv/bin/python3 pipelines/auto_collectors.py B-3
# REDDIT_CLIENT_ID 미설정 → 자동으로 HN 'memory chip price' 대체
```

### 옵션 B: Reddit PRAW 사용 (정확도 향상)

**키 발급 (5분, 무료)**:
1. https://www.reddit.com/prefs/apps 접속
2. 하단 "create another app" 클릭
3. Type: **script**, Name: `Sixsense`, redirect uri: `http://localhost:8080`
4. "Create app" 클릭
5. 앱 카드 좌상단 14자 문자열 = client ID
6. "secret" 옆 값 = client secret

**`.env`에 추가**:
```bash
REDDIT_CLIENT_ID=AbCdEfGhIjKlMn
REDDIT_CLIENT_SECRET=AbCdEfGhIjKlMnOpQrStUvWxYz12345
```

**설치 + 실행**:
```bash
.venv/bin/pip install praw
source .env
.venv/bin/python3 pipelines/auto_collectors.py B-3
# → ✅ B-3   53주  | Reddit PRAW (r/hardware + buildapc + memorymarket ...)
```

---

## 4. ⚠️ A-6 Polymarket (시장 ID 수동 큐레이션 필요)

**현재 상태**: API 호출은 성공하지만 적합한 Taiwan market의 history가 비어있음 (대부분 inactive 또는 daily-resolution 시장).

**해결안 (2가지)**:

### 옵션 A: Metaculus 대체 (권장)

`auto_collectors.py` 에 다음 함수 추가:
```python
def collect_A6_metaculus():
    """Metaculus #15356 Taiwan-China invasion 확률."""
    qid = "15356"  # 또는 사용자가 찾은 question ID
    url = f"https://www.metaculus.com/api2/questions/{qid}/"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    j = r.json()
    history = j.get("community_prediction", {}).get("history", [])
    weekly = defaultdict(list)
    for pt in history:
        try:
            t = datetime.fromtimestamp(pt["t"]).date()
            if not (START_D <= t <= END_D):
                continue
            wk = snap_to_monday(t).isoformat()
            weekly[wk].append(pt["x"])  # community median
        except (KeyError, ValueError):
            continue
    data = [{"week": w, "value": round(sum(v) / len(v), 4)} for w, v in sorted(weekly.items())]
    return data, "real", f"Metaculus question #{qid} community prediction"
```

→ `COLLECTORS["A-6"] = collect_A6_metaculus` 로 교체.

### 옵션 B: Polymarket 시장 ID 찾기

1. https://polymarket.com 접속
2. 검색: "Taiwan"
3. 적합 시장 찾으면 URL 끝의 ID 복사
4. `auto_collectors.py` 의 `collect_A6_polymarket()` 에 ID hardcode

---

## 5. ⏸ A-4 KOSIS (키 발급 즉시 — 가장 빠른 추가)

**키 발급 (즉시, 5분)**:
1. https://kosis.kr/openapi/index/index.jsp 접속
2. 우상단 "회원가입" → 일반 회원 가입
3. 로그인 → "활용신청" → "OpenAPI 활용신청"
4. 활용목적 입력 (예: "반도체 가격 예측 연구") → 즉시 키 발급
5. 마이페이지 → "인증키" 복사

**`.env`에 추가**:
```bash
KOSIS_API_KEY=YOUR_KOSIS_KEY_HERE
```

**실행**:
```bash
source .env
.venv/bin/python3 pipelines/auto_collectors.py A-4
```

**구현 위치**: [auto_collectors.py L256-292](backend/pipelines/auto_collectors.py)
- 시리즈 `DT_1F31035` (광공업동향 — 전자부품 재고지수)
- 월간 데이터 → 주간 forward-fill

---

## 6. ⏸ A-3 관세청 (키 발급 1~3일)

**키 발급 (1~3 영업일, 무료)**:
1. https://unipass.customs.go.kr/ets/index.do 접속
2. 회원가입 (실명 인증 필요)
3. 로그인 → 마이페이지 → "OpenAPI 이용신청"
4. 사용 목적 입력 → 신청 → 승인 대기 1~3일
5. 승인 후 마이페이지 → 인증키 복사

**`.env`에 추가**:
```bash
KCS_API_KEY=YOUR_CUSTOMS_KEY
```

**실행**:
```bash
source .env
.venv/bin/python3 pipelines/auto_collectors.py A-3
```

**구현**: HS 코드 854231 (메모리 IC) 월별 수출액 자동 수집. 12개월 분 호출 → 주간 forward-fill.

---

## 7. ⏸ A-5 AWS EC2 Spot Price

**키 발급 (10분)**:
1. https://console.aws.amazon.com 가입 (결제카드 필수, free tier 12개월)
2. IAM 콘솔 → Users → Add user → name `sixsense-readonly`
3. Attach policy: **AmazonEC2ReadOnlyAccess**
4. Security credentials → "Create access key" → Use case: CLI
5. Access key ID + Secret access key 복사

**`.env`에 추가**:
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

**설치 + 실행**:
```bash
.venv/bin/pip install boto3
source .env
.venv/bin/python3 pipelines/auto_collectors.py A-5
```

**한계**: AWS는 spot price history를 **최대 90일**만 제공 → 1년 백필 불가, 향후 90일만 누적 가능.

**대안**: 주간 cron으로 매주 90일치 받아서 누적 → 1년 차에 누적 데이터 확보.

---

## 8. ⏸ B-2 GDELT BigQuery

**설정 (15분)**:

### 8.1 GCP 프로젝트 + BigQuery 활성화
1. https://console.cloud.google.com 가입 (Google 계정 + 결제카드 필수)
2. 새 프로젝트 생성 (이름: `sixsense`)
3. "BigQuery API" 활성화 (검색 → Enable)

### 8.2 Service Account 키 생성
1. IAM & Admin → Service Accounts → Create
2. Name: `sixsense-bigquery`
3. Role: **BigQuery Data Viewer** + **BigQuery Job User**
4. Done → 생성된 SA 클릭 → Keys → Add key → Create new → **JSON**
5. JSON 파일 자동 다운로드 → 안전한 위치로 이동 (예: `~/.config/gcp-sixsense.json`)

**`.env`에 추가**:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/Users/you/.config/gcp-sixsense.json
```

**설치 + 실행**:
```bash
.venv/bin/pip install google-cloud-bigquery
source .env
.venv/bin/python3 pipelines/auto_collectors.py B-2
```

**비용**: 1TB/월 무료. GDELT events_partitioned 테이블 쿼리 1회 ≈ 50MB. 월 200회 가능.

---

## 9. ⏸ B-1 / B-5 / B-6 — Claude API + IR PDF 자동화 (추가 구현 필요)

**현재**: 스켈레톤 완성, ANTHROPIC_API_KEY 검증 동작.

### 9.1 Claude API 키 발급 (즉시, 5분)
1. https://console.anthropic.com 가입
2. Settings → Billing → 결제카드 등록
3. API Keys → "Create Key" → 복사

**`.env`에 추가**:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**비용**: claude-haiku-4-5 사용 시 $1/M input tokens, $5/M output. 분기당 3사 × 4분기 = 12회 호출, 회당 ~8K input + 32 output → 약 $0.10 / 1년 전체

### 9.2 추가 구현 필요 (B-1)

`auto_collectors.py`의 `collect_B1_earnings_sentiment()` 함수 확장:

```python
import pypdf
from io import BytesIO

def _fetch_ir_pdfs():
    """Samsung/SK/Micron IR 분기 PDF URL 수집."""
    pdfs = []
    # Samsung — IR 페이지에서 PDF 링크 스크래핑
    for ym in ["2025-04", "2025-07", "2025-10", "2026-01"]:
        url_pattern = f"https://images.samsung.com/is/content/samsung/p5/global/ir/docs/{ym}_qrf.pdf"
        pdfs.append(("Samsung", ym, url_pattern))
    # SK Hynix 마찬가지...
    # Micron 마찬가지...
    return pdfs

def collect_B1_earnings_sentiment():
    _ = need_env("ANTHROPIC_API_KEY", "...")
    quarterly_scores = []
    for company, ym, url in _fetch_ir_pdfs():
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            continue
        pdf = pypdf.PdfReader(BytesIO(r.content))
        text = "\n".join(p.extract_text() for p in pdf.pages[:10])  # 첫 10페이지
        score = _claude_sentiment(text, f"{company} {ym} 메모리 가격 전망")
        quarter_date = date(int(ym[:4]), int(ym[5:]), 1)
        quarterly_scores.append((quarter_date, score, company))
    # 3사 평균 → 분기 1점수 → 13주 forward-fill
    by_quarter = defaultdict(list)
    for d, s, _ in quarterly_scores:
        by_quarter[d].append(s)
    monthly = [(d, sum(v)/len(v)) for d, v in sorted(by_quarter.items())]
    data = monthly_to_weekly(monthly)
    return data, "real", f"Samsung/SK/Micron 분기 IR PDF → Claude haiku sentiment ({len(quarterly_scores)} obs)"
```

### 9.3 B-5 LTA, B-6 HBM 동일 패턴

- B-1과 동일 PDF 파이프라인 재사용
- `_claude_sentiment()` 호출 시 prompt 변경:
  - B-5: "메모리 장기 계약(LTA) 비율 (0~1 사이 숫자)"
  - B-6: "HBM 매출 비중 (0~1 사이 숫자)"

---

## 🔁 일괄 실행 + Prophet 재학습

모든 환경변수 설정 후:

```bash
cd backend
source .env

# 11개 모두 시도
.venv/bin/python3 pipelines/auto_collectors.py --all

# 결과: 키 있는 신호 ✅, 없는 신호 ⏸
# 예시:
#   ✅ A-3    52주  | 관세청 무역통계 API HS 854231
#   ✅ A-4    53주  | KOSIS 광공업동향 C26
#   ⏸  A-5   설정 필요 | 환경변수 AWS_ACCESS_KEY_ID 미설정
#   ⏸  A-6   실패     | Polymarket history 비어있음
#   ✅ B-2    53주  | GDELT BigQuery
#   ✅ B-3    53주  | Reddit PRAW
#   ✅ B-4    53주  | Caldara GPR Index
#   ✅ B-7    53주  | Hacker News Algolia
#   ...

# Prophet 재학습 (새 신호 자동 인식)
.venv/bin/python3 pipelines/forecast.py
```

forecast.py는 `data/historical/` 폴더의 모든 `*.json`을 자동으로 인식하여 regressor로 사용할 수 있습니다.

---

## 📋 우선순위 권장 (자동화 ROI 순)

| 우선순위 | 신호 | 소요 시간 | 비용 | ROI |
|---------|------|----------|------|-----|
| 🥇 1 | **B-4** GPR | 0분 (이미 작동) | 무료 | ⭐⭐⭐⭐⭐ |
| 🥇 1 | **B-7** BOM | 0분 (이미 작동) | 무료 | ⭐⭐⭐⭐ |
| 🥇 1 | **B-3** HN 대체 | 0분 (이미 작동) | 무료 | ⭐⭐⭐ |
| 🥈 2 | **A-4** KOSIS | 5분 (가입+키) | 무료 | ⭐⭐⭐⭐⭐ |
| 🥈 2 | **B-3** Reddit | 5분 (앱 등록) | 무료 | ⭐⭐⭐⭐ |
| 🥉 3 | **B-2** GDELT BigQuery | 15분 (GCP 설정) | $0 (1TB free) | ⭐⭐⭐⭐ |
| 🥉 3 | **A-3** 관세청 | 1~3일 (승인 대기) | 무료 | ⭐⭐⭐⭐ |
| 4 | **B-1/5/6** Claude IR | 1시간 (코드 확장) | $0.10/년 | ⭐⭐⭐ |
| 5 | **A-5** AWS Spot | 10분 (IAM) | 무료 | ⭐⭐ (90일 한계) |
| 후순위 | **A-6** Polymarket | 1시간 (시장 큐레이션) | 무료 | ⭐ |

---

## 🎯 최단 경로: 5분이면 신호 3개 추가

```bash
cd backend
# 키 불필요 3개를 즉시 자동 수집
.venv/bin/python3 pipelines/auto_collectors.py B-4
.venv/bin/python3 pipelines/auto_collectors.py B-7
.venv/bin/python3 pipelines/auto_collectors.py B-3
# Prophet 재학습으로 신호 추가 효과 확인
.venv/bin/python3 pipelines/forecast.py
```

→ 기존 9개 → **12개 신호로 학습 가능**, MAPE 개선 효과 즉시 측정.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | 11개 신호 자동 수집 가이드 + 검증 결과 |
