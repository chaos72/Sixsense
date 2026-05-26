import React, { useState, useEffect, useRef, useMemo, useCallback, Fragment } from 'react'
import { SIXSENSE_DATA } from '../mocks/data.js'
import { Sig, Sparkline, Modal, MetricCard, Tabs, Seg, HITL, HITL_DEFAULT_RULES, AiNote, BarRow, LineChart, FilterSelect, SectionHead } from '../components/components.jsx'
// USER-REQUESTED EXTENSION (#16) — 생성일 동적
import { lastTuesday06KST, formatTuesdayShort } from '../utils/dates.js'

// Modal-based detail screens: S-002, S-003, S-004, S-005, S-007, S-009, S-011, S-013
const D2 = SIXSENSE_DATA;

// ==== S-002 AI 예측 근거 ====
function S002({ horizon: initialHorizon, onClose, onNav }) {
  const [tab, setTab] = useState(initialHorizon === 21 ? "21" : "7");
  const isH7 = tab === "7";
  const data = isH7 ? D2.forecast7 : D2.forecast21;
  const finalVal = data[data.length - 1];
  
  const contributions = isH7 ? [
    { rank: 1, code: "A-2", label: "빅테크 CapEx 급증", pct: 28, tone: "pos" },
    { rank: 2, code: "B-1", label: "Earnings Call 긍정", pct: 22, tone: "pos" },
    { rank: 3, code: "A-7", label: "구리가격 선행 상승", pct: 18, tone: "pos" },
    { rank: 4, code: "A-1", label: "대만 공급망 강세", pct: 14, tone: "pos" },
    { rank: 5, code: "A-4", label: "재고지수 Red Alert", pct: -10, tone: "neg" },
    { rank: 6, code: "B-4", label: "지정학 리스크", pct: -8, tone: "neg" },
    { rank: 7, code: "—", label: "기타 8개 신호", pct: 4, tone: "neu" },
  ] : [
    { rank: 1, code: "A-7", label: "구리 선행 효과 누적", pct: 32, tone: "pos" },
    { rank: 2, code: "A-2", label: "빅테크 CapEx (장기)", pct: 24, tone: "pos" },
    { rank: 3, code: "B-5", label: "LTA 비율 상승", pct: 19, tone: "pos" },
    { rank: 4, code: "B-1", label: "Earnings Call 가이던스", pct: 15, tone: "pos" },
    { rank: 5, code: "B-4", label: "지정학 리스크", pct: -12, tone: "neg" },
    { rank: 6, code: "A-4", label: "공급과잉 압력", pct: -8, tone: "neg" },
    { rank: 7, code: "—", label: "기타 8개 신호", pct: 6, tone: "neu" },
  ];

  return (
    <Modal title="AI 예측 근거 상세" badge="S-002" size="lg" onClose={onClose}>
      <div className="modal-body">
        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            { id: "7", code: "1~7주", label: "단기 예측" },
            { id: "21", code: "8~21주", label: "중장기 예측" },
          ]}
        />
        
        {/* Top summary */}
        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 1fr 1fr", gap: 16, marginBottom: 22 }}>
          <div>
            <div className="dlabel">예측값</div>
            <div className="num" style={{ fontSize: 28, fontWeight: 600 }}>${finalVal.value.toFixed(2)}</div>
            <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>+{isH7 ? "7" : "21"}주 시점 기준</div>
          </div>
          <div>
            <div className="dlabel">신뢰 구간</div>
            <div className="num" style={{ fontSize: 14, fontWeight: 600, marginTop: 4 }}>${finalVal.lower.toFixed(2)} ─ ${finalVal.upper.toFixed(2)}</div>
            <ConfidenceBar lower={finalVal.lower} value={finalVal.value} upper={finalVal.upper} />
          </div>
          <div>
            <div className="dlabel">생성일 · 모델</div>
            <div style={{ fontSize: 13, fontWeight: 500, marginTop: 4 }}>{formatTuesdayShort(lastTuesday06KST())}</div>
            <div className="mono muted" style={{ fontSize: 11 }}>prophet_v2.1</div>
          </div>
          <div>
            <div className="dlabel">신뢰도</div>
            <div className="num" style={{ fontSize: 28, fontWeight: 600, color: "var(--sig-pos)" }}>{isH7 ? 81 : 74}%</div>
          </div>
        </div>

        {/* Contribution bars */}
        <div className="dlabel" style={{ marginBottom: 8 }}>신호별 예측 기여도 (순위순)</div>
        <div className="card" style={{ padding: "12px 18px" }}>
          {contributions.map(c => <BarRow key={c.rank} {...c} />)}
        </div>

        {/* Weekly table */}
        <div className="dlabel" style={{ margin: "22px 0 8px" }}>주별 예측값 테이블</div>
        <table className="tbl">
          <thead>
            <tr>
              <th>주차</th>
              <th className="num">예측값</th>
              <th className="num">신뢰구간 하단</th>
              <th className="num">신뢰구간 상단</th>
              <th>구간 폭</th>
            </tr>
          </thead>
          <tbody>
            {data.map(d => (
              <tr key={d.week}>
                <td>+{d.week}주</td>
                <td className="num" style={{ fontWeight: 600 }}>${d.value.toFixed(2)}</td>
                <td className="num muted">${d.lower.toFixed(2)}</td>
                <td className="num muted">${d.upper.toFixed(2)}</td>
                <td className="muted mono" style={{ fontSize: 11 }}>±{((d.upper - d.lower) / 2).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* AI judgment */}
        <div style={{ marginTop: 22 }}>
          <AiNote>
            {isH7 ?
              `"수요 측 신호(CapEx·실적콜)가 강하게 긍정적. 구리 선행지표도 6주 연속 상승세로 후행 효과 본격 반영 예상. 재고과잉 경고(A-4 Red Alert)가 하방 리스크이나 전반적 상승 압력 우세. 단, 지정학 리스크(B-4) 악화 모니터링 필요."` :
              `"중장기는 구리 선행효과의 풀(full) 반영과 빅테크 CapEx 실행이 본격화되는 구간. LTA 비율 상승이 확인되며 메모리 4사 가이던스도 동조. 단, 지정학 리스크의 누적 효과와 중국 자급화 진척이 변수. 신뢰도 74%로 단기 대비 다소 낮음."`
            }
          </AiNote>
        </div>

        <div style={{ marginTop: 22 }}>
          <HITL rules={HITL_DEFAULT_RULES} />
        </div>
      </div>
    </Modal>
  );
}

function ConfidenceBar({ lower, value, upper }) {
  const min = lower * 0.98, max = upper * 1.02;
  const pos = (v) => ((v - min) / (max - min)) * 100;
  return (
    <div style={{ marginTop: 8, height: 6, background: "var(--surface-2)", borderRadius: 3, position: "relative" }}>
      <div style={{ position: "absolute", left: `${pos(lower)}%`, width: `${pos(upper) - pos(lower)}%`, height: "100%", background: "var(--sig-info-bg)", borderRadius: 3 }}></div>
      <div style={{ position: "absolute", left: `${pos(value)}%`, top: -3, width: 2, height: 12, background: "var(--accent)", transform: "translateX(-50%)" }}></div>
    </div>
  );
}

// ==== S-003 Group A 정형 ====
function S003({ tab: initialTab, onClose, onNav }) {
  const [tab, setTab] = useState(initialTab || "A-1");
  const s = D2.signalsA.find(x => x.id === tab);
  
  return (
    <Modal title="정형 데이터 (Group A) 통합 상세" badge="S-003" size="lg" onClose={onClose}>
      <div className="modal-body">
        <Tabs
          active={tab} onChange={setTab}
          tabs={D2.signalsA.map(s => ({ id: s.id, code: s.id, label: s.name }))}
        />
        <SignalDetail s={s} groupType="A" onNav={onNav} />
        <div style={{ marginTop: 22 }}>
          <HITL rules={HITL_DEFAULT_RULES} />
        </div>
      </div>
    </Modal>
  );
}

// ==== S-004 Group B 비정형 ====
function S004({ tab: initialTab, onClose, onNav }) {
  const [tab, setTab] = useState(initialTab || "B-1");
  const s = D2.signalsB.find(x => x.id === tab);
  
  return (
    <Modal title="비정형 데이터 (Group B) 통합 상세" badge="S-004" size="lg" onClose={onClose}>
      <div className="modal-body">
        <Tabs
          active={tab} onChange={setTab}
          tabs={D2.signalsB.map(s => ({ id: s.id, code: s.id, label: s.name }))}
        />
        <SignalDetail s={s} groupType="B" onNav={onNav} />
        <div style={{ marginTop: 22 }}>
          <HITL rules={HITL_DEFAULT_RULES} />
        </div>
      </div>
    </Modal>
  );
}

function SignalDetail({ s, groupType, onNav }) {
  // Generate 28-week trend
  const trend = useMemo(() => {
    const base = s.spark;
    const out = [];
    for (let i = 0; i < 28; i++) {
      const idx = (i / 27) * (base.length - 1);
      const a = base[Math.floor(idx)], b = base[Math.ceil(idx)];
      const v = a + (b - a) * (idx - Math.floor(idx));
      out.push({ x: i - 27, value: v + (Math.sin(i * 2.3) * 0.02) });
    }
    return out;
  }, [s.id]);

  const isAlert = s.tone === "alert";
  
  // News samples for group B
  const sampleNews = D2.news.slice(0, 3);

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 0.8fr 0.8fr", gap: 16, marginBottom: 18, alignItems: "flex-end" }}>
        <div>
          <div className="dlabel">신호명</div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>{s.name}</div>
          <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>{s.desc}</div>
        </div>
        <div>
          <div className="dlabel">현재값</div>
          <div className="num" style={{ fontSize: 26, fontWeight: 600 }}>{s.value}</div>
        </div>
        <div>
          <div className="dlabel">판정</div>
          <Sig tone={s.tone} size="lg">
            {s.tone === "alert" ? "🚨 Red Alert" : s.tone === "pos" ? "긍정" : s.tone === "neg" ? "부정" : "중립"}
          </Sig>
          {isAlert && <div style={{ fontSize: 11, color: "var(--sig-alert)", marginTop: 4 }}>100 초과 = 공급과잉</div>}
        </div>
        <div>
          <div className="dlabel">수집</div>
          <div style={{ fontSize: 12, fontWeight: 500 }}>{s.source}</div>
          <div className="muted mono" style={{ fontSize: 10, marginTop: 2 }}>갱신: {groupType === "A" ? "주 1회" : "일 1회 (집계 주 1회)"}</div>
        </div>
      </div>

      {isAlert && (
        <div className="banner">
          🚨 Red Alert — 재고/출하 비율이 임계치(100)를 초과했습니다. 단기 가격 하방 압력 예상.
        </div>
      )}

      <div className="dlabel" style={{ marginBottom: 8 }}>{groupType === "A" ? "28주 추이" : "8주 감성 점수 추이"}</div>
      <div className="card">
        <LineChart
          width={1000} height={220}
          series={[{ data: trend.slice(groupType === "A" ? 0 : 20), color: s.tone === "alert" || s.tone === "neg" ? "var(--sig-neg)" : s.tone === "pos" ? "var(--sig-pos)" : "var(--sig-neu)", dots: groupType !== "A" }]}
          refLines={isAlert ? [{ value: 100, label: "경고선 100", color: "var(--sig-alert)" }] : []}
          xLabels={groupType === "A" ?
            [{ x: -27, label: "28주전" }, { x: -14, label: "14주전" }, { x: 0, label: "현재" }] :
            [{ x: -7, label: "8주전" }, { x: -3, label: "4주전" }, { x: 0, label: "현재" }]
          }
        />
      </div>

      {/* Original data or news list */}
      {groupType === "A" ? (
        <div style={{ marginTop: 18 }}>
          <div className="dlabel" style={{ marginBottom: 8 }}>원본 데이터 (최근 4개월)</div>
          <table className="tbl">
            <thead>
              <tr>
                <th>월</th>
                <th className="num">{s.id === "A-4" ? "재고지수" : "값"}</th>
                {s.id === "A-4" && <><th className="num">출하지수</th><th className="num">비율</th></>}
                <th>판정</th>
              </tr>
            </thead>
            <tbody>
              {[{m:"2026-04",a:108.2,b:105.7,r:102.4,tone:"alert"},{m:"2026-03",a:104.5,b:103.8,r:100.7,tone:"neu"},{m:"2026-02",a:98.3,b:101.2,r:97.1,tone:"pos"},{m:"2026-01",a:94.1,b:99.8,r:94.3,tone:"pos"}].map(row => (
                <tr key={row.m}>
                  <td className="mono">{row.m}</td>
                  <td className="num">{s.id === "A-4" ? row.a.toFixed(1) : (Math.random() * 100).toFixed(2)}</td>
                  {s.id === "A-4" && <><td className="num">{row.b.toFixed(1)}</td><td className="num" style={{ fontWeight: 600 }}>{row.r.toFixed(1)}</td></>}
                  <td><Sig tone={row.tone}>{row.tone === "alert" ? "🚨 Red Alert" : row.tone === "pos" ? "정상" : "주의"}</Sig></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ marginTop: 18 }}>
          <div className="dlabel" style={{ marginBottom: 8 }}>이번 주 주요 탐지 뉴스 · 점수 상위</div>
          <div className="card" style={{ padding: 0 }}>
            {sampleNews.map((n, i) => (
              <div key={i} className="tappable" onClick={() => onNav("S-007", { news: n })}
                style={{ padding: "12px 16px", borderBottom: i < sampleNews.length - 1 ? "1px solid var(--border)" : "none", display: "grid", gridTemplateColumns: "auto 1fr auto auto", gap: 12, alignItems: "center", fontSize: 12.5, cursor: "pointer" }}>
                <Sig tone={n.tone}>{n.tone === "pos" ? "긍정" : n.tone === "neg" ? "부정" : "중립"}</Sig>
                <div>
                  <div style={{ fontWeight: 500 }}>{n.title}</div>
                  <div className="muted mono" style={{ fontSize: 10, marginTop: 2 }}>{n.titleEn}</div>
                </div>
                <span className="muted mono" style={{ fontSize: 11 }}>{n.source} · {n.date}</span>
                <span className="num" style={{ fontWeight: 600, color: n.tone === "pos" ? "var(--sig-pos)" : "var(--sig-neg)" }}>{n.score > 0 ? "+" : ""}{n.score.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 18 }}>
        <AiNote label="AI 해석">
          {s.id === "A-4" ? `"재고가 출하를 초과하며 비율이 ${s.value}로 상승. 단기 가격 하방 압력 예상. 3개월 내 조정 가능성 주시 필요. 다만 A-2 CapEx·B-1 실적콜의 강한 긍정 신호와 결합 시 일시적 조정 후 재상승 시나리오 우세."` :
            `"${s.name} 신호 ${s.tone === "pos" ? "긍정 강세" : s.tone === "neg" ? "부정 압력" : "중립적 흐름"}. 8주 전 대비 ${Math.abs((s.spark[s.spark.length-1] - s.spark[0]) * 100).toFixed(0)}p 변화. 다른 14개 신호와의 정합성 검토 필요."`}
        </AiNote>
      </div>

      {s.id === "A-7" && (
        <div style={{ marginTop: 14, display: "flex", justifyContent: "flex-end" }}>
          <button className="btn primary" onClick={() => onNav("S-005")}>
            🔍 Graph RAG 구리↔DRAM 전체 분석 →
          </button>
        </div>
      )}
    </div>
  );
}

// ==== S-005 Graph RAG ====
function S005({ onClose }) {
  return (
    <Modal title="Graph RAG — 구리 vs 서버 DRAM 상관관계" badge="S-005" size="lg" onClose={onClose}>
      <div className="modal-body">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 22 }}>
          <div>
            <div className="dlabel">분석 기간</div>
            <div className="num" style={{ fontSize: 22, fontWeight: 600 }}>52주</div>
          </div>
          <div>
            <div className="dlabel">상관계수</div>
            <div className="num" style={{ fontSize: 22, fontWeight: 600, color: "var(--sig-pos)" }}>+0.72</div>
          </div>
          <div>
            <div className="dlabel">최적 선행 시차</div>
            <div className="num" style={{ fontSize: 22, fontWeight: 600 }}>10주</div>
          </div>
        </div>

        <div className="dlabel" style={{ marginBottom: 8 }}>구리(파란) vs DRAM(검정) — 104주 오버레이</div>
        <div className="card">
          <LineChart
            width={1200} height={240}
            series={[
              { data: Array.from({length: 26}, (_,i) => ({ x: i, value: 0.3 + Math.sin(i*0.3)*0.15 + i*0.018 })), color: "var(--sig-info)", endLabel: "구리 (선행 10주)" },
              { data: Array.from({length: 26}, (_,i) => ({ x: i, value: 0.2 + Math.sin((i-5)*0.3)*0.12 + i*0.013 })), color: "var(--text)", endLabel: "DRAM" },
            ]}
            xLabels={[
              { x: 0, label: "104주전" }, { x: 13, label: "52주전" }, { x: 20, label: "26주전" }, { x: 25, label: "현재" }
            ]}
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.2fr", gap: 22, marginTop: 22 }}>
          <div>
            <div className="dlabel" style={{ marginBottom: 8 }}>선행 시차별 상관계수</div>
            <div className="card" style={{ padding: "12px 18px" }}>
              {[{l:"4주",v:0.51},{l:"6주",v:0.64},{l:"8주",v:0.69},{l:"10주",v:0.72,best:true},{l:"12주",v:0.68},{l:"16주",v:0.55}].map(r => (
                <div key={r.l} style={{ display: "grid", gridTemplateColumns: "50px 1fr 60px", gap: 10, alignItems: "center", padding: "6px 0", fontSize: 12 }}>
                  <span className="mono">{r.l}</span>
                  <div className="bar-track" style={{ height: 12 }}>
                    <div className={r.best ? "pos" : "neu"} style={{ width: `${r.v * 100}%`, opacity: r.best ? 1 : 0.55 }}></div>
                  </div>
                  <span className="num" style={{ textAlign: "right", fontWeight: r.best ? 700 : 500, color: r.best ? "var(--sig-pos)" : "var(--text)" }}>
                    +{r.v.toFixed(2)}{r.best ? " ◀" : ""}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div className="dlabel" style={{ marginBottom: 8 }}>인과관계 경로</div>
            <div className="card">
              <div className="path">
                <div className="path-node" style={{ background: "var(--sig-info-bg)", borderColor: "var(--sig-info)", color: "var(--sig-info)", fontWeight: 600 }}>
                  <span>구리 가격 상승 (LME)</span>
                  <span className="mono">+8.3%</span>
                </div>
                <div className="path-branch">
                  <div className="path-node" style={{ marginTop: 8 }}>
                    <span>① PCB 기판 원가 상승</span>
                    <span className="mono muted">4~6주 · 기여도 42%</span>
                  </div>
                  <div className="path-node" style={{ marginTop: 6 }}>
                    <span>② 반도체 패키징 비용 상승</span>
                    <span className="mono muted">6~8주 · 기여도 31%</span>
                  </div>
                  <div className="path-node" style={{ marginTop: 6 }}>
                    <span>③ 데이터센터 투자 비용 증가</span>
                    <span className="mono muted">8~12주 · 기여도 27%</span>
                  </div>
                </div>
                <div className="path-node" style={{ marginTop: 8, background: "var(--surface-2)", fontWeight: 600 }}>
                  <span>↓ DRAM 가격 변동</span>
                  <span className="mono" style={{ color: "var(--sig-pos)" }}>+6~8% (10주 후)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 22 }}>
          <AiNote label="현재 시사점" source="Claude · Graph RAG">
            "구리 $4.82 (+8.3%, 6주 연속 상승). PCB·패키징·DC 투자 3중 경로로 약 10주 후 DRAM 가격에 6~8% 상승 압력 전달 예상. 신뢰도 74%. 단, 동일 기간 빅테크 CapEx·실적콜 강세와 중첩되어 실측 영향은 더 클 수 있음."
          </AiNote>
        </div>
      </div>
    </Modal>
  );
}

// ==== S-007 News detail ====
function S007({ news, onClose, onNav }) {
  const n = news;
  return (
    <Modal title="뉴스 원문 & AI 분석 상세" badge="S-007" size="lg" onClose={onClose}>
      <div className="modal-body">
        <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 6 }}>
          <Sig tone={n.tone} size="lg">{n.tone === "pos" ? "긍정" : n.tone === "neg" ? "부정" : "중립"}</Sig>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-0.01em", lineHeight: 1.4 }}>{n.title}</div>
            <div className="muted mono" style={{ fontSize: 11, marginTop: 4 }}>{n.titleEn}</div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 16, fontSize: 11, color: "var(--text-dim)", marginBottom: 18 }}>
          <span><span className="muted">출처</span> <strong className="mono" style={{ color: "var(--text)" }}>{n.source}</strong></span>
          <span><span className="muted">발행</span> <span className="mono">{n.date}</span></span>
          <span><span className="muted">감성 점수</span> <span className="num" style={{ color: n.tone === "pos" ? "var(--sig-pos)" : "var(--sig-neg)", fontWeight: 600 }}>{n.score > 0 ? "+" : ""}{n.score.toFixed(2)}</span></span>
          <span><span className="muted">신뢰도</span> <span className="num">{n.conf}%</span></span>
        </div>

        <AiNote label="AI 요약 · Claude 자동 생성">{n.summary || "—"}</AiNote>

        {n.effects && (
          <div style={{ marginTop: 22 }}>
            <div className="dlabel" style={{ marginBottom: 8 }}>DRAM 가격 영향 분석</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
              {[{k:"short",l:"단기 (1~7주)"},{k:"mid",l:"중장기 (8~21주)"},{k:"long",l:"장기 (22주~)"}].map(p => {
                const e = n.effects[p.k];
                return (
                  <div key={p.k} className="card">
                    <div className="dlabel">{p.l}</div>
                    <div style={{ marginTop: 6, marginBottom: 8 }}><Sig tone={e.tone} size="lg">{e.tone === "pos" ? "긍정" : e.tone === "neg" ? "부정" : "중립"}</Sig></div>
                    <div style={{ fontSize: 12, color: "var(--text-mid)" }}>{e.text}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {n.linked && (
          <div style={{ marginTop: 22 }}>
            <div className="dlabel" style={{ marginBottom: 8 }}>연결된 신호</div>
            <div className="card" style={{ padding: "10px 14px" }}>
              {n.linked.map((l, i) => (
                <div key={i} style={{ padding: "4px 0", fontSize: 12.5 }}>· {l}</div>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginTop: 22, display: "flex", justifyContent: "flex-end" }}>
          <button className="btn primary">
            🌐 원문 기사 열기 →
          </button>
        </div>

        <div style={{ marginTop: 22 }}>
          <HITL rules={HITL_DEFAULT_RULES} />
        </div>
      </div>
    </Modal>
  );
}

// ==== S-009 Weekly snapshot ====
function S009({ week, onClose }) {
  const sp = D2.snapshotPast;
  const isFuture = week > 0;
  
  if (isFuture) {
    // Future week — show prediction breakdown
    const isF7 = week <= 7;
    const data = isF7 ? D2.forecast7.find(d => d.week === week) : D2.forecast21.find(d => d.week === week);
    if (!data) return null;
    return (
      <Modal title={`주별 신호 스냅샷 · +${week}주 예측`} badge="S-009" onClose={onClose}>
        <div className="modal-body">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 22 }}>
            <div><div className="dlabel">예측가</div><div className="num" style={{ fontSize: 26, fontWeight: 600 }}>${data.value.toFixed(2)}</div></div>
            <div><div className="dlabel">신뢰구간</div><div className="num" style={{ fontSize: 14, fontWeight: 500, marginTop: 6 }}>${data.lower.toFixed(2)} ─ ${data.upper.toFixed(2)}</div></div>
            <div><div className="dlabel">기여도 상위</div><div style={{ marginTop: 6, display: "flex", gap: 6 }}><Sig tone="pos">A-2 CapEx</Sig><Sig tone="pos">B-1 실적콜</Sig><Sig tone="pos">A-7 구리</Sig></div></div>
          </div>
          <AiNote>
            +{week}주 시점 예측은 CapEx 확장의 후행 효과와 구리 선행지표의 누적 반영이 주된 상승 동력. 단, 지정학 변수에 따라 신뢰구간이 넓어질 수 있음.
          </AiNote>
        </div>
      </Modal>
    );
  }
  
  // Past week — show signal snapshot
  return (
    <Modal title={`주별 신호 스냅샷 — ${sp.date} (화)`} badge="S-009" size="lg" onClose={onClose}>
      <div className="modal-body">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 16, marginBottom: 22 }}>
          <div><div className="dlabel">실제가</div><div className="num" style={{ fontSize: 22, fontWeight: 600 }}>${sp.actual.toFixed(2)}</div></div>
          <div><div className="dlabel">당시 예측값</div><div className="num" style={{ fontSize: 22, fontWeight: 600 }}>${sp.predicted.toFixed(2)}</div></div>
          <div><div className="dlabel">오차</div><div className="num" style={{ fontSize: 22, fontWeight: 600, color: "var(--sig-neu)" }}>+{sp.error.toFixed(1)}%</div></div>
          <div><div className="dlabel">판정</div><div style={{ marginTop: 6 }}><Sig tone="neu" size="lg">중립 — 허용 오차 내</Sig></div></div>
        </div>
        
        <div className="dlabel" style={{ marginBottom: 8 }}>해당 시점 14개 신호 상태</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <div>
            <div className="muted" style={{ fontSize: 11, fontWeight: 600, marginBottom: 6 }}>Group A · 정형 (7종)</div>
            {sp.signals.filter(x => x.id.startsWith("A")).map(s => (
              <div key={s.id} style={{ display: "grid", gridTemplateColumns: "60px 1fr auto auto", gap: 10, padding: "6px 0", fontSize: 12, borderBottom: "1px solid var(--border)", alignItems: "center" }}>
                <span className="mono muted">{s.id}</span>
                <span style={{ fontWeight: 500 }}>{s.name}</span>
                <span className="num">{s.then}</span>
                <Sig tone={s.thenTone}>{s.thenTone === "alert" ? "🚨" : s.thenTone === "pos" ? "긍정" : s.thenTone === "neg" ? "부정" : "중립"}</Sig>
              </div>
            ))}
          </div>
          <div>
            <div className="muted" style={{ fontSize: 11, fontWeight: 600, marginBottom: 6 }}>Group B · 비정형 (7종)</div>
            {sp.signals.filter(x => x.id.startsWith("B")).map(s => (
              <div key={s.id} style={{ display: "grid", gridTemplateColumns: "60px 1fr auto auto", gap: 10, padding: "6px 0", fontSize: 12, borderBottom: "1px solid var(--border)", alignItems: "center" }}>
                <span className="mono muted">{s.id}</span>
                <span style={{ fontWeight: 500 }}>{s.name}</span>
                <span className="num">{s.then}</span>
                <Sig tone={s.thenTone}>{s.thenTone === "pos" ? "긍정" : s.thenTone === "neg" ? "부정" : "중립"}</Sig>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginTop: 22 }}>
          <AiNote label="오차 원인 AI 분석">
            "당시 AI 서버 수요가 예측보다 빠르게 증가. A-2 CapEx·A-1 대만 신호가 현재보다 약했음. → 모델에 AI 서버 수요 가중치 상향 반영 완료. 동일 시점 재학습 시 오차 3.5%로 개선 확인."
          </AiNote>
        </div>

        <div style={{ marginTop: 22 }}>
          <HITL rules={HITL_DEFAULT_RULES} />
        </div>
      </div>
    </Modal>
  );
}

// ==== S-011 Event detail ====
function S011({ event, onClose, onNav }) {
  const e = event;
  return (
    <Modal title="글로벌 이벤트 상세" badge="S-011" onClose={onClose}>
      <div className="modal-body">
        <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 18 }}>
          <Sig tone={e.risk === "high" ? "neg" : e.risk === "mid" ? "neu" : "pos"} size="lg">
            {e.risk === "high" ? "고위험" : e.risk === "mid" ? "중위험" : "저위험"}
          </Sig>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-0.01em" }}>{e.title}</div>
            <div style={{ display: "flex", gap: 12, marginTop: 6, fontSize: 11, color: "var(--text-dim)" }}>
              <span><span className="muted">유형</span> <strong style={{ color: "var(--text)" }}>{e.type}</strong></span>
              <span><span className="muted">지역</span> <strong style={{ color: "var(--text)" }}>{e.region}</strong></span>
              <span><span className="muted">발생일</span> <span className="mono">{e.date}</span></span>
            </div>
          </div>
        </div>

        <AiNote label="AI 이벤트 요약">{e.summary}</AiNote>

        <div style={{ marginTop: 22 }}>
          <div className="dlabel" style={{ marginBottom: 8 }}>DRAM 가격 영향 분석</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
            {[{k:"short",l:"단기 (1~7주)"},{k:"mid",l:"중장기 (8~21주)"},{k:"long",l:"장기 (22주~)"}].map(p => {
              const eff = e.effects[p.k];
              return (
                <div key={p.k} className="card">
                  <div className="dlabel">{p.l}</div>
                  <div style={{ marginTop: 6, marginBottom: 8 }}><Sig tone={eff.tone} size="lg">{eff.tone === "pos" ? "긍정" : eff.tone === "neg" ? "부정" : "중립"}</Sig></div>
                  <div style={{ fontSize: 12, color: "var(--text-mid)" }}>{eff.text}</div>
                </div>
              );
            })}
          </div>
        </div>

        {e.links && e.links.length > 0 && (
          <div style={{ marginTop: 22 }}>
            <div className="dlabel" style={{ marginBottom: 8 }}>관련 수집 뉴스</div>
            <div className="card" style={{ padding: 0 }}>
              {e.links.map(idx => {
                const n = D2.news[idx];
                if (!n) return null;
                return (
                  <div key={idx} className="tappable" onClick={() => onNav("S-007", { news: n })}
                    style={{ padding: "10px 14px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 10, cursor: "pointer", fontSize: 12.5 }}>
                    <Sig tone={n.tone}>{n.tone === "pos" ? "긍정" : "부정"}</Sig>
                    <span style={{ flex: 1 }}>{n.title}</span>
                    <span className="mono muted" style={{ fontSize: 11 }}>{n.source}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {e.affects && e.affects.length > 0 && (
          <div style={{ marginTop: 22 }}>
            <div className="dlabel" style={{ marginBottom: 8 }}>영향 받는 신호</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {e.affects.map(sid => {
                const sig = [...D2.signalsA, ...D2.signalsB].find(x => x.id === sid);
                if (!sig) return null;
                return (
                  <button key={sid} className="chip" onClick={() => onNav(sid.startsWith("A") ? "S-003" : "S-004", { tab: sid })}>
                    <span className="mono">{sid}</span>
                    <span>{sig.name}</span>
                    <Sig tone={sig.tone}>{sig.tone === "pos" ? "긍정" : sig.tone === "neg" ? "부정" : sig.tone === "alert" ? "ALERT" : "중립"}</Sig>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div style={{ marginTop: 22 }}>
          <HITL rules={HITL_DEFAULT_RULES} />
        </div>
      </div>
    </Modal>
  );
}

// ==== S-013 Past signal vs current ====
function S013({ row, onClose }) {
  const sp = D2.snapshotPast;
  return (
    <Modal title="당시 신호 vs 현재 신호 비교" badge="S-013" size="lg" onClose={onClose}>
      <div className="modal-body">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 16, marginBottom: 22 }}>
          <div><div className="dlabel">예측일</div><div className="num" style={{ fontSize: 18, fontWeight: 600 }}>{row?.predDate || sp.date}</div></div>
          <div><div className="dlabel">예측값 → 실제값</div><div className="num" style={{ fontSize: 18, fontWeight: 600 }}>${(row?.pred || sp.predicted).toFixed(2)} → ${(row?.actual || sp.actual).toFixed(2)}</div></div>
          <div><div className="dlabel">오차</div><div className="num" style={{ fontSize: 18, fontWeight: 600, color: "var(--sig-neu)" }}>{(row?.error || sp.error).toFixed(1)}%</div></div>
          <div><div className="dlabel">판정</div><div style={{ marginTop: 6 }}><Sig tone={row?.tone || "neu"} size="lg">{(row?.tone || "neu") === "pos" ? "양호" : (row?.tone || "neu") === "neg" ? "부정확" : "허용범위"}</Sig></div></div>
        </div>

        <div className="dlabel" style={{ marginBottom: 8 }}>14개 신호 — 당시 vs 현재 비교</div>
        <table className="tbl">
          <thead>
            <tr>
              <th style={{ width: 60 }}>신호</th>
              <th>이름</th>
              <th className="num">당시값</th>
              <th>당시판정</th>
              <th className="num">현재값</th>
              <th>현재판정</th>
              <th>변화</th>
            </tr>
          </thead>
          <tbody>
            {sp.signals.map(s => (
              <tr key={s.id}>
                <td className="mono muted">{s.id}</td>
                <td>{s.name}</td>
                <td className="num">{s.then}</td>
                <td><Sig tone={s.thenTone}>{s.thenTone === "alert" ? "🚨" : s.thenTone === "pos" ? "긍정" : s.thenTone === "neg" ? "부정" : "중립"}</Sig></td>
                <td className="num">{s.now}</td>
                <td><Sig tone={s.nowTone}>{s.nowTone === "alert" ? "🚨" : s.nowTone === "pos" ? "긍정" : s.nowTone === "neg" ? "부정" : "중립"}</Sig></td>
                <td>
                  <span className={`arr ${s.direction === "up" ? "up" : s.direction === "down" ? "dn" : "flat"}`}>
                    {s.direction === "up" ? "↑" : s.direction === "down" ? "↓" : "↔"}
                  </span>
                  <span style={{ marginLeft: 8, fontSize: 11 }} className="muted">{s.change}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div style={{ marginTop: 22 }}>
          <AiNote label="오차 원인 AI 분석">
            "당시 A-1·A-2·B-2 신호가 현재보다 크게 약했음. AI 서버 수요 급증을 모델이 과소평가. 다음 학습에 CapEx·대만 공급망 가중치 상향 반영 완료. 동일 시점 재학습 시 오차 6.0% → 3.5% 개선 검증."
          </AiNote>
        </div>

        <div style={{ marginTop: 22 }}>
          <HITL rules={HITL_DEFAULT_RULES} />
        </div>
      </div>
    </Modal>
  );
}

Object.assign(window, { S002, S003, S004, S005, S007, S009, S011, S013 });


export { S002, S003, S004, S005, S007, S009, S011, S013, ConfidenceBar, SignalDetail }
