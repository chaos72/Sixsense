import React, { useState, useEffect, useRef, useMemo, useCallback, Fragment } from 'react'
import { SIXSENSE_DATA } from '../mocks/data.js'
import { Sig, Sparkline, Modal, MetricCard, Tabs, Seg, HITL, HITL_DEFAULT_RULES, AiNote, BarRow, LineChart, FilterSelect, SectionHead, InsightCard } from '../components/components.jsx'
// USER-REQUESTED EXTENSION (#16) — 다음 수집/잔여 시간 동적 계산
import { nextTuesday06KST, lastTuesday06KST, formatTimeUntil } from '../utils/dates.js'

// S-001 Main Dashboard
const D = SIXSENSE_DATA;

// USER-REQUESTED EXTENSION (2026-05-18 #8/#9) — 이벤트 카테고리별 칩 클래스 매핑
function categoryClass(type) {
  if (type === "국내 반도체") return "domestic";
  if (type === "물리적 충돌") return "conflict";
  if (type === "기상이변") return "weather";
  if (type === "금융 위기") return "financial";
  return "other";
}


// USER-REQUESTED EXTENSION (2026-05-18 #7) — 수동 갱신 패널 (§09 풋바 바로 아래)
// 백엔드 /api/refresh POST → polling /api/refresh/jobs/{id} → 완료 시 page reload
const API_BASE = (typeof window !== "undefined" && window.location.hostname === "localhost")
  ? "http://localhost:8000" : "";

function RefreshPanel() {
  const [job, setJob] = useState(null);     // {queueId, status, stage, currentStep, totalSteps, logs, error, totalDurSec}
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  // 컴포넌트 마운트 시 단계 메타 가져오기 (사전 표시용) — 실패해도 무시
  const [stages, setStages] = useState([]);
  useEffect(() => {
    fetch(`${API_BASE}/api/refresh/stages`).then(r => r.ok ? r.json() : null).then(j => {
      if (j && j.stages) setStages(j.stages);
    }).catch(() => {});
  }, []);

  const stopPolling = () => {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
  };

  const startPolling = (queueId) => {
    stopPolling();
    pollRef.current = setInterval(async () => {
      try {
        const r = await fetch(`${API_BASE}/api/refresh/jobs/${queueId}`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const j = await r.json();
        setJob(j);
        if (j.status === "done") {
          stopPolling();
          // 완료 — data.js 가 갱신되었으므로 페이지 새로고침으로 신규 데이터 반영
          setTimeout(() => window.location.reload(), 1200);
        } else if (j.status === "failed") {
          stopPolling();
        }
      } catch (e) {
        setError(e.message);
        stopPolling();
      }
    }, 2000);
  };

  useEffect(() => () => stopPolling(), []);

  const trigger = async () => {
    setError(null);
    try {
      const r = await fetch(`${API_BASE}/api/refresh`, { method: "POST" });
      if (!r.ok) throw new Error(`HTTP ${r.status}: ${await r.text()}`);
      const j = await r.json();
      setJob({ ...j, logs: [], currentStep: j.currentStep || 0 });
      startPolling(j.queueId);
    } catch (e) {
      setError(`백엔드 호출 실패 — uvicorn(:8000) 이 실행 중인지 확인하세요. (${e.message})`);
    }
  };

  const isRunning = job && (job.status === "queued" || job.status === "running");
  const isDone = job && job.status === "done";
  const isFailed = job && job.status === "failed";
  const progressPct = job ? Math.round((job.currentStep / Math.max(1, job.totalSteps || stages.length || 5)) * 100) : 0;

  return (
    <div className="refresh-panel">
      <div className="refresh-row">
        <button
          className={`btn refresh-btn ${isRunning ? "running" : ""}`}
          onClick={trigger}
          disabled={isRunning}
          title="현재까지 수집된 모든 데이터와 예측 모델을 즉시 재학습합니다 (~1~2분)"
        >
          <span className={`refresh-ic ${isRunning ? "spin" : ""}`}>🔄</span>
          <span>{isRunning ? "갱신 중…" : isDone ? "✅ 갱신 완료 — 새로고침 중" : isFailed ? "⚠ 다시 시도" : "수동 갱신 실행"}</span>
        </button>
        <div className="refresh-hint">
          모든 신호 수집 + 뉴스 분류 + 모델 재학습 + 인사이트 + 빌드 (5단계, 약 1~2분)
        </div>
      </div>

      {job && (
        <div className="refresh-progress">
          <div className="refresh-progress-bar">
            <div className={`refresh-progress-fill ${isFailed ? "failed" : isDone ? "done" : ""}`} style={{ width: `${progressPct}%` }} />
          </div>
          <div className="refresh-progress-meta">
            <span>
              <strong>단계 {job.currentStep}/{job.totalSteps || stages.length || 5}</strong> · {job.stage || "초기화"}
            </span>
            {job.totalDurSec && <span className="muted">총 {job.totalDurSec}초</span>}
          </div>
        </div>
      )}

      {job && job.logs && job.logs.length > 0 && (
        <ul className="refresh-log">
          {job.logs.map((l) => (
            <li key={l.step} className={l.ok ? "ok" : "fail"}>
              <span className="refresh-log-tag">{l.ok ? "✅" : "❌"}</span>
              <span><strong>{l.stage}</strong> <span className="muted">({l.durSec}s)</span> — {l.lastLine}</span>
            </li>
          ))}
        </ul>
      )}

      {(error || (isFailed && job.error)) && (
        <div className="refresh-error">
          <strong>오류:</strong> {error || job.error}
        </div>
      )}
    </div>
  );
}


// USER-REQUESTED EXTENSION (2026-05-18 #3, #4) — §02 Multi-Model 검증 표 (헤드라인/아키텍처/환경처리는 #4에서 삭제)
function ModelValidationPanel({ mv }) {
  if (!mv) return null;
  return (
    <div className="model-validation">
      <div className="grid-2">
        <div className="card">
          <div className="dlabel" style={{ marginBottom: 8 }}>단기 (1~7주) — 우수 모델 자동 선정</div>
          <table className="model-table">
            <thead>
              <tr><th>모델</th><th>MAPE</th><th>평가</th></tr>
            </thead>
            <tbody>
              {mv.shortRows.map((r) => (
                <tr key={r.model} className={r.winner ? "winner" : ""}>
                  <td>{r.model}</td>
                  <td className="num-cell">{r.mape.toFixed(2)}%</td>
                  <td>{r.eval}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="dlabel" style={{ marginBottom: 8 }}>중장기 (8~21주)</div>
          <table className="model-table">
            <thead>
              <tr><th>모델</th><th>held-out MAPE</th></tr>
            </thead>
            <tbody>
              {mv.midRows.map((r) => (
                <tr key={r.model}>
                  <td>{r.model}</td>
                  <td className="num-cell">{r.mape.toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="model-train-time">
            ⏱ 학습 시간 (전체 파이프라인): <span className="num">~{mv.trainTotal}초</span>{" "}
            ({mv.trainTimes.map((t, i) => (
              <Fragment key={t.name}>
                {i > 0 && " + "}
                {t.name} <span className="num">{t.sec}s</span>
              </Fragment>
            ))})
          </div>
        </div>
      </div>
    </div>
  );
}

function Dashboard({ onNav }) {
  const m = D.meta;
  const [chartRange, setChartRange] = useState("all");
  
  return (
    <div className="content">
      {/* Top 3 cards */}
      <div className="section">
        <SectionHead num="01" icon="◉" title="가격 스냅샷" sub={`${m.updated || "최신"} 기준 — 매주 화요일 06:00 자동 갱신`} />
        <div className="grid-snapshot">
          {/* USER-REQUESTED CHANGE (v2.1) — 모바일에서 세 가격 카드를 한 카드로 합침 (price-combo, 데스크톱은 영향 없음) */}
          <div className="price-combo">
            <MetricCard
              label="현재 계약가"
              code="SPOT · DDR5 8Gb"
              value={`$${m.current.toFixed(2)}`}
              unit="/ GB"
              change={`${m.currentChange} 전주 대비`}
              changeTone="pos"
            />
            <MetricCard
              label="1~7주 AI 예측가"
              code={`GBR · 신뢰 ${m.confidence ?? 81}%`}
              value={`$${m.pred7.toFixed(2)}`}
              unit="/ GB"
              change={`${m.pred7Change} 예상`}
              changeTone="pos"
              sub="🔍 클릭하여 근거 보기"
              onClick={() => onNav("S-002", { horizon: 7 })}
            />
            <MetricCard
              label="8~21주 AI 예측가"
              code={`LSTM · 신뢰 ${(m.confidence ?? 81) - 7}%`}
              value={`$${m.pred21.toFixed(2)}`}
              unit="/ GB"
              change={`${m.pred21Change} 예상`}
              changeTone="pos"
              sub="🔍 클릭하여 근거 보기"
              onClick={() => onNav("S-002", { horizon: 21 })}
            />
          </div>
          <InsightCard insight={m.insight} />
        </div>
      </div>

      {/* DRAM Chart */}
      <div className="section">
        <SectionHead num="02" icon="◢" title="DRAM 52주 히스토리 + AI 예측" sub="차트의 특정 주 클릭 → 주별 스냅샷" actions={<ChartRangeSeg value={chartRange} onChange={setChartRange} />} />
        <div className="card dram-chart-card">
          <DramChart range={chartRange} onPointClick={(d) => onNav("S-009", { week: d.x })} />
          <ChartLegend range={chartRange} />
        </div>
        <ModelValidationPanel mv={m.modelValidation} />
      </div>

      {/* 14 signals */}
      <div className="section">
        <SectionHead num="03" icon="◧" title="10개 프록시 신호 통합 현황" sub="각 카드 클릭 → 상세" />
        
        <div style={{ marginBottom: 18 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div className="dlabel">Group A · 정형 (6종)</div>
            <button className="btn sm" onClick={() => onNav("S-003", { tab: "A-1" })}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" /></svg>
              전체 상세
            </button>
          </div>
          <div className="grid-7">
            {D.signalsA.map(s => <SignalCard key={s.id} s={s} onClick={() => onNav("S-003", { tab: s.id })} />)}
          </div>
        </div>

        <div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div className="dlabel">Group B · 비정형 (4종)</div>
            <button className="btn sm" onClick={() => onNav("S-004", { tab: "B-1" })}>
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" /></svg>
              전체 상세
            </button>
          </div>
          <div className="grid-7">
            {D.signalsB.map(s => <SignalCard key={s.id} s={s} onClick={() => onNav("S-004", { tab: s.id })} />)}
          </div>
        </div>
      </div>

      {/* News + Macro */}
      <div className="section">
        <div className="grid-2">
          <div>
            <SectionHead num="04" icon="◳" title="AI 뉴스 & 감성 분석" actions={<button className="btn sm" onClick={() => onNav("S-006")}>전체 목록 →</button>} />
            <div className="card" style={{ padding: 0 }}>
              {D.news.filter(n => n.hot).map((n, i) => (
                <div key={i} className="card tappable flat" onClick={() => onNav("S-007", { news: n })}
                     style={{ border: "none", borderBottom: i < 2 ? "1px solid var(--border)" : "none", borderRadius: 0, padding: "12px 18px", display: "flex", alignItems: "flex-start", gap: 12 }}>
                  <Sig tone={n.tone}>{n.tone === "pos" ? "긍정" : n.tone === "neg" ? "부정" : "중립"}</Sig>
                  {/* USER-REQUESTED CHANGE (v2.0) — 제목/출처를 한 컬럼에 위·아래로 배치 */}
                  <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", gap: 3 }}>
                    <div style={{ fontSize: 13, fontWeight: 500, lineHeight: 1.4 }}>{n.title}</div>
                    <span className="muted mono" style={{ fontSize: 11 }}>{n.source}</span>
                  </div>
                  <span className="num" style={{ fontSize: 11, color: n.tone === "pos" ? "var(--sig-pos)" : n.tone === "neg" ? "var(--sig-neg)" : "var(--sig-neu)", fontWeight: 500, whiteSpace: "nowrap" }}>
                    {n.score > 0 ? "+" : ""}{n.score.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <SectionHead num="05" icon="◔" title="거시경제 지표" actions={<button className="btn sm" onClick={() => onNav("S-008", { tab: "fed" })}>전체 →</button>} />
            <div className="card" style={{ padding: 0 }}>
              {D.macro.map((mi, i) => (
                <div key={i} className="card tappable flat macro-row" onClick={() => onNav("S-008", { tab: mi.id })}
                     style={{ border: "none", borderBottom: i < D.macro.length - 1 ? "1px solid var(--border)" : "none", borderRadius: 0, padding: "10px 18px", display: "grid", gridTemplateColumns: "1fr 0.85fr 1.3fr", alignItems: "center", gap: 12 }}>
                  <span style={{ fontSize: 12.5, fontWeight: 500 }}>{mi.name}</span>
                  {/* USER-REQUESTED CHANGE (v2.1) — 값/긍부정을 한 컬럼에 위·아래로 배치 */}
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                    <span className="num" style={{ fontSize: 13, fontWeight: 600 }}>{mi.value}</span>
                    <Sig tone={mi.tone}>{mi.change}</Sig>
                  </div>
                  {/* USER-REQUESTED CHANGE (v2.1) — 설명 글자색을 지표명과 동일하게 */}
                  <span style={{ fontSize: 11, fontWeight: 500 }}>{mi.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Global events + Accuracy */}
      <div className="section">
        <div className="grid-2">
          <div>
            <SectionHead num="06" icon="⚠" title="글로벌 이벤트 모니터링" sub="우선순위(위험도) + 카테고리 다양성 Top 10" actions={<button className="btn sm" onClick={() => onNav("S-010")}>전체 목록 →</button>} />
            {/* USER-REQUESTED EXTENSION (2026-05-18 #8) — 3건 → 10건 + 유형(type) 칩 추가 표시 */}
            <div className="card events-list">
              {D.events.slice(0, 10).map((e) => (
                <div key={e.id} className="card tappable flat events-row" onClick={() => onNav("S-011", { event: e })}>
                  {/* USER-REQUESTED CHANGE (v2.1) — 위험/뉴스유형을 한 컬럼에 위·아래로 배치, 제목 영역 확대 */}
                  <div className="events-risktype">
                    <Sig tone={e.risk === "high" ? "neg" : e.risk === "mid" ? "neu" : "pos"}>
                      {e.risk === "high" ? "고위험" : e.risk === "mid" ? "중위험" : "저위험"}
                    </Sig>
                    <span className={`events-type events-type-${categoryClass(e.type)}`}>{e.type}</span>
                  </div>
                  <span className="events-title">{e.title}</span>
                  <span className="mono muted events-region">{e.region}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <SectionHead num="07" icon="▤" title="AI 예측 정확도 트래킹" actions={<button className="btn sm" onClick={() => onNav("S-012")}>전체 이력 →</button>} />
            <div className="card" style={{ padding: 0 }}>
              {D.accuracy.filter(a => a.actual !== null).slice(0, 3).map((a, i) => (
                <div key={i} className="acc-row" style={{ padding: "12px 16px", borderBottom: i < 2 ? "1px solid var(--border)" : "none", display: "grid", gridTemplateColumns: "auto auto auto 1fr auto", alignItems: "center", gap: 14, fontSize: 12 }}>
                  <span className="muted mono">{Math.round((lastTuesday06KST().getTime() - Date.parse(a.predDate)) / (1000 * 60 * 60 * 24 * 7))}주전</span>
                  <span>예측 <span className="num" style={{ fontWeight: 600 }}>${a.pred.toFixed(2)}</span></span>
                  <span className="muted mono">→</span>
                  <span>실제 <span className="num" style={{ fontWeight: 600 }}>${a.actual.toFixed(2)}</span></span>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <Sig tone={a.tone}>오차 {a.error.toFixed(1)}%</Sig>
                    <button className="btn ghost sm" onClick={() => onNav("S-013", { row: a })}>당시 신호 →</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Collection foot */}
      <div className="section">
        <SectionHead num="08" icon="▤" title="이번 주 새 수집 데이터 현황" actions={<button className="btn sm" onClick={() => onNav("S-014")}>수집 현황 →</button>} />
        <div className="foot-bar">
          <div><span className="label">정형</span><span className="num">{D.collection.groupA.reduce((s, x) => s + x.newItems, 0)}건</span><span className="muted"> 수집완료 ✓</span></div>
          <div className="sep"></div>
          <div><span className="label">비정형</span><span className="num">{D.collection.groupB.reduce((s, x) => s + x.newItems, 0)}건</span><span className="muted"> 수집완료 ✓</span></div>
          <div className="sep"></div>
          <div><span className="label">수집실패</span><span className="num">{D.collection.summary.fail}건</span></div>
          <div className="sep"></div>
          <div><span className="label">사이클</span><span className="num">매주 화요일 06:00 KST</span></div>
          <div style={{ marginLeft: "auto" }}>
            <span className="muted">다음 수집까지</span>
            <span className="num" style={{ marginLeft: 8, fontWeight: 600 }}>{formatTimeUntil(nextTuesday06KST())}</span>
          </div>
        </div>
        {/* USER-REQUESTED EXTENSION (2026-05-18 #7) — 수동 갱신 버튼 (전체 파이프라인 즉시 재실행) */}
        <RefreshPanel />
      </div>
    </div>
  );
}

// ==== Signal Card ====
function SignalCard({ s, onClick }) {
  return (
    <div className="card tappable" onClick={onClick}>
      <div className="card-h">
        <span className="code">{s.id}</span>
        <Sig tone={s.tone}>
          {s.tone === "alert" ? "ALERT" : s.tone === "pos" ? "긍정" : s.tone === "neg" ? "부정" : "중립"}
        </Sig>
      </div>
      <div className="card-label">{s.name}</div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 6 }}>
        <span className="num" style={{ fontSize: 17, fontWeight: 600 }}>{s.value}</span>
      </div>
      <Sparkline data={s.spark} tone={s.tone} height={28} />
    </div>
  );
}

// ==== Chart range segmented control ====
function ChartRangeSeg({ value, onChange }) {
  return (
    <Seg
      value={value}
      onChange={onChange}
      options={[
        { value: "short", label: "단기 1~7주" },
        { value: "mid", label: "중장기 8~21주" },
        { value: "all", label: "전체" },
      ]}
    />
  );
}

// ==== DRAM Chart with bands ====
function DramChart({ range = "all", onPointClick }) {
  const last = D.history[D.history.length - 1];
  const lastF7 = D.forecast7[D.forecast7.length - 1];
  
  // Slice history based on range
  let histStart = -52;
  let xMax = 21;
  let xLabels = [
    { x: -52, label: "52주전" },
    { x: -26, label: "26주전" },
    { x: 0, label: "현재" },
    { x: 7, label: "+7주" },
    { x: 14, label: "+14주" },
    { x: 21, label: "+21주" },
  ];
  
  if (range === "short") {
    histStart = -26;
    xMax = 7;
    xLabels = [
      { x: -26, label: "26주전" },
      { x: -13, label: "13주전" },
      { x: 0, label: "현재" },
      { x: 3, label: "+3주" },
      { x: 7, label: "+7주" },
    ];
  } else if (range === "mid") {
    histStart = -13;
    xMax = 21;
    xLabels = [
      { x: -13, label: "13주전" },
      { x: 0, label: "현재" },
      { x: 7, label: "+7주" },
      { x: 14, label: "+14주" },
      { x: 21, label: "+21주" },
    ];
  }
  
  const histSeries = D.history.filter(d => d.week >= histStart).map(d => ({ x: d.week, value: d.value }));
  const f7Data = D.forecast7.filter(d => d.week <= xMax);
  const f21Data = D.forecast21.filter(d => d.week <= xMax);
  
  const series = [];
  const bands = [];
  
  // Always show history up to current
  series.push({ data: histSeries, color: "var(--text)" });

  // USER-REQUESTED EXTENSION (2026-05-18 #4 → #6) — 4개 모델 동시 표시. #6: Prophet 황색 dotted / HistGBR 보라 dashed-long으로 명확 구분
  // Prophet baseline (1~21w 전 구간) — 황색 dotted (촘촘한 점)
  if (D.forecast_prophet && D.forecast_prophet.length) {
    const prophetData = [{ x: 0, value: last.value }, ...D.forecast_prophet.filter(d => d.week <= xMax).map(d => ({ x: d.week, value: d.value }))];
    series.push({ data: prophetData, color: "var(--chart-baseline)", strokeWidth: 1.6, dashed: "2 4" });
  }
  // HistGBR (1~7w, 단기 보조 모델) — 보라 long-dash
  if (D.forecast_histgbr && D.forecast_histgbr.length && range !== "mid") {
    const histgbrData = [{ x: 0, value: last.value }, ...D.forecast_histgbr.filter(d => d.week <= xMax).map(d => ({ x: d.week, value: d.value }))];
    series.push({ data: histgbrData, color: "var(--chart-secondary)", strokeWidth: 1.8, dashed: "7 3" });
  }

  // Short range: only 1-7 forecast (blue)
  if (range === "short") {
    const f7 = [{ x: 0, value: last.value }, ...f7Data.map(d => ({ x: d.week, value: d.value }))];
    const f7Band = [{ x: 0, lower: last.value, upper: last.value }, ...f7Data.map(d => ({ x: d.week, lower: d.lower, upper: d.upper }))];
    bands.push({ data: f7Band, color: "var(--sig-info)" });
    series.push({ data: f7, color: "var(--sig-info)", dashed: true, dots: true, onDotClick: onPointClick, endLabel: `1~7주 $${lastF7.value.toFixed(2)}` });
  }
  
  // Mid range: show 1~7 in blue (context) + 8~21 in pastel green (emphasis)
  if (range === "mid") {
    // 1~7 segment — same blue style as short
    const f7Full = [{ x: 0, value: last.value }, ...D.forecast7.map(d => ({ x: d.week, value: d.value }))];
    const f7Band = [{ x: 0, lower: last.value, upper: last.value }, ...D.forecast7.map(d => ({ x: d.week, lower: d.lower, upper: d.upper }))];
    bands.push({ data: f7Band, color: "var(--sig-info)" });
    series.push({ data: f7Full, color: "var(--sig-info)", dashed: true, dots: true, onDotClick: onPointClick });
    
    // 8~21 segment — pastel green emphasis (same color as 전체 mode)
    const f21Seg = [{ x: 7, value: lastF7.value }, ...D.forecast21.map(d => ({ x: d.week, value: d.value }))];
    const f21Band = [{ x: 7, lower: lastF7.lower, upper: lastF7.upper }, ...D.forecast21.map(d => ({ x: d.week, lower: d.lower, upper: d.upper }))];
    bands.push({ data: f21Band, color: "var(--forecast-mid)" });
    series.push({ data: f21Seg, color: "var(--forecast-mid)", strokeWidth: 2.6, dashed: false, dots: true, dotR: 3.5, onDotClick: onPointClick, endLabel: `8~21주 $${D.forecast21[D.forecast21.length-1].value.toFixed(2)}` });
  }
  
  // All: 1~7 blue + 8~21 pastel green
  if (range === "all") {
    const f7 = [{ x: 0, value: last.value }, ...f7Data.map(d => ({ x: d.week, value: d.value }))];
    const f7Band = [{ x: 0, lower: last.value, upper: last.value }, ...f7Data.map(d => ({ x: d.week, lower: d.lower, upper: d.upper }))];
    bands.push({ data: f7Band, color: "var(--sig-info)" });
    series.push({ data: f7, color: "var(--sig-info)", dashed: true, dots: true, onDotClick: onPointClick, endLabel: `$${lastF7.value.toFixed(2)}` });
    
    const f21 = [{ x: 7, value: lastF7.value }, ...f21Data.map(d => ({ x: d.week, value: d.value }))];
    const f21Band = [{ x: 7, lower: lastF7.lower, upper: lastF7.upper }, ...f21Data.map(d => ({ x: d.week, lower: d.lower, upper: d.upper }))];
    bands.push({ data: f21Band, color: "var(--forecast-mid)" });
    series.push({ data: f21, color: "var(--forecast-mid)", dashed: true, dots: true, onDotClick: onPointClick, endLabel: `$${D.forecast21[D.forecast21.length-1].value.toFixed(2)}` });
  }
  
  return (
    <div style={{ position: "relative" }}>
      <LineChart
        width={1200}
        height={300}
        bands={bands}
        refLines={[
          { value: D.meta.current, label: `현재 $${D.meta.current.toFixed(2)}`, color: "var(--text-faint)" },
        ]}
        series={series}
        xLabels={xLabels}
        preserveAspectRatio="none"
      />
    </div>
  );
}

function ChartLegend({ range }) {
  // USER-REQUESTED EXTENSION (2026-05-18 #4) — Prophet baseline + HistGBR 범례 추가
  return (
    <div className="chart-legend-wrap" style={{ display: "flex", gap: 18, marginTop: 12, paddingLeft: 44, fontSize: 11, color: "var(--text-dim)", flexWrap: "wrap" }}>
      <span className="chart-legend-item leg-actual">
        <svg width="20" height="2"><line x1="0" y1="1" x2="20" y2="1" stroke="var(--text)" strokeWidth="1.75"/></svg> 실측 ({range === "short" ? "26주" : range === "mid" ? "13주" : "52주"})
      </span>
      <span className="chart-legend-item leg-prophet">
        <svg width="22" height="6"><line x1="0" y1="3" x2="22" y2="3" stroke="var(--chart-baseline)" strokeWidth="1.6" strokeDasharray="2 4"/></svg>
        <span style={{ color: "var(--chart-baseline)", fontWeight: 600 }}>Prophet baseline</span> (1~21w)
      </span>
      {range !== "mid" && (
        <span className="chart-legend-item leg-histgbr">
          <svg width="22" height="6"><line x1="0" y1="3" x2="22" y2="3" stroke="var(--chart-secondary)" strokeWidth="1.8" strokeDasharray="7 3"/></svg>
          <span style={{ color: "var(--chart-secondary)", fontWeight: 600 }}>HistGBR</span> (1~7w · 6.86%)
        </span>
      )}
      {(range === "short" || range === "mid" || range === "all") && (
        <span className="chart-legend-item leg-gbr">
          <svg width="20" height="6"><line x1="0" y1="3" x2="20" y2="3" stroke="var(--sig-info)" strokeWidth="1.75" strokeDasharray="4 3"/></svg>
          <strong style={{ color: "var(--sig-info)" }}>GBR ★</strong> (1~7w · 4.54%) · 신뢰구간
        </span>
      )}
      {(range === "mid" || range === "all") && (
        <span className="chart-legend-item leg-lstm">
          <svg width="20" height="6"><line x1="0" y1="3" x2="20" y2="3" stroke="var(--forecast-mid)" strokeWidth={range === "mid" ? "2.4" : "1.75"} strokeDasharray={range === "mid" ? null : "4 3"}/></svg>
          <strong style={{ color: "var(--forecast-mid)" }}>LSTM ★</strong> (8~21w · 9.19%) {range === "mid" && <span style={{ color: "var(--forecast-mid)", fontWeight: 600, marginLeft: 4 }}>(중점)</span>}
        </span>
      )}
      {/* USER-REQUESTED CHANGE (v2.1) — 모바일에서 CSS order로 순서 재배치(실측→힌트→Prophet→HistGBR→GBR→LSTM), 데스크톱은 marginLeft:auto 로 기존처럼 오른쪽 끝 고정 */}
      <span className="muted leg-hint" style={{ marginLeft: "auto", whiteSpace: "nowrap" }}>예측 데이터 포인트 클릭 → S-009</span>
    </div>
  );
}

Object.assign(window, { Dashboard, SignalCard });


export { Dashboard, SignalCard, ChartRangeSeg, DramChart, ChartLegend }
