import React, { useState, useEffect, useRef, useMemo, useCallback, Fragment } from 'react'
import { SIXSENSE_DATA } from '../mocks/data.js'
import { Sig, Sparkline, Modal, MetricCard, Tabs, Seg, HITL, HITL_DEFAULT_RULES, AiNote, BarRow, LineChart, FilterSelect, SectionHead } from '../components/components.jsx'
// USER-REQUESTED EXTENSION (#16) — 다음 수집 일정 동적 계산
import { nextTuesday06KST, lastTuesday06KST, formatTuesdayKST } from '../utils/dates.js'

// Full-page detail screens: S-006, S-008, S-010, S-012, S-014
const D3 = SIXSENSE_DATA;

// ==== Shared page header ====
function PageHead({ num, icon, title, sub, summary, onBack }) {
  return (
    <div style={{ marginBottom: 22 }}>
      <button className="back-btn" onClick={onBack} style={{ marginBottom: 14 }}>
        ← 메인으로 돌아가기
      </button>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 16, marginBottom: 6 }}>
        <div>
          <div className="dlabel">화면 {num}</div>
          <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, letterSpacing: "-0.02em" }}>
            {icon && <span style={{ marginRight: 8 }}>{icon}</span>}
            {title}
          </h1>
          {sub && <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>{sub}</div>}
        </div>
        {summary}
      </div>
    </div>
  );
}

// ==== S-006 News full list ====
function S006({ onClose, onNav }) {
  const [filter, setFilter] = useState("all");
  const [source, setSource] = useState("all");
  const [sort, setSort] = useState("impact");

  let items = [...D3.news];
  if (filter !== "all") items = items.filter(n => n.tone === filter);
  if (source !== "all") items = items.filter(n => n.source === source);
  if (sort === "impact") items.sort((a, b) => Math.abs(b.score) - Math.abs(a.score));
  if (sort === "conf") items.sort((a, b) => b.conf - a.conf);
  if (sort === "date") items.sort((a, b) => b.date.localeCompare(a.date));

  const counts = { pos: D3.news.filter(n => n.tone === "pos").length, neu: D3.news.filter(n => n.tone === "neu").length, neg: D3.news.filter(n => n.tone === "neg").length };
  const sources = [...new Set(D3.news.map(n => n.source))];
  
  return (
    <div className="content">
      <PageHead num="S-006" icon="◳" title="AI 뉴스 분석 전체 목록"
        sub={`이번 주 수집: 총 ${D3.news.length}건`}
        summary={
          <div className="chips">
            <button className={`chip ${filter === "all" ? "on" : ""}`} onClick={() => setFilter("all")}>전체 <span className="n">{D3.news.length}</span></button>
            <button className={`chip ${filter === "pos" ? "on" : ""}`} onClick={() => setFilter("pos")}>🟢 긍정 <span className="n">{counts.pos}</span></button>
            <button className={`chip ${filter === "neu" ? "on" : ""}`} onClick={() => setFilter("neu")}>🟡 중립 <span className="n">{counts.neu}</span></button>
            <button className={`chip ${filter === "neg" ? "on" : ""}`} onClick={() => setFilter("neg")}>🔴 부정 <span className="n">{counts.neg}</span></button>
          </div>
        }
        onBack={onClose}
      />
      
      <div className="filterbar">
        <select value={source} onChange={(e) => setSource(e.target.value)}>
          <option value="all">출처: 전체</option>
          {sources.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="impact">정렬: 영향도순</option>
          <option value="conf">정렬: 신뢰도순</option>
          <option value="date">정렬: 발행일순</option>
        </select>
        <span className="count">{items.length}건 표시</span>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <table className="tbl">
          <thead>
            <tr>
              <th style={{ width: 90 }}>발행일</th>
              <th>제목 (한국어 / 원문)</th>
              <th style={{ width: 120 }}>출처</th>
              <th className="num" style={{ width: 80 }}>점수</th>
              <th style={{ width: 80 }}>판정</th>
              <th className="num" style={{ width: 80 }}>신뢰도</th>
              <th style={{ width: 40 }}></th>
            </tr>
          </thead>
          <tbody>
            {items.map((n, i) => (
              <tr key={i} className="tappable" onClick={() => onNav("S-007", { news: n })}>
                <td className="mono muted">{n.date}</td>
                <td>
                  <div style={{ fontWeight: 500 }}>{n.title}</div>
                  <div className="muted mono" style={{ fontSize: 10, marginTop: 2 }}>{n.titleEn}</div>
                </td>
                <td className="mono">{n.source}</td>
                <td className="num" style={{ fontWeight: 600, color: n.tone === "pos" ? "var(--sig-pos)" : n.tone === "neg" ? "var(--sig-neg)" : "var(--text)" }}>
                  {n.score > 0 ? "+" : ""}{n.score.toFixed(2)}
                </td>
                <td><Sig tone={n.tone}>{n.tone === "pos" ? "긍정" : n.tone === "neg" ? "부정" : "중립"}</Sig></td>
                <td className="num muted">{n.conf}%</td>
                <td className="muted mono">→</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 22 }}>
        <HITL rules={HITL_DEFAULT_RULES} />
      </div>
    </div>
  );
}

// ==== S-008 Macro indicators ====
function S008({ tab: initialTab, onClose }) {
  const [tab, setTab] = useState(initialTab || "fed");
  const m = D3.macro.find(x => x.id === tab);

  const explanations = {
    fed: `"금리 인하 → 데이터센터 투자 증가 → DRAM 수요 상승. 동결 지속으로 중립 신호. 인하 전환 시 수요 강한 긍정 전환 예상. Polymarket 금리 인하 확률 42%."`,
    dxy: `"달러 강세 = 한국 수출 메모리 수출가 부담. 신흥국 데이터센터 투자 위축 가능. DXY 105 돌파 시 추가 부정 압력."`,
    pmi: `"50 초과 = 확장 국면. 글로벌 제조업 회복은 산업용·자동차용 DRAM 수요 지지. 현재 52.3 → 확장세 6개월 지속."`,
    krw: `"원화 약세 = 한국 메모리 4사 수출 채산성 개선이나, 수입 원자재(웨이퍼·기판) 원가 부담. 순효과는 분기 시차로 반영."`,
    cu: `"구리 선행 시차 10주. 현재 +8.3%, 6주 연속 상승. 10주 후 DRAM 6~8% 상승 가능. 자세한 분석은 Graph RAG (S-005)."`
  };

  return (
    <div className="content">
      <PageHead num="S-008" icon="◔" title="거시경제 지표 통합 상세" onBack={onClose} />

      <Tabs
        active={tab} onChange={setTab}
        tabs={D3.macro.map(m => ({ id: m.id, label: m.name }))}
      />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 16, marginBottom: 22 }}>
        <div>
          <div className="dlabel">현재값</div>
          <div className="num" style={{ fontSize: 28, fontWeight: 600 }}>{m.value}</div>
        </div>
        <div>
          <div className="dlabel">변화 신호</div>
          <div style={{ marginTop: 6 }}><Sig tone={m.tone} size="lg">{m.change}</Sig></div>
        </div>
        <div>
          <div className="dlabel">설명</div>
          <div style={{ marginTop: 4, fontSize: 12 }}>{m.desc}</div>
        </div>
        <div>
          <div className="dlabel">수집 출처</div>
          <div className="mono" style={{ marginTop: 4, fontSize: 12 }}>{m.id === "fed" ? "FRED API" : m.id === "dxy" ? "ICE" : m.id === "pmi" ? "S&P Global" : m.id === "krw" ? "BOK API" : "LME Public"}</div>
        </div>
      </div>

      <div className="dlabel" style={{ marginBottom: 8 }}>52주 추이</div>
      <div className="card">
        <LineChart
          width={1200} height={240}
          series={[{ data: m.history.map((v, i) => ({ x: i, value: v })), color: m.tone === "pos" ? "var(--sig-pos)" : m.tone === "neg" ? "var(--sig-neg)" : "var(--text)", dots: true }]}
          refLines={m.id === "pmi" ? [{ value: 50, label: "확장/수축 경계 50", color: "var(--sig-info)" }] : []}
          xLabels={[{ x: 0, label: "52주전" }, { x: 3, label: "26주전" }, { x: 6, label: "현재" }]}
        />
      </div>

      <div className="dlabel" style={{ margin: "22px 0 8px" }}>월별 원본 데이터 (최근 7개월)</div>
      <table className="tbl">
        <thead><tr><th>월</th><th className="num">{m.name}</th><th>판정</th><th>비고</th></tr></thead>
        <tbody>
          {m.history.slice().reverse().map((v, i) => (
            <tr key={i}>
              <td className="mono">{`2026-${String(4 - i).padStart(2, "0")}`}</td>
              <td className="num" style={{ fontWeight: 600 }}>{typeof v === "number" ? v.toFixed(m.id === "krw" ? 0 : 2) : v}{m.id === "fed" ? "%" : ""}</td>
              <td><Sig tone={i === 0 ? m.tone : "neu"}>{i === 0 ? (m.tone === "pos" ? "긍정" : m.tone === "neg" ? "부정" : "중립") : "—"}</Sig></td>
              <td className="muted" style={{ fontSize: 11 }}>{i === 0 ? "최신 발표" : ""}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: 22 }}>
        <AiNote label="DRAM 연관 설명 · AI 해석">
          {explanations[tab]}
        </AiNote>
      </div>

      <div style={{ marginTop: 22 }}>
        <HITL rules={HITL_DEFAULT_RULES} />
      </div>
    </div>
  );
}

// ==== S-010 Global events list ====
function S010({ onClose, onNav }) {
  const [risk, setRisk] = useState("all");
  const [type, setType] = useState("all");
  
  let items = D3.events;
  if (risk !== "all") items = items.filter(e => e.risk === risk);
  if (type !== "all") items = items.filter(e => e.type === type);
  
  const types = [...new Set(D3.events.map(e => e.type))];
  const counts = { high: D3.events.filter(e => e.risk === "high").length, mid: D3.events.filter(e => e.risk === "mid").length, low: D3.events.filter(e => e.risk === "low").length };

  return (
    <div className="content">
      <PageHead num="S-010" icon="⚠" title="글로벌 이벤트 모니터링"
        sub={`이번 주 탐지: 총 ${D3.events.length}건`}
        summary={
          <div className="chips">
            <button className={`chip ${risk === "all" ? "on" : ""}`} onClick={() => setRisk("all")}>전체 <span className="n">{D3.events.length}</span></button>
            <button className={`chip ${risk === "high" ? "on" : ""}`} onClick={() => setRisk("high")}>🔴 고위험 <span className="n">{counts.high}</span></button>
            <button className={`chip ${risk === "mid" ? "on" : ""}`} onClick={() => setRisk("mid")}>🟡 중위험 <span className="n">{counts.mid}</span></button>
            <button className={`chip ${risk === "low" ? "on" : ""}`} onClick={() => setRisk("low")}>🟢 저위험 <span className="n">{counts.low}</span></button>
          </div>
        }
        onBack={onClose}
      />

      <div className="filterbar">
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="all">유형: 전체</option>
          {types.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <span className="count">{items.length}건 표시</span>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <table className="tbl">
          <thead>
            <tr>
              <th style={{ width: 80 }}>위험도</th>
              <th style={{ width: 100 }}>유형</th>
              <th style={{ width: 110 }}>지역</th>
              <th>이벤트 요약</th>
              <th style={{ width: 90 }}>영향 방향</th>
              <th style={{ width: 90 }}>발생일</th>
              <th style={{ width: 40 }}></th>
            </tr>
          </thead>
          <tbody>
            {items.map(e => (
              <tr key={e.id} className="tappable" onClick={() => onNav("S-011", { event: e })}>
                <td><Sig tone={e.risk === "high" ? "neg" : e.risk === "mid" ? "neu" : "pos"}>{e.risk === "high" ? "고위험" : e.risk === "mid" ? "중위험" : "저위험"}</Sig></td>
                <td>{e.type}</td>
                <td className="mono muted">{e.region}</td>
                <td style={{ fontWeight: 500 }}>{e.title}</td>
                <td className="mono">{e.impact}</td>
                <td className="mono muted">{e.date}</td>
                <td className="muted mono">→</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 22 }}>
        <HITL rules={HITL_DEFAULT_RULES} />
      </div>
    </div>
  );
}

// ==== S-012 Accuracy history ====
function S012({ onClose, onNav }) {
  const [filter, setFilter] = useState("all");
  let items = D3.accuracy;
  if (filter === "7") items = items.filter(a => a.horizon === "7주");
  if (filter === "21") items = items.filter(a => a.horizon === "21주");

  const completed = D3.accuracy.filter(a => a.error !== null);
  const avgAll = (completed.reduce((s, a) => s + a.error, 0) / completed.length).toFixed(1);
  const avg7 = (() => { const c = completed.filter(a => a.horizon === "7주"); return c.length ? (c.reduce((s, a) => s + a.error, 0) / c.length).toFixed(1) : "—"; })();
  const avg21 = (() => { const c = completed.filter(a => a.horizon === "21주"); return c.length ? (c.reduce((s, a) => s + a.error, 0) / c.length).toFixed(1) : "—"; })();

  // Error trend (chronological completed predictions)
  const trend = completed.slice().reverse();

  return (
    <div className="content">
      <PageHead num="S-012" icon="▤" title="AI 예측 정확도 전체 이력" sub="MAPE 기준 평균 오차" onBack={onClose}
        summary={
          <div style={{ display: "flex", gap: 20, fontFamily: "var(--font-mono)" }}>
            <div><div className="dlabel">전체 MAPE</div><div className="num" style={{ fontSize: 22, fontWeight: 600 }}>{avgAll}%</div></div>
            <div><div className="dlabel">7주 평균</div><div className="num" style={{ fontSize: 22, fontWeight: 600, color: "var(--sig-pos)" }}>{avg7}%</div></div>
            <div><div className="dlabel">21주 평균</div><div className="num" style={{ fontSize: 22, fontWeight: 600, color: "var(--sig-neu)" }}>{avg21}%</div></div>
          </div>
        }
      />

      <div className="dlabel" style={{ marginBottom: 8 }}>누적 오차율 추이</div>
      <div className="card" style={{ marginBottom: 22 }}>
        <LineChart
          width={1200} height={200}
          series={[{ data: trend.map((a, i) => ({ x: i, value: a.error })), color: "var(--text)", dots: true, onDotClick: () => {} }]}
          refLines={[{ value: 5.8, label: "현재 평균 5.8%", color: "var(--sig-info)" }]}
          xLabels={trend.length ? [{ x: 0, label: trend[0].predDate }, { x: trend.length - 1, label: trend[trend.length - 1].predDate }] : []}
        />
      </div>

      <div className="filterbar">
        <button className={`chip ${filter === "all" ? "on" : ""}`} onClick={() => setFilter("all")}>전체</button>
        <button className={`chip ${filter === "7" ? "on" : ""}`} onClick={() => setFilter("7")}>7주 예측</button>
        <button className={`chip ${filter === "21" ? "on" : ""}`} onClick={() => setFilter("21")}>21주 예측</button>
        <span className="count">{items.length}건</span>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <table className="tbl">
          <thead>
            <tr>
              <th>예측일</th>
              <th>구분</th>
              <th className="num">예측값</th>
              <th className="num">실제값</th>
              <th className="num">오차율</th>
              <th>판정</th>
              <th style={{ width: 130 }}></th>
            </tr>
          </thead>
          <tbody>
            {items.map((a, i) => (
              <tr key={i}>
                <td className="mono">{a.predDate}</td>
                <td>{a.horizon}</td>
                <td className="num" style={{ fontWeight: 600 }}>${a.pred.toFixed(2)}</td>
                <td className="num" style={{ fontWeight: 600 }}>{a.actual !== null ? `$${a.actual.toFixed(2)}` : <span className="muted">(대기중)</span>}</td>
                <td className="num">{a.error !== null ? `${a.error.toFixed(1)}%` : <span className="muted">—</span>}</td>
                <td>{a.tone ? <Sig tone={a.tone}>{a.tone === "pos" ? "양호" : a.tone === "neg" ? "부정확" : "허용범위"}</Sig> : <span className="muted" style={{ fontSize: 11 }}>관측중</span>}</td>
                <td>{a.actual !== null && <button className="btn ghost sm" onClick={() => onNav("S-013", { row: a })}>당시 신호 →</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 22 }}>
        <HITL rules={HITL_DEFAULT_RULES} />
      </div>
    </div>
  );
}

// ==== S-014 Collection status ====
function S014({ onClose }) {
  const [tab, setTab] = useState("A");
  const c = D3.collection;
  const items = tab === "A" ? c.groupA : c.groupB;
  
  return (
    <div className="content">
      <PageHead num="S-014" icon="▤" title="데이터 수집 현황 상세" sub={`수집 사이클: ${c.week} 06:00 KST`} onBack={onClose}
        summary={
          <div className="chips">
            <span className="chip">총 신호 <span className="n">14</span></span>
            <span className="chip" style={{ background: "var(--sig-pos-bg)", borderColor: "var(--sig-pos-bg)", color: "var(--sig-pos)" }}>성공 <span className="n">{c.summary.success}</span></span>
            <span className="chip">신규 데이터 <span className="n">{c.summary.newCount.toLocaleString()}</span></span>
            <span className="chip">실패 <span className="n">{c.summary.fail}</span></span>
          </div>
        }
      />

      <Tabs
        active={tab} onChange={setTab}
        tabs={[
          { id: "A", code: "Group A", label: "정형 (7종)" },
          { id: "B", code: "Group B", label: "비정형 (7종)" },
        ]}
      />

      <div className="card" style={{ padding: 0 }}>
        <table className="tbl">
          <thead>
            <tr>
              <th style={{ width: 60 }}>ID</th>
              <th>신호명</th>
              <th>수집 출처</th>
              <th>수집 일시</th>
              <th className="num">신규 건수</th>
              <th className="num">전주 대비</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            {items.map(r => (
              <tr key={r.id}>
                <td className="mono muted">{r.id}</td>
                <td style={{ fontWeight: 500 }}>{r.name}</td>
                <td className="muted">{r.source}</td>
                <td className="mono muted" style={{ fontSize: 11 }}>{r.time}</td>
                <td className="num" style={{ fontWeight: 600 }}>{r.newItems.toLocaleString()}</td>
                <td className="num">
                  <span className={`arr ${r.newItems > r.prev ? "up" : r.newItems < r.prev ? "dn" : "flat"}`}>
                    {r.newItems > r.prev ? "↑" : r.newItems < r.prev ? "↓" : "↔"}
                  </span>
                  <span style={{ marginLeft: 6 }}>{r.newItems === r.prev ? "0" : `${r.newItems > r.prev ? "+" : ""}${r.newItems - r.prev}`}</span>
                </td>
                <td><span className={`status-pill ${r.status === "ok" ? "ok" : r.status === "fail" ? "fail" : "warn"}`}>
                  {r.status === "ok" ? "✓ 성공" : r.status === "fail" ? "✕ 실패" : "⚠ 부분"}
                </span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 22, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div className="card">
          <div className="dlabel">다음 수집 일정</div>
          <div className="num" style={{ fontSize: 18, fontWeight: 600, marginTop: 4 }}>{formatTuesdayKST(nextTuesday06KST())}</div>
          <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>매주 화요일 새벽 6시 자동 실행. 14개 신호 일제 갱신 + 모델 재학습 트리거.</div>
        </div>
        <div className="card">
          <div className="dlabel">수집 안정성</div>
          <div className="num" style={{ fontSize: 18, fontWeight: 600, marginTop: 4, color: "var(--sig-pos)" }}>최근 8주 100% 성공</div>
          <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>외부 API 장애 시 자동 재시도 3회, 부분 실패 시 직전 주 값으로 보간.</div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { S006, S008, S010, S012, S014 });


export { PageHead, S006, S008, S010, S012, S014 }
