-- Sixsense Supabase 스키마
-- 사용법: Supabase Studio → SQL Editor → 본 파일 내용 붙여넣기 → [Run]
--   URL: https://cmhounzyibgyrmvnhzda.supabase.co (사용자 프로젝트)
--
-- 이 스키마는:
--  1. signals 테이블 — 신호 메타 (ID, 출처, 모드, 갱신 시각)
--  2. signal_data 테이블 — 주간 시계열 (week, value)
--  3. forecasts 테이블 — Prophet 예측 결과 저장
--  4. RLS off + 익명 read+write 허용 (개발 편의, 운영 전환 시 정책 강화)

-- ────────────────────────────────────────────────────────────────────────────
-- 1. signals: 신호 메타
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.signals (
    signal_id      TEXT PRIMARY KEY,                  -- 'A-1', 'B-4', 'macro-fed', 'target-dram' 등
    "group"        TEXT,                              -- '정형'/'비정형'/'거시'/'타겟'
    name           TEXT,                              -- 한글 설명
    source         TEXT,                              -- '관세청 API', 'Yahoo Finance' 등
    mode           TEXT,                              -- 'real'/'real-proxy'/'manual'/'synthetic'
    range_start    DATE,
    range_end      DATE,
    collected_at   TIMESTAMPTZ DEFAULT NOW(),
    note           TEXT,
    metadata       JSONB DEFAULT '{}'::jsonb
);

COMMENT ON TABLE public.signals IS 'Sixsense 14신호 + 5거시 + 1타겟의 메타정보';

-- ────────────────────────────────────────────────────────────────────────────
-- 2. signal_data: 주간 시계열
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.signal_data (
    id             BIGSERIAL PRIMARY KEY,
    signal_id      TEXT NOT NULL REFERENCES public.signals(signal_id) ON DELETE CASCADE,
    week           DATE NOT NULL,                     -- 해당 주의 월요일
    value          DOUBLE PRECISION,
    inserted_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (signal_id, week)
);

CREATE INDEX IF NOT EXISTS idx_signal_data_signal_week ON public.signal_data (signal_id, week DESC);
CREATE INDEX IF NOT EXISTS idx_signal_data_week        ON public.signal_data (week DESC);

COMMENT ON TABLE public.signal_data IS '신호별 주간 시계열. UNIQUE(signal_id, week)로 중복 방지';

-- ────────────────────────────────────────────────────────────────────────────
-- 3. forecasts: Prophet 예측 결과
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.forecasts (
    id             BIGSERIAL PRIMARY KEY,
    model          TEXT NOT NULL,                     -- 'prophet_v1.3.0' 등
    target_id      TEXT NOT NULL,                     -- 'target-dram' 등 (signals 참조 또는 free-text)
    trained_at     TIMESTAMPTZ DEFAULT NOW(),
    train_cutoff   DATE NOT NULL,
    horizon        SMALLINT NOT NULL,                 -- 1~21 (forecast week ahead)
    week           DATE NOT NULL,                     -- 예측 대상 주
    yhat           DOUBLE PRECISION,
    yhat_lower     DOUBLE PRECISION,
    yhat_upper     DOUBLE PRECISION,
    interval_width DOUBLE PRECISION DEFAULT 0.80,
    regressors_used JSONB DEFAULT '[]'::jsonb,
    UNIQUE (model, train_cutoff, week)
);

CREATE INDEX IF NOT EXISTS idx_forecasts_cutoff_week ON public.forecasts (train_cutoff, week);

COMMENT ON TABLE public.forecasts IS 'Prophet 예측 결과. (model, train_cutoff, week) 조합 unique';

-- ────────────────────────────────────────────────────────────────────────────
-- 4. RLS — 개발 단계 허용 (운영 전 강화 필수)
-- ────────────────────────────────────────────────────────────────────────────
-- 옵션 A (가장 간단): RLS off — 모든 키가 읽기/쓰기
ALTER TABLE public.signals      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.signal_data  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forecasts    ENABLE ROW LEVEL SECURITY;

-- 옵션 B (권장): RLS on + 익명 read + 인증 write만 허용
DROP POLICY IF EXISTS sig_read   ON public.signals;
DROP POLICY IF EXISTS sd_read    ON public.signal_data;
DROP POLICY IF EXISTS fc_read    ON public.forecasts;
DROP POLICY IF EXISTS sig_write  ON public.signals;
DROP POLICY IF EXISTS sd_write   ON public.signal_data;
DROP POLICY IF EXISTS fc_write   ON public.forecasts;

-- 익명 read 허용
CREATE POLICY sig_read   ON public.signals     FOR SELECT TO anon USING (true);
CREATE POLICY sd_read    ON public.signal_data FOR SELECT TO anon USING (true);
CREATE POLICY fc_read    ON public.forecasts   FOR SELECT TO anon USING (true);

-- 익명 write도 허용 (Phase 5 단순화 — 운영 전환 시 service_role only로 변경 필요)
CREATE POLICY sig_write  ON public.signals     FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY sd_write   ON public.signal_data FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY fc_write   ON public.forecasts   FOR ALL TO anon USING (true) WITH CHECK (true);

-- ────────────────────────────────────────────────────────────────────────────
-- 5. 편의 뷰 (대시보드에서 직접 쿼리 가능)
-- ────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW public.v_signal_latest AS
SELECT
    s.signal_id,
    s."group",
    s.name,
    s.source,
    s.mode,
    sd.week AS latest_week,
    sd.value AS latest_value
FROM public.signals s
LEFT JOIN LATERAL (
    SELECT week, value
    FROM public.signal_data
    WHERE signal_id = s.signal_id
    ORDER BY week DESC
    LIMIT 1
) sd ON true;

COMMENT ON VIEW public.v_signal_latest IS '신호별 최근 1개 값 — 대시보드 메인 화면용';

-- ────────────────────────────────────────────────────────────────────────────
-- 완료 확인
-- ────────────────────────────────────────────────────────────────────────────
SELECT
    'signals' AS table_name, COUNT(*) AS rows FROM public.signals
UNION ALL
SELECT 'signal_data', COUNT(*) FROM public.signal_data
UNION ALL
SELECT 'forecasts',   COUNT(*) FROM public.forecasts;
