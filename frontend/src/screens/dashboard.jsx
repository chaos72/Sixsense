import React, { useState, useEffect, useRef, useMemo, useCallback, Fragment } from 'react'
import { SIXSENSE_DATA } from '../mocks/data.js'
import { Sig, Sparkline, MetricCard, LineChart, SectionHead, InsightCard } from '../components/components.jsx'
// USER-REQUESTED EXTENSION (#16) — 다음 수집/잔여 시간 동적 계산
import { nextTuesday06KST, formatTimeUntil } from '../utils/dates.js'

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


// USER-REQUESTED EXTENSION (v2.2) — 수동 갱신 패널 (§08 풋바 바로 아래)
// 아이폰/웹: 버튼 → Vercel 함수(/api/refresh) → GitHub Actions 트리거 →
// /api/refresh-status 폴링 → 완료 시 자동 새로고침. (백엔드 서버 불필요, 무료)
function RefreshPanel() {
  const [phase, setPhase] = useState("idle"); // idle | running | done | failed
  const [msg, setMsg] = useState("");
  const [elapsed, setElapsed] = useState(0);
  const pollRef = useRef(null);
  const tickRef = useRef(null);
  const triggeredAtRef = useRef(0);

  const stopAll = () => {
    if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null; }
    if (tickRef.current) { clearInterval(tickRef.current); tickRef.current = null; }
  };
  useEffect(() => () => stopAll(), []);

  const startPolling = () => {
    if (pollRef.current) return;
    pollRef.current = setInterval(async () => {
      try {
        const r = await fetch("/api/refresh-status", { cache: "no-store" });
        const j = await r.json();
        const created = j.createdAt ? new Date(j.createdAt).getTime() : 0;
        // 방금 트리거한 실행인지 판별 (이전 완료 실행을 오인하지 않도록 2분 버퍼)
        const isOurs = created >= triggeredAtRef.current - 120000;
        if (j.status === "completed" && isOurs) {
          stopAll();
          if (j.conclusion === "success") {
            setPhase("done");
            setMsg("갱신 완료 — 새 데이터 반영까지 약 1분, 곧 자동 새로고침됩니다");
            setTimeout(() => window.location.reload(), 75000);
          } else {
            setPhase("failed");
            setMsg(`공용 주방 실행 실패 (${j.conclusion || "unknown"})`);
          }
        } else if (j.status === "in_progress" && isOurs) {
          setMsg("공용 주방에서 데이터 수집·예측 검증 중… (약 5분 소요)");
        } else if (j.status === "queued" || !isOurs) {
          setMsg("대기열 등록됨 — 곧 시작합니다…");
        }
      } catch (e) { /* 네트워크 일시 오류는 무시하고 계속 폴링 */ }
    }, 12000);
  };

  const trigger = async () => {
    setPhase("running");
    setMsg("공용 주방 가동 요청 중…");
    setElapsed(0);
    triggeredAtRef.current = Date.now();
    if (!tickRef.current) {
      const t0 = Date.now();
      tickRef.current = setInterval(() => setElapsed(Math.floor((Date.now() - t0) / 1000)), 1000);
    }
    try {
      const r = await fetch("/api/refresh", { method: "POST" });
      const j = await r.json().catch(() => ({}));
      if (r.ok && (j.status === "triggered" || j.status === "already_running")) {
        setMsg(j.status === "already_running"
          ? "이미 갱신이 진행 중입니다 — 완료를 기다립니다"
          : "공용 주방 시작됨 — 약 5분 소요");
        startPolling();
      } else {
        stopAll();
        setPhase("failed");
        setMsg(j.error || `요청 실패 (HTTP ${r.status})`);
      }
    } catch (e) {
      stopAll();
      setPhase("failed");
      setMsg(`요청 실패: ${String(e).slice(0, 80)}`);
    }
  };

  const isRunning = phase === "running";
  const mm = Math.floor(elapsed / 60), ss = elapsed % 60;

  return (
    <div className="refresh-panel">
      <div className="refresh-row">
        <button
          className={`btn refresh-btn ${isRunning ? "running" : ""}`}
          onClick={trigger}
          disabled={isRunning}
          title="GitHub Actions(무료)에서 전체 데이터 수집 + 예측 검증 + AI 요약 후 자동 배포 (약 5분)"
        >
          <span className={`refresh-ic ${isRunning ? "spin" : ""}`}>🔄</span>
          <span>{isRunning ? "갱신 중…" : phase === "done" ? "✅ 갱신 완료" : phase === "failed" ? "⚠ 다시 시도" : "수동 갱신 실행"}</span>
        </button>
        <div className="refresh-hint">
          클릭하면 전체 신호 수집 + 예측 검증 + AI 요약 + 자동 배포 (약 5분, 무료·서버 불필요)
        </div>
      </div>

      {phase !== "idle" && (
        <div className="refresh-progress">
          <div className="refresh-progress-bar">
            <div
              className={`refresh-progress-fill ${phase === "failed" ? "failed" : phase === "done" ? "done" : ""}`}
              style={{ width: isRunning ? "66%" : "100%" }}
            />
          </div>
          <div className="refresh-progress-meta">
            <span>{msg}</span>
            {isRunning && <span className="muted">{mm}분 {ss}초</span>}
          </div>
        </div>
      )}

      {phase === "failed" && (
        <div className="refresh-error">
          <strong>오류:</strong> {msg}
        </div>
      )}
    </div>
  );
}


const pct = (v) => (v === null || v === undefined ? "—" : `${v > 0 ? "+" : ""}${v.toFixed(1)}%`);
const toneOf = (v) => (v > 0 ? "pos" : v < 0 ? "neg" : "neu");

// §07 예측 검증 요약 — honest_backtest.py 결과 (워크포워드 백테스트, 모델 vs 단순 기준선)
function ValidationSummary({ v, onNav }) {
  if (!v) return <div className="card muted" style={{ fontSize: 12 }}>예측 검증 결과가 아직 없습니다.</div>;
  const level = v.variants[0];
  const pr = level.procurement;
  return (
    <div className="card">
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <Sig tone={v.pass ? "pos" : "neg"} size="lg">{v.pass ? "✅ 합격" : "❌ 불합격"}</Sig>
        <span style={{ fontSize: 12.5, fontWeight: 500 }}>
          {v.pass ? "AI 모델이 단순 기준선보다 정확했습니다." : "AI 모델이 '지난주 값 그대로'보다 부정확했습니다."}
        </span>
      </div>
      <table className="model-table">
        <thead><tr><th>방식</th><th>모델 오차</th><th>기준선 오차</th><th>판정</th></tr></thead>
        <tbody>
          {v.variants.map((x) => (
            <tr key={x.key}>
              <td>{x.name}</td>
              <td className="num-cell">{x.overall.modelMape.toFixed(1)}%</td>
              <td className="num-cell">{x.overall.naiveMape.toFixed(1)}%</td>
              <td>{x.pass ? "합격" : "불합격"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="muted" style={{ fontSize: 11.5, marginTop: 10, lineHeight: 1.6 }}>
        앱이 쓰던 방식대로 {pr.horizonWeeks}주 대기 여부를 정했다면 평균 구매 단가 <strong>{pct(pr.modelPct)}</strong>
        (미래를 안다면 최대 {pct(pr.perfectPct)}). {v.dataWeeks}주 데이터 · {v.runAt} 검증 · 오차는 평균 절대 백분율 오차(MAPE).
      </div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
        <button className="btn sm" onClick={() => onNav("S-012")}>검증 방법·상세 →</button>
      </div>
    </div>
  );
}

function Dashboard({ onNav }) {
  const m = D.meta;
  const tr = D.trend;
  const v = D.validation;

  return (
    <div className="content">
      {/* Top 3 cards — 측정값만 (예측 수치 없음: 검증 불합격) */}
      <div className="section">
        <SectionHead num="01" icon="◉" title="시장 지표 스냅샷" sub={`${m.updated || "최신"} 기준 · ${m.proxyNote}`} />
        <div className="grid-snapshot">
          {/* USER-REQUESTED CHANGE (v2.1) — 모바일에서 세 카드를 한 카드로 합침 (price-combo, 데스크톱은 영향 없음) */}
          <div className="price-combo">
            <MetricCard
              label={m.unitLabel}
              code={m.unitDesc}
              value={m.current.toFixed(1)}
              unit={m.unitShort}
              change={`${m.currentChange} 전주 대비`}
              changeTone={toneOf(parseFloat(m.currentChange))}
            />
            <MetricCard
              label="최근 4주 변화 (실측)"
              code={`13주 ${pct(tr.change13w)} · 52주 고점 ${tr.high52.value.toFixed(1)} (${tr.high52.date})`}
              value={pct(tr.change4w)}
              change={`주간 변동폭 ±${tr.weeklyVol13w}% (최근 13주)`}
              changeTone="neu"
            />
            <MetricCard
              label="AI 가격 예측 검증"
              code={v ? `모델 오차 ${v.variants[0].overall.modelMape.toFixed(1)}% vs 단순 기준선 ${v.variants[0].overall.naiveMape.toFixed(1)}%` : "검증 결과 없음"}
              value={v ? (v.pass ? "합격" : "불합격") : "—"}
              change={v && !v.pass ? "예측 수치를 표시하지 않습니다" : "검증 통과"}
              changeTone={v && v.pass ? "pos" : "neg"}
              onClick={() => onNav("S-012")}
            />
          </div>
          <InsightCard insight={m.insight} />
        </div>
      </div>

      {/* 주가지수 추이 — 실측만 */}
      <div className="section">
        <SectionHead num="02" icon="◢" title={`${m.unitLabel} 52주 추이`} sub="실측값 · 예측선 없음 (검증 불합격)"
          actions={<button className="btn sm" onClick={() => onNav("S-009")}>8주 전과 비교 →</button>} />
        <div className="card dram-chart-card">
          <IndexChart />
        </div>
      </div>

      {/* 14 signals */}
      <div className="section">
        <SectionHead num="03" icon="◧" title="수집 신호 10종" sub="각 카드 클릭 → 실측 이력" />
        
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
                    {mi.stale
                      ? <Sig tone="alert">갱신 중단</Sig>
                      : <Sig tone={mi.tone}>{mi.change}</Sig>}
                    <span className="muted mono" style={{ fontSize: 10 }}>{mi.asOf} 기준</span>
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
            <SectionHead num="07" icon="▤" title="AI 가격 예측 검증" sub="워크포워드 백테스트"
              actions={<button className="btn sm" onClick={() => onNav("S-012")}>상세 →</button>} />
            <ValidationSummary v={v} onNav={onNav} />
          </div>
        </div>
      </div>

      {/* Collection foot */}
      <div className="section">
        <SectionHead num="08" icon="▤" title="이번 주 새 수집 데이터 현황" actions={<button className="btn sm" onClick={() => onNav("S-014")}>수집 현황 →</button>} />
        <div className="foot-bar">
          <div><span className="label">정상</span><span className="num">{D.collection.summary.success}개</span></div>
          <div className="sep"></div>
          <div><span className="label">갱신 중단</span><span className="num">{D.collection.summary.stale}개</span><span className="muted"> (수집 중단 또는 값 정체)</span></div>
          <div className="sep"></div>
          <div><span className="label">수집 실패</span><span className="num">{D.collection.summary.fail}개</span><span className="muted"> / 전체 {D.collection.summary.total}개</span></div>
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
    <div className="card tappable" onClick={onClick} title={s.staleReason || undefined}>
      <div className="card-h">
        <span className="code">{s.id}</span>
        {s.stale
          ? <Sig tone="alert">갱신 중단</Sig>
          : <Sig tone={s.tone}>{s.tone === "pos" ? "긍정" : s.tone === "neg" ? "부정" : "중립"}</Sig>}
      </div>
      <div className="card-label">{s.name}</div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 6 }}>
        <span className="num" style={{ fontSize: 17, fontWeight: 600 }}>{s.value}</span>
      </div>
      <Sparkline data={s.spark} tone={s.stale ? "neu" : s.tone} height={28} />
      <div className="muted mono" style={{ fontSize: 10, marginTop: 4 }}>{s.asOf} 기준</div>
    </div>
  );
}

// ==== 주가지수 52주 실측 차트 (예측선 없음) ====
function IndexChart() {
  const series = [{ data: D.history.map((d) => ({ x: d.week, value: d.value })), color: "var(--text)" }];
  const at = (w) => (D.history.find((d) => d.week === w) || {}).date || "";
  return (
    <LineChart
      width={1200}
      height={300}
      series={series}
      refLines={[{ value: D.meta.current, label: `현재 ${D.meta.current.toFixed(1)} ${D.meta.unitShort}`, color: "var(--text-faint)" }]}
      xLabels={[
        { x: -51, label: at(-51) },
        { x: -26, label: at(-26) },
        { x: -13, label: at(-13) },
        { x: 0, label: `${at(0)} (최신)` },
      ]}
      preserveAspectRatio="none"
    />
  );
}

Object.assign(window, { Dashboard, SignalCard });


export { Dashboard, SignalCard, IndexChart }
