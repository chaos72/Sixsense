# LLM Sentiment 무료 키 가이드 (Anthropic 크레딧 없이)

> **목적**: B-1/B-5/B-6 (메모리社 sentiment 분석)을 Anthropic 결제 없이 작동시키기.
> **현재**: 키워드 fallback으로 즉시 동작 중. LLM 키 추가 시 정확도 향상.

---

## 🆓 무료 옵션 비교

| 옵션 | 무료 한도 | 발급 시간 | 결제 카드 |
|------|----------|----------|----------|
| **Google Gemini** | **1,500 req/day** | 5분 (즉시) | ❌ 불필요 |
| **Groq** (Llama 3.3) | **14,400 req/day** | 5분 (즉시) | ❌ 불필요 |
| Together AI | $25 free credit | 5분 | 필요 (인증만) |
| Mistral La Plateforme | 한정 | 10분 | 필요 |
| OpenRouter | 일부 모델 무료 | 5분 | 필요 (인증) |
| Anthropic Claude | $5 충전 시작 | 즉시 | 필요 |

→ **권장: Gemini (Google) 또는 Groq — 둘 다 결제카드 불필요**

---

## 🥇 Gemini API (Google) — 권장

### 발급 단계 (5분)

1. https://aistudio.google.com 접속
2. Google 계정 로그인
3. 좌측 **[Get API Key]** 클릭
4. **[Create API Key in new project]** 클릭
5. 키 자동 생성 → 복사 (예: `AIzaSy...`)

### .env에 추가

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense
echo "GEMINI_API_KEY=AIzaSy여기에복사한키" >> .env
```

### 검증

```bash
cd backend
source ../.env
.venv/bin/python3 -c "
import os, requests
key = os.environ['GEMINI_API_KEY']
r = requests.post(
    f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}',
    json={'contents':[{'parts':[{'text':'반도체 메모리 가격 sentiment를 한 단어로'}]},
          'generationConfig':{'maxOutputTokens':30}})
print(r.json()['candidates'][0]['content']['parts'][0]['text'] if r.status_code==200 else r.text)
"
```

### B-1/B-5/B-6 재실행 (자동으로 Gemini 사용)

```bash
.venv/bin/python3 pipelines/auto_collectors.py B-1
# → Anthropic 시도 → 크레딧 부족 → Gemini 자동 fallback
#   ✅ B-1   34주  | Google News (167 entries, LLM 6회 호출, 34주)
```

### 한도 + 비용

- **1,500 req/day** 무료 (gemini-2.0-flash 기준)
- B-1+B-5+B-6 합쳐서 1회 실행 = 약 50~80 호출 → 무료 한도 내 충분
- 매주 cron 갱신 시 1년 = 약 4,000 호출 → 여전히 무료

---

## 🥈 Groq (Llama 3.3) — 대안

### 발급 (5분)

1. https://console.groq.com 접속
2. Google/Github 로그인
3. 좌측 **[API Keys]** → **[Create API Key]**
4. 이름: `Sixsense` → 복사 (예: `gsk_...`)

### .env에 추가

```bash
echo "GROQ_API_KEY=gsk_여기에복사한키" >> .env
```

### 한도

- **14,400 req/day** 무료 (llama-3.3-70b-versatile)
- 가장 관대한 무료 tier
- 단점: 응답이 Gemini보다 약간 verbose

---

## 🔄 자동 fallback 동작

`backend/pipelines/auto_collectors.py`의 `_llm_sentiment()` 함수:

```
시도 순서:
1. ANTHROPIC_API_KEY → 크레딧 부족 시 다음으로
2. GEMINI_API_KEY    → 실패 시 다음으로
3. GROQ_API_KEY      → 실패 시 다음으로
4. 키워드 fallback   (정확도 ↓ 하지만 항상 작동)
```

3개 중 어느 하나만 있어도 LLM 정확도 확보.

---

## 📊 정확도 비교 (예상)

| 모드 | 정확도 | 비용 | 적용 시점 |
|------|--------|------|----------|
| 키워드 fallback | 60% | 무료 | **현재** (이미 작동) |
| **Gemini Flash** | **85%** | **무료** | Gemini 키 등록 후 |
| Groq Llama 3.3 | 82% | 무료 | Groq 키 등록 후 |
| Claude Haiku | 90% | $0.1/년 | 크레딧 충전 후 |

---

## 🆘 트러블슈팅

### "Gemini HTTP 400: Quota exceeded"
- 일일 한도 초과 (드물지만 가능)
- 다음날 재시도 또는 Groq로 fallback

### "GEMINI_API_KEY invalid"
- aistudio.google.com에서 키 재생성
- `.env` 파일에서 키 앞뒤 공백 제거

### B-1/5/6가 여전히 키워드 fallback 사용
- `source ../.env` 먼저 실행 (환경변수 로드)
- 또는 collector가 자동 로드 (auto_collectors.py 내장)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | Anthropic 크레딧 없이 LLM 사용 가이드 — Gemini/Groq 무료 옵션 |
