import React, { useState, useEffect, useRef, useMemo, useCallback, Fragment } from 'react'
import { SIXSENSE_DATA } from '../mocks/data.js'
import { Sig, Tabs, LineChart } from '../components/components.jsx'
// USER-REQUESTED EXTENSION (#16) — 다음 수집 일정 동적 계산
import { nextTuesday06KST, formatTuesdayKST } from '../utils/dates.js'

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
          <option value="conf">정렬: AI 확신도순</option>
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
              <th className="num" style={{ width: 80 }}>AI 감성</th>
              <th style={{ width: 80 }}>판정</th>
              <th className="num" style={{ width: 96 }}>AI 확신도</th>
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

    </div>
  );
}

// ==== S-008 Macro indicators ====
// 출처·날짜·이력은 모두 수집 파일에서 온 값. 고정 해설 문장(이전: '구리 +8.3%, 10주 후 DRAM 6~8% 상승' 등) 삭제.
function fmtMacro(v, unit) {
  if (unit === "원") return v.toLocaleString(undefined, { maximumFractionDigits: 0 });
  if (unit === "%") return `${v.toFixed(2)}%`;
  if (unit === "$") return `$${v.toFixed(2)}`;
  return v.toFixed(2);
}

function S008({ tab: initialTab, onClose }) {
  const [tab, setTab] = useState(initialTab || D3.macro[0].id);
  const m = D3.macro.find(x => x.id === tab) || D3.macro[0];
  const rows = m.recent || [];
  const n = rows.length;

  return (
    <div className="content">
      <PageHead num="S-008" icon="◔" title="거시경제 지표 상세" sub="수집된 값 그대로 — 해석 문장 없음" onBack={onClose} />

      <Tabs active={m.id} onChange={setTab} tabs={D3.macro.map(x => ({ id: x.id, label: x.name }))} />

      {m.stale && (
        <div className="banner">갱신 중단 — {m.staleReason}. 현재 상황 판단에 쓰지 마세요.</div>
      )}

      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginBottom: 22 }}>
        <div style={{ flex: "1 1 140px" }}>
          <div className="dlabel">최신값 ({m.asOf})</div>
          <div className="num" style={{ fontSize: 28, fontWeight: 600 }}>{m.value}</div>
        </div>
        <div style={{ flex: "1 1 180px" }}>
          <div className="dlabel">4주 변화 (규칙 기반 표시)</div>
          <div style={{ marginTop: 6 }}>{m.stale ? <Sig tone="alert" size="lg">갱신 중단</Sig> : <Sig tone={m.tone} size="lg">{m.change}</Sig>}</div>
        </div>
        <div style={{ flex: "1 1 180px" }}>
          <div className="dlabel">설명</div>
          <div style={{ marginTop: 4, fontSize: 12 }}>{m.desc}</div>
        </div>
        <div style={{ flex: "1 1 180px" }}>
          <div className="dlabel">수집 출처</div>
          <div className="mono" style={{ marginTop: 4, fontSize: 12 }}>{m.source || "—"}</div>
        </div>
      </div>

      <div className="dlabel" style={{ marginBottom: 8 }}>최근 {n}주 추이 (주간)</div>
      <div className="card">
        {n > 1 ? (
          <LineChart
            width={1200} height={240}
            series={[{ data: rows.map((r, i) => ({ x: i - (n - 1), value: r.value })), color: "var(--text)" }]}
            xLabels={[{ x: -(n - 1), label: rows[0].week }, { x: 0, label: rows[n - 1].week }]}
          />
        ) : <div className="muted" style={{ fontSize: 12 }}>표시할 이력이 없습니다.</div>}
      </div>

      <div className="dlabel" style={{ margin: "22px 0 8px" }}>최근 관측값 (최신 8주)</div>
      <table className="tbl">
        <thead><tr><th>주</th><th className="num">{m.name}</th></tr></thead>
        <tbody>
          {rows.slice(-8).reverse().map(r => (
            <tr key={r.week}>
              <td className="mono">{r.week}</td>
              <td className="num" style={{ fontWeight: 600 }}>{fmtMacro(r.value, m.unit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
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

    </div>
  );
}

// ==== S-012 AI 가격 예측 검증 상세 (honest_backtest.py) ====
function S012({ onClose }) {
  const v = D3.validation;
  if (!v) {
    return (
      <div className="content">
        <PageHead num="S-012" icon="▤" title="AI 가격 예측 검증" onBack={onClose} />
        <div className="card muted" style={{ fontSize: 12 }}>검증 결과가 아직 없습니다.</div>
      </div>
    );
  }
  return (
    <div className="content">
      <PageHead num="S-012" icon="▤" title="AI 가격 예측 검증" sub={`워크포워드 백테스트 · ${v.runAt} 실행 · ${v.dataRange[0]} ~ ${v.dataRange[1]} (${v.dataWeeks}주)`} onBack={onClose}
        summary={<Sig tone={v.pass ? "pos" : "neg"} size="lg">{v.pass ? "✅ 합격" : "❌ 불합격"}</Sig>}
      />

      <div className="card" style={{ marginBottom: 18, fontSize: 12.5, lineHeight: 1.7 }}>
        <div><strong>예측 대상</strong> · {v.target}</div>
        <div><strong>비교 기준</strong> · {v.baseline}</div>
        <div><strong>합격 기준</strong> · {v.passRule}</div>
        <div style={{ marginTop: 8 }}><strong>방법</strong></div>
        <ul style={{ margin: "4px 0 0 18px", padding: 0 }}>
          {v.method.map((t, i) => <li key={i}>{t}</li>)}
        </ul>
      </div>

      {v.variants.map(x => {
        const o = x.overall, pr = x.procurement;
        return (
          <div key={x.key} style={{ marginBottom: 22 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div className="dlabel" style={{ margin: 0 }}>{x.name}</div>
              <Sig tone={x.pass ? "pos" : "neg"}>{x.pass ? "합격" : "불합격"}</Sig>
            </div>
            <div className="card" style={{ padding: 0 }}>
              <table className="tbl">
                <thead>
                  <tr><th>예측 기간</th><th className="num">예측 수</th><th className="num">모델 오차</th><th className="num">기준선 오차</th><th className="num">기준선을 이긴 비율</th><th className="num">방향 적중률</th></tr>
                </thead>
                <tbody>
                  {x.byHorizon.map(h => (
                    <tr key={h.h}>
                      <td>{h.h}주 뒤</td>
                      <td className="num">{h.n}</td>
                      <td className="num" style={{ fontWeight: 600 }}>{h.modelMape.toFixed(2)}%</td>
                      <td className="num">{h.naiveMape.toFixed(2)}%</td>
                      <td className="num">{h.winRate.toFixed(0)}%</td>
                      <td className="num">{h.dirAcc.toFixed(0)}%</td>
                    </tr>
                  ))}
                  <tr style={{ fontWeight: 600 }}>
                    <td>전체</td><td className="num">{o.n}</td>
                    <td className="num">{o.modelMape.toFixed(2)}%</td><td className="num">{o.naiveMape.toFixed(2)}%</td>
                    <td className="num">{o.winRate.toFixed(0)}%</td><td className="num">{o.dirAcc.toFixed(0)}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="muted" style={{ fontSize: 11.5, marginTop: 8, lineHeight: 1.7 }}>
              우연히 이 정도로 이길 확률 p = {o.pValue} · '항상 오른다'고 찍었을 때 방향 적중률 {o.alwaysUpDirAcc.toFixed(0)}% ·
              {" "}{pr.horizonWeeks}주 대기 여부를 모델대로 정했을 때 평균 구매 단가 {pr.modelPct > 0 ? "+" : ""}{pr.modelPct.toFixed(2)}%
              (대기 신호 {pr.waitCount}회 중 실제로 옳았던 경우 {pr.waitCorrect}회, 미래를 안다면 {pr.perfectPct.toFixed(2)}%)
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ==== S-014 Collection status ====
function S014({ onClose }) {
  const [tab, setTab] = useState("A");
  const c = D3.collection;
  const items = tab === "A" ? c.groupA : c.groupB;
  const stale = [...c.groupA, ...c.groupB].filter(r => r.status !== "ok");
  const label = (st) => (st === "ok" ? "✓ 정상" : st === "stale" ? "⚠ 갱신 중단" : "✕ 실패");

  return (
    <div className="content">
      <PageHead num="S-014" icon="▤" title="데이터 수집 현황" sub={`기준일 ${c.week} · ${c.staleDays}일 넘게 수집이 없거나, 같은 값이 8주 이상 이어지면 '갱신 중단'`} onBack={onClose}
        summary={
          <div className="chips">
            <span className="chip">전체 <span className="n">{c.summary.total}</span></span>
            <span className="chip" style={{ background: "var(--sig-pos-bg)", borderColor: "var(--sig-pos-bg)", color: "var(--sig-pos)" }}>정상 <span className="n">{c.summary.success}</span></span>
            <span className="chip">갱신 중단 <span className="n">{c.summary.stale}</span></span>
            <span className="chip">실패 <span className="n">{c.summary.fail}</span></span>
          </div>
        }
      />

      <Tabs
        active={tab} onChange={setTab}
        tabs={[
          { id: "A", code: "Group A", label: `정형 (${c.groupA.length}종)` },
          { id: "B", code: "Group B", label: `비정형 (${c.groupB.length}종)` },
        ]}
      />

      <div className="card" style={{ padding: 0 }}>
        <table className="tbl">
          <thead>
            <tr><th style={{ width: 60 }}>ID</th><th>신호명</th><th>수집 출처</th><th>마지막 수집일</th><th className="num">데이터(주)</th><th>상태</th></tr>
          </thead>
          <tbody>
            {items.map(r => (
              <tr key={r.id}>
                <td className="mono muted">{r.id}</td>
                <td style={{ fontWeight: 500 }}>{r.name}</td>
                <td className="muted">{r.source}</td>
                <td className="mono muted" style={{ fontSize: 11 }}>{r.time}</td>
                <td className="num" style={{ fontWeight: 600 }}>{r.weeks}</td>
                <td>
                  <span className={`status-pill ${r.status === "ok" ? "ok" : r.status === "fail" ? "fail" : "warn"}`}>{label(r.status)}</span>
                  {r.reason && <div className="muted" style={{ fontSize: 10.5, marginTop: 4 }}>{r.reason}</div>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 22, display: "flex", flexWrap: "wrap", gap: 16 }}>
        <div className="card" style={{ flex: "1 1 240px" }}>
          <div className="dlabel">다음 자동 수집</div>
          <div className="num" style={{ fontSize: 18, fontWeight: 600, marginTop: 4 }}>{formatTuesdayKST(nextTuesday06KST())}</div>
          <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>매주 화요일 06:00 — 신호 수집 · 예측 검증 · AI 요약 · 배포.</div>
        </div>
        <div className="card" style={{ flex: "1 1 240px" }}>
          <div className="dlabel">수집이 멈춘 신호</div>
          <div className="num" style={{ fontSize: 18, fontWeight: 600, marginTop: 4, color: stale.length ? "var(--sig-alert)" : "var(--sig-pos)" }}>
            {stale.length ? `${stale.length}개` : "없음"}
          </div>
          <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>
            {stale.length ? stale.map(r => `${r.id} ${r.name}`).join(" · ") : "모든 신호가 최신입니다."}
            {" "}수집에 실패하면 자동 재시도 없이 직전 값을 유지합니다.
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { S006, S008, S010, S012, S014 });


export { PageHead, S006, S008, S010, S012, S014 }
