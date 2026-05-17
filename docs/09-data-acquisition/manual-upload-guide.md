# Sixsense 미수집 11개 신호 — 수동 1회 업로드 가이드

> **목적**: 자동 수집 실패한 11개 신호를 사용자가 직접 무료 출처에서 받아 1회 업로드.
> **도구**: `backend/pipelines/upload_manual.py` (CSV → historical/<id>.json 변환)
> **템플릿**: `backend/data/manual/<id>.csv` (53주 빈 행 사전 생성됨)

---

## 0. 업로드 흐름 (모든 신호 공통)

```
1. 출처 사이트 접속 → 데이터 다운로드 (Excel/CSV)
2. backend/data/manual/<신호ID>.csv 파일 열기
3. value 열에 주별 값 채우기 (week 열은 이미 채워져 있음)
4. 파일 저장
5. 터미널에서 업로드 명령 실행
```

**업로드 명령**:
```bash
cd backend
.venv/bin/python3 pipelines/upload_manual.py A-3 data/manual/A-3.csv --source "관세청 무역통계 (HS 8542) 수동 다운로드"
```

또는 11개 모두 한 번에:
```bash
.venv/bin/python3 pipelines/upload_manual.py --all
```

업로드 후 자동 갱신:
- `backend/data/historical/<id>.json` 생성
- `backend/data/historical/_summary.json` 갱신
- 그 다음 `pipelines/forecast.py` 재실행하면 새 데이터 반영된 예측 출력

---

## A-3 관세청 수출 (DRAM IC 수출)

**무엇**: HS 8542.31 (메모리 IC) 월별 수출액 — 한국 메모리 산업 출하 직접 지표.

### 수동 수집 (10분)

| 단계 | 작업 |
|------|------|
| 1 | https://unipass.customs.go.kr/clip/index.do 접속 |
| 2 | 상단 메뉴 → "수출입통계" → "품목별 수출입실적" |
| 3 | 검색 조건: HS 코드 `854231` (메모리 IC), 기간 `202505 ~ 202604` (월간) |
| 4 | "조회" → 결과 표 우측 상단 "엑셀 다운로드" 클릭 |
| 5 | 다운로드한 Excel을 CSV로 저장 (Excel → 파일 → 다른 이름 저장 → CSV UTF-8) |

### CSV 변환

다운로드 데이터는 **월간**이므로 주간으로 변환:
- 월 값을 해당 월의 4-5주에 동일 분배 (간단)
- 또는 다음 달 발표일까지 forward-fill

`backend/data/manual/A-3.csv` 값 채우기 예:
```csv
week,value
2025-05-05,4825000000      ← 5월 발표값
2025-05-12,4825000000
2025-05-19,4825000000
2025-05-26,4825000000
2025-06-02,5102000000      ← 6월 발표값
...
```

(value 단위: USD, 백만 달러 단위로 통일하면 더 좋음)

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py A-3 data/manual/A-3.csv --source "관세청 무역통계 HS 854231 수출액 (월간→주간 분배)"
```

---

## A-4 KOSIS 재고/출하 지수

**무엇**: 통계청 광공업동향조사 — 전자부품 (DRAM 포함) 재고지수 / 출하지수 / 가동률.

### 수동 수집 (5분)

| 단계 | 작업 |
|------|------|
| 1 | https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1F31035 접속 |
| 2 | 가입 불필요. 바로 조회 가능. |
| 3 | 상단 "분류" 트리에서 `C26 전자부품·컴퓨터·영상·음향 및 통신장비` 선택 |
| 4 | "시점" 영역: 시작=`202505`, 끝=`202604` (월간), "행렬편집"으로 정렬 |
| 5 | 우측 상단 "다운로드" 클릭 → CSV 형식 선택 → 다운로드 |

### CSV 변환

월간 지수 값을 4주씩 분배:

```csv
week,value
2025-05-05,98.4         ← 5월 재고지수
2025-05-12,98.4
2025-05-19,98.4
2025-05-26,98.4
2025-06-02,102.1        ← 6월
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py A-4 data/manual/A-4.csv --source "KOSIS 광공업 재고지수 C26 (월간→주간 forward-fill)"
```

---

## A-5 AWS Spot 가격

**무엇**: AWS EC2 m6i.xlarge (메모리 대용 인스턴스) Spot 가격 — 메모리 수요 proxy.

### ⚠️ 무료 출처 한계

| 출처 | 한계 |
|------|------|
| AWS Spot Instance Advisor | 현재 시점만 (history X) |
| Vantage.sh | 일부 무료, 회원가입 |
| AWS CLI `describe-spot-price-history` | IAM 키 필요 (무료, 90일 history) |

### 권장 방식: AWS CLI (계정 + IAM 키 보유 시)

```bash
# AWS CLI 설치된 환경에서 실행
aws ec2 describe-spot-price-history \
    --instance-types m6i.xlarge \
    --product-descriptions "Linux/UNIX" \
    --start-time 2025-05-01 \
    --end-time 2026-04-30 \
    --availability-zone us-east-1a \
    --max-items 500 \
    --output json > /tmp/aws_spot.json
```

→ 그 다음 jq로 weekly 평균 추출:
```bash
jq -r '.SpotPriceHistory[] | "\(.Timestamp[0:10]),\(.SpotPrice)"' /tmp/aws_spot.json | sort | uniq -c > /tmp/aws_weekly.csv
```

### 대안: 손쉬운 우회

A-5는 단기 메모리 수요 proxy인데, 우리는 이미 **A-1 (TSM/UMC)**, **target-dram (MU/SK/Samsung blend)**으로 메모리 수요 proxy 확보. **A-5 생략 가능** — Prophet에 추가 정보 제공도가 낮음.

→ **A-5는 스킵 권장**. 업로드 안 함.

---

## A-6 Polymarket 봉쇄확률

**무엇**: 대만 지정학 리스크 (예: "China-Taiwan invasion before 2026" 예측시장 가격).

### 수동 수집 (15분)

| 단계 | 작업 |
|------|------|
| 1 | https://polymarket.com 접속 |
| 2 | 검색창에 `Taiwan` 입력 → 관련 active/resolved market 찾기 |
| 3 | 적합 market 예시: "Will China invade Taiwan in 2026?" |
| 4 | market 페이지 → 차트 영역의 "Export" 버튼 (또는 우클릭 → 데이터 복사) |
| 5 | 데이터 없으면 **Kalshi**, **Metaculus** 도 검색 |

### Metaculus 대안 (가장 안정적)

| 단계 | 작업 |
|------|------|
| 1 | https://www.metaculus.com 접속 |
| 2 | 검색: "Taiwan" |
| 3 | 대표 문항: "Will China invade Taiwan before 2027?" (https://www.metaculus.com/questions/) |
| 4 | 질문 페이지 → "Download data" (CSV) — 일별 community prediction |

### CSV 변환

일별 데이터를 주별 평균으로 그룹화:

```csv
week,value
2025-05-05,0.04         ← 4% 확률
2025-05-12,0.045
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py A-6 data/manual/A-6.csv --source "Metaculus #15356 China-Taiwan 침공 확률 (일간→주간 평균)"
```

---

## B-1 Earnings Call 감성

**무엇**: Samsung/SK Hynix/Micron 분기 콜에서 추출한 메모리 가격 sentiment 점수 (-1 ~ +1).

### 무료 출처 3종

| 사이트 | 비용 | 비고 |
|--------|------|------|
| **Motley Fool** (https://www.fool.com/earnings/call-transcripts/) | 무료 | 검색: "Samsung", "SK Hynix", "Micron" |
| **Samsung IR** (https://www.samsung.com/global/ir/financial-information/earnings-release/) | 무료 | 분기 Call PDF + 음성 |
| **SK Hynix IR** (https://www.skhynix.com/eng/ir/earningsRelease.do) | 무료 | 분기 발표 PDF |

### 수집 (분기당 ~30분, 1년 = 4분기 × 3사 = 12회)

| 단계 | 작업 |
|------|------|
| 1 | 위 사이트 중 하나에서 transcript 텍스트 또는 PDF 다운로드 |
| 2 | Claude/ChatGPT에 다음 프롬프트로 sentiment 추출: |
| | ``` |
| | 다음 earnings call transcript에서 메모리 가격 전망에 대한 sentiment를 |
| | -1 (매우 부정) ~ +1 (매우 긍정) 사이 점수로 평가하고, 근거 문장 3개 제시: |
| | <transcript 본문 붙여넣기> |
| | ``` |
| 3 | Claude 응답에서 점수만 추출하여 발표일 + 다음 분기 종료일까지 forward-fill |

### CSV 작성

```csv
week,value
2025-05-05,0.3      ← Samsung Q1 2025 (4월 30일 발표) sentiment
2025-05-12,0.3
2025-05-19,0.3
...
2025-07-28,0.5      ← Samsung Q2 2025 (7월 28일 발표) sentiment
2025-08-04,0.5
...
```

또는 3사 평균:
```csv
week,value
2025-05-05,0.4      ← (Samsung 0.3 + SK 0.5 + Micron 0.4) / 3
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py B-1 data/manual/B-1.csv --source "Samsung/SK/Micron 분기 Earnings Call 감성 (Claude 점수, 분기→주간 ffill)"
```

---

## B-2 대만 뉴스 감성

**무엇**: 대만 반도체 산업 관련 뉴스의 주별 볼륨 + 감성.

### 무료 출처 3종

| 출처 | 한계 |
|------|------|
| **NewsAPI.org free** (https://newsapi.org/) | 회원가입 후 100 requests/day. **과거 30일만** |
| **GDELT BigQuery** (https://console.cloud.google.com/bigquery) | GCP 결제 카드 등록. **1TB/월 무료** |
| **Google News RSS** (https://news.google.com/rss/search?q=Taiwan+semiconductor) | 무료, 무제한, 그러나 최근 뉴스만 |

### 권장: GDELT BigQuery (1년 history 가능)

| 단계 | 작업 |
|------|------|
| 1 | https://console.cloud.google.com 가입 (결제카드 필수, 무료 등급) |
| 2 | BigQuery 콘솔에서 다음 SQL 실행: |
| 2 | ```sql |
| | SELECT DATE_TRUNC(DATE(PARSE_TIMESTAMP('%Y%m%d%H%M%S', CAST(DATE AS STRING))), WEEK(MONDAY)) AS week, |
| |        COUNT(*) AS article_count |
| | FROM `gdelt-bq.gdeltv2.events` |
| | WHERE _PARTITIONTIME BETWEEN '2025-05-01' AND '2026-04-30' |
| |   AND Actor1CountryCode = 'TWN' |
| |   AND THEMES LIKE '%TECH_AUTOMOTIVE%' |
| | GROUP BY week ORDER BY week |
| | ``` |
| 3 | "Save Results" → CSV 다운로드 |

### CSV 작성

```csv
week,value
2025-05-05,12.4     ← 그 주 대만+반도체 관련 기사 수 (정규화)
2025-05-12,15.2
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py B-2 data/manual/B-2.csv --source "GDELT 2.0 BigQuery (TWN actor + tech theme article count)"
```

---

## B-3 Reddit / X 감성

**무엇**: r/hardware, r/buildapc, r/memorymarket 등에서 메모리 가격 관련 글 수 + sentiment.

### Reddit 직접 검색 (무료, 즉시)

| 단계 | 작업 |
|------|------|
| 1 | https://www.reddit.com/r/hardware/search/?q=memory+price&restrict_sr=on&sort=top&t=year 접속 |
| 2 | 결과 페이지를 주별로 스크롤 (Reddit는 자체 export 없음 → 수동 카운트) |
| 3 | 각 주별 게시물 수 카운트 또는 |
| 4 | **간소화**: 핵심 5개 게시물 제목 → Claude로 sentiment 점수화 |

### 자동화 (Reddit PRAW)

```python
# Reddit 앱 등록 (https://www.reddit.com/prefs/apps) 후
import praw
reddit = praw.Reddit(client_id='YOUR_ID', client_secret='YOUR_SECRET', user_agent='Sixsense Research')
posts = reddit.subreddit('hardware').search('memory price', sort='new', limit=500, time_filter='year')
for p in posts:
    print(p.created_utc, p.title, p.score)
```

### 대안 (가장 쉬움): Hacker News

```bash
# HN Search API (free, no auth)
curl "https://hn.algolia.com/api/v1/search?query=DRAM+memory+price&numericFilters=created_at_i>1714521600" | jq '.hits[] | {date: .created_at, title, points}'
```

### CSV 작성

```csv
week,value
2025-05-05,8       ← 그 주 관련 글 수
2025-05-12,12
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py B-3 data/manual/B-3.csv --source "Reddit r/hardware 'memory price' 주간 게시물 수"
```

---

## B-4 지정학 리스크 — **가장 강력한 무료 옵션 존재**

**무엇**: 지정학적 리스크 지수.

### ⭐ Caldara & Iacoviello GPR Index (학술, 무료, 1985~현재)

| 단계 | 작업 |
|------|------|
| 1 | https://www.matteoiacoviello.com/gpr.htm 접속 |
| 2 | 페이지 중간 "Geopolitical Risk Index" 섹션 |
| 3 | "GPR Index, Monthly Updates" 옆 **gpr_monthly.csv** 클릭 다운로드 |
| 4 | 또는 daily 버전: **gpr_daily_recent.csv** |

### CSV 변환

받은 파일에는 monthly GPR 값이 있음:
```csv
month,GPR
2025-05,156.32
2025-06,142.10
...
```

→ 우리 형식으로 변환 (월간 → 주간 forward-fill):
```csv
week,value
2025-05-05,156.32
2025-05-12,156.32
2025-05-19,156.32
2025-05-26,156.32
2025-06-02,142.10
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py B-4 data/manual/B-4.csv --source "Caldara & Iacoviello GPR Index monthly (학술, 무료, https://www.matteoiacoviello.com/gpr.htm)"
```

---

## B-5 LTA 비율 (Long-Term Agreement)

**무엇**: DRAM 장기 계약 vs spot 비율 — 공급망 가시성 지표.

### ⚠️ 직접 무료 출처 거의 없음

| 출처 | 한계 |
|------|------|
| DRAMeXchange | 유료 |
| TrendForce | 유료 |
| Samsung 분기 IR PDF | LTA % 직접 언급 가끔 (수동 추출) |
| 관세청 수출 변동성 | A-3과 중복 |

### 추정 방식 (전문가 추정)

분기 IR에서 "Long-term contracts represent ~70% of revenue" 같은 문장 추출:
- Samsung Q1 2025: 65%
- Samsung Q2 2025: 68%
- ...

분기당 1 값을 13주에 forward-fill.

### CSV 작성

```csv
week,value
2025-05-05,0.65
2025-05-12,0.65
2025-05-19,0.65
...
2025-07-28,0.68
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py B-5 data/manual/B-5.csv --source "Samsung/SK 분기 IR LTA 비율 언급 (수동 추출)"
```

> **권장**: B-5는 데이터 품질이 낮음. 처음에는 스킵 권장. Phase 6 후순위.

---

## B-6 HBM/D램 믹스

**무엇**: SK Hynix HBM 매출 비중 — 고부가가치 메모리 수요 강도.

### SK Hynix IR에서 직접 (무료, 분기당 10분)

| 단계 | 작업 |
|------|------|
| 1 | https://www.skhynix.com/eng/ir/earningsRelease.do 접속 |
| 2 | 분기별 "Earnings Conference Call Presentation" PDF 다운로드 (4개 분기 × 1년) |
| 3 | PDF 내 "Product Mix" 또는 "HBM Revenue %" 슬라이드 찾기 |
| 4 | 보통 페이지 3~5에 위치 (예: "HBM accounted for 40% of DRAM revenue") |
| 5 | 값을 손으로 추출 |

### Micron 분기 보고서 (보완)

| 단계 | 작업 |
|------|------|
| 1 | https://investors.micron.com/financial-information/quarterly-results 접속 |
| 2 | 분기 10-Q 또는 Earnings Presentation 다운로드 |
| 3 | "HBM" 검색 → 매출 비중 추출 |

### CSV 작성

```csv
week,value
2025-05-05,0.32   ← Q1 2025: SK Hynix HBM 32%
2025-05-12,0.32
...
2025-07-28,0.40   ← Q2 2025: 40%
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py B-6 data/manual/B-6.csv --source "SK Hynix 분기 IR HBM 매출 비중 (분기→주간 ffill)"
```

---

## B-7 BOM 신호 (Bill of Materials)

**무엇**: Apple/NVIDIA/AMD 신제품 출시에 따른 DRAM 수요 신호.

### 무료 출처 3종

| 출처 | 특징 |
|------|------|
| **iFixit Teardown** (https://www.ifixit.com/Device/) | 신제품 분해 → 부품 명시. 무료. |
| **AnandTech** (https://www.anandtech.com/) | 신제품 리뷰 + 메모리 스펙. 무료. |
| **Apple/NVIDIA RSS** | 출시 일정 + 메모리 용량 |

### 간소화 방식: 메모리 출시 캘린더

| 단계 | 작업 |
|------|------|
| 1 | Wikipedia 또는 Tom's Hardware에서 "2025 GPU releases", "2025 iPhone releases" 검색 |
| 2 | 출시 주별로 "메모리 수요 임팩트" 0~10 점수 부여 |
| | - GB200 출시 주: 10 (HBM3e 대량) |
| | - iPhone 17 출시 주: 8 (LPDDR5) |
| | - 일반 노트북 출시 주: 3 |
| 3 | 미출시 주: 0 |

### CSV 작성

```csv
week,value
2025-05-05,0
2025-05-12,2     ← 마이너 출시
...
2025-09-08,8     ← iPhone 17 출시 주
...
```

### 업로드

```bash
.venv/bin/python3 pipelines/upload_manual.py B-7 data/manual/B-7.csv --source "주요 IT 신제품 출시 주별 메모리 수요 점수 (수동 평가)"
```

---

## 📦 11개 일괄 업로드 (모든 CSV 채운 후)

```bash
cd backend
.venv/bin/python3 pipelines/upload_manual.py --all
```

출력 예시:
```
══════════════════════════════════════════════════════════════════════
  Sixsense Manual Upload
══════════════════════════════════════════════════════════════════════

  ✅ A-3          52주 [2025-05-05 ~ 2026-04-27]
  ✅ A-4          52주 [2025-05-05 ~ 2026-04-27]
  ⏭  A-5          (스킵 — CSV 비어있음)
  ✅ A-6          52주 [2025-05-05 ~ 2026-04-27]
  ✅ B-1          52주 [...]
  ✅ B-2          52주 [...]
  ✅ B-3          52주 [...]
  ✅ B-4          52주 [...]
  ⏭  B-5          (스킵 — CSV 비어있음)
  ✅ B-6          52주 [...]
  ✅ B-7          52주 [...]

  📊 전체 신호 현황: real=8, manual=9, real-proxy=1, ...
  📁 _summary.json 갱신됨
```

## 🔁 업로드 후 — 예측 재실행

```bash
.venv/bin/python3 pipelines/forecast.py
```

→ 17~18개 신호 기반 새 Prophet 예측 출력 + MAPE 재계산

---

## 📋 우선순위 권장 (시간 부족 시)

| 우선순위 | 신호 | 사유 | 예상 소요 |
|---------|------|------|----------|
| **1순위** | **B-4 지정학 리스크** | Caldara GPR CSV는 클릭 한 번 + 12개월 즉시 | 5분 |
| **2순위** | **A-4 KOSIS 재고지수** | 가입 불필요, 즉시 다운로드 | 10분 |
| **3순위** | **A-3 관세청 수출** | 가입 필요하나 무료, 클릭 다운로드 | 15분 (가입 시간 포함) |
| **4순위** | **B-6 HBM 비중** | SK Hynix IR PDF 4개 × 5분 | 20분 |
| **5순위** | **B-1 Earnings Call** | 12 transcript × Claude 분석 | 1시간 |
| **6순위** | **A-6 Metaculus** | 단일 CSV 다운로드 | 10분 |
| 후순위 | B-2, B-3, B-5, B-7 | 노이즈 큼 또는 수동 작업 많음 | 각 30분~2시간 |
| 스킵 권장 | **A-5 AWS Spot** | 정보 가치 낮음 (A-1과 중복) | — |

**총 권장**: 1~4순위만 완료해도 **추가 4개 신호 확보 → 13개로 학습** → 정확도 크게 향상 가능.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | 11개 신호 수동 수집 가이드 + 업로드 도구 + 우선순위 |
