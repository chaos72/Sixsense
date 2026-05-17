# Sixsense × Supabase 통합 가이드

> **목적**: 백엔드의 JSON 파일 저장소를 Supabase Postgres로 확장.
> **상태**: Phase 5f — 클라이언트 모듈 + 스키마 + sync 스크립트 완성 (사용자 1회 SQL 실행 필요)
>
> **자동 로드**: `Sixsense/.env`의 `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_ANON_KEY` 즉시 사용 가능

---

## 📦 구축된 자산

| 파일 | 역할 |
|------|------|
| `backend/app/supabase_client.py` | 경량 REST 래퍼 (외부 의존 없음) — `from app.supabase_client import sb` |
| `backend/app/schema.sql` | DDL — signals + signal_data + forecasts + RLS 정책 |
| `backend/pipelines/sync_supabase.py` | 13개 신호 + 예측 결과 → Supabase 일괄 업로드 |

---

## 🚀 사용자 액션 (1회, 3분)

### Step 1: Supabase Studio에서 스키마 실행

1. https://cmhounzyibgyrmvnhzda.supabase.co 접속 → 본인 프로젝트 로그인
2. 좌측 메뉴 → **[SQL Editor]** 클릭
3. **[+ New query]** 클릭
4. `backend/app/schema.sql` 내용 전체 복사 → 에디터에 붙여넣기
5. 우상단 **[Run]** 버튼 클릭 (Ctrl+Enter)
6. 하단 결과창에:
   ```
   table_name    | rows
   --------------|------
   signals       |    0
   signal_data   |    0
   forecasts     |    0
   ```
   가 나오면 성공

### Step 2: 데이터 동기화 (단일 명령)

```bash
cd /Users/youngseok.kim@dataiku.com/Documents/CAIO/Sixsense/backend
.venv/bin/python3 pipelines/sync_supabase.py
```

**예상 출력**:
```
  ✅ Supabase 연결됨 (status 404)
  📥 historical/ JSON 파일: 13개
  📤 signals: 13건 upsert... ✅
  📤 signal_data: 689건 upsert (배치)...
     500/689 완료
     689/689 완료
  ✅ signal_data: 689건 동기화
  📤 forecasts: 21건 upsert... ✅

  🔍 Supabase 확인:
     signals          13건
     signal_data     689건
     forecasts        21건
```

### Step 3: Supabase Studio에서 확인

1. 좌측 메뉴 → **[Table Editor]**
2. `signals` / `signal_data` / `forecasts` 테이블 클릭하여 데이터 확인

---

## 📊 스키마 구조

### `signals` (신호 메타, 13~20행)
```
signal_id       PK    'A-1', 'B-4', 'macro-fed', 'target-dram'
group                 '정형'/'비정형'/'거시'/'타겟'
name                  '대만 공급망' 등
source                'Yahoo Finance: TSM+UMC'
mode                  'real'/'real-proxy'/'manual'
range_start/end       DATE
metadata              JSONB
```

### `signal_data` (주간 시계열, ~700행)
```
id              BIGSERIAL PK
signal_id       FK → signals
week            DATE (월요일)
value           DOUBLE PRECISION
UNIQUE (signal_id, week)
```

### `forecasts` (Prophet 예측, 21행/사이클)
```
id              BIGSERIAL PK
model           'prophet_v1.3.0'
target_id       'target-dram'
train_cutoff    DATE
horizon         1~21
week            DATE
yhat / yhat_lower / yhat_upper
regressors_used JSONB
UNIQUE (model, train_cutoff, week)
```

### View: `v_signal_latest` (대시보드 메인용)
```sql
SELECT * FROM v_signal_latest;
-- 각 신호의 최근 1주 값을 한 번에 조회
```

---

## 🔐 보안 (RLS) 정책

스키마는 **개발 단계 정책**으로 설정됨:

| 작업 | 정책 |
|------|------|
| `anon` SELECT | ✅ 모든 테이블 |
| `anon` INSERT/UPDATE/DELETE | ✅ 허용 (publishable_key로 sync 가능) |
| `authenticated` | ✅ (anon 정책 상속) |
| `service_role` | ✅ (RLS 무시) |

**운영 전환 시**:
```sql
-- write 정책을 service_role only로 강화
DROP POLICY sig_write ON public.signals;
DROP POLICY sd_write ON public.signal_data;
DROP POLICY fc_write ON public.forecasts;

-- service_role만 INSERT 허용
CREATE POLICY sig_write ON public.signals
    FOR INSERT TO service_role WITH CHECK (true);
-- ... (signal_data, forecasts 동일)
```

이후 sync 시 `SUPABASE_SECRET_KEY`(sb_secret_*) 환경변수 필요.

---

## 🔄 운영 흐름 (매주 화요일)

```bash
# 1. 자동 수집 (13개 신호 갱신)
.venv/bin/python3 pipelines/auto_collectors.py --all

# 2. Prophet 재학습
.venv/bin/python3 pipelines/forecast.py

# 3. Supabase로 push
.venv/bin/python3 pipelines/sync_supabase.py
```

→ 3개 명령으로 1주차 업데이트 완료. cron으로 자동화 가능:
```
0 7 * * 2 cd /path/to/backend && ./run_weekly_update.sh
```

---

## 🖥️ 프론트엔드 연동 (다음 단계)

현재 frontend는 mocks/data.js를 import 함. Supabase로 전환:

```typescript
// frontend/src/services/supabase.ts (신규)
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY,
)

// 사용
const { data } = await supabase
  .from('signal_data')
  .select('week, value')
  .eq('signal_id', 'A-1')
  .order('week', { ascending: true })
```

`frontend/.env.local` (gitignored):
```
VITE_SUPABASE_URL=https://cmhounzyibgyrmvnhzda.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_ylQ6idpFL8...
```

---

## 🆘 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `404 Could not find the table 'public.signals'` | 스키마 미실행 | Step 1 다시 |
| `401 Secret API key required` | publishable_key가 메타 endpoint 호출 | 데이터 테이블만 접근 (이미 처리됨) |
| `403 new row violates row-level security` | RLS 정책에 write 미허용 | schema.sql 다시 실행 (write 정책 포함) |
| sync 중 일부 실패 | 일시적 네트워크 | 재실행 (upsert이라 idempotent) |
| 데이터 중복 | UNIQUE 제약 + ON CONFLICT 처리됨 | 안전 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-05-17 | Supabase 통합 — REST 클라이언트 + 스키마 + sync 스크립트 |
