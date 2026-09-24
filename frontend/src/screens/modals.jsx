import React, { useState } from 'react'
import { SIXSENSE_DATA } from '../mocks/data.js'
import { Sig, Modal, Tabs, AiNote, LineChart } from '../components/components.jsx'

// Modal-based detail screens: S-003, S-004, S-007, S-009, S-011
// 원칙: 수집·측정된 값만 표시. 고정 숫자·예시 문장·동작하지 않는 버튼을 두지 않는다.
// (v2.3 에서 S-002 예측 근거·S-005 Graph RAG·S-013 당시 신호 — 고정 가짜 내용 — 삭제)
const D2 = SIXSENSE_DATA;

// 원값 표시 — 신호마다 단위·자릿수가 달라 크기에 따라 줄여 쓴다
function fmtRaw(v) {
  if (v === null || v === undefined) return "—";
  const a = Math.abs(v);
  if (a >= 1e9) return `${(v / 1e9).toFixed(2)}B`;
  if (a >= 1e6) return `${(v / 1e6).toFixed(2)}M`;
  if (a >= 1e3) return v.toLocaleString(undefined, { maximumFractionDigits: 1 });
  if (a >= 10) return v.toFixed(1);
  return v.toFixed(3);
}

function changeText(now, then) {
  if (then === 0 || then === null || then === undefined) return "—";
  const c = (now / then - 1) * 100;
  return `${c > 0 ? "+" : ""}${c.toFixed(1)}%`;
}

// ==== S-003 Group A 정형 ====
function S003({ tab: initialTab, onClose, onNav }) {
  const [tab, setTab] = useState(initialTab || D2.signalsA[0].id);
  const s = D2.signalsA.find(x => x.id === tab) || D2.signalsA[0];
  return (
    <Modal title="정형 데이터 (Group A) 상세" badge="S-003" size="lg" onClose={onClose}>
      <div className="modal-body">
        <Tabs active={s.id} onChange={setTab} tabs={D2.signalsA.map(x => ({ id: x.id, code: x.id, label: x.name }))} />
        <SignalDetail s={s} groupType="A" onNav={onNav} />
      </div>
    </Modal>
  );
}

// ==== S-004 Group B 비정형 ====
function S004({ tab: initialTab, onClose, onNav }) {
  const [tab, setTab] = useState(initialTab || D2.signalsB[0].id);
  const s = D2.signalsB.find(x => x.id === tab) || D2.signalsB[0];
  return (
    <Modal title="비정형 데이터 (Group B) 상세" badge="S-004" size="lg" onClose={onClose}>
      <div className="modal-body">
        <Tabs active={s.id} onChange={setTab} tabs={D2.signalsB.map(x => ({ id: x.id, code: x.id, label: x.name }))} />
        <SignalDetail s={s} groupType="B" onNav={onNav} />
      </div>
    </Modal>
  );
}

// 신호 상세 — 실측 이력(s.recent, 최근 26주 원값)만 사용
function SignalDetail({ s, groupType, onNav }) {
  const rows = s.recent || [];
  const n = rows.length;
  const series = [{ data: rows.map((r, i) => ({ x: i - (n - 1), value: r.value })), color: s.stale ? "var(--sig-neu)" : "var(--text)", dots: n <= 12 }];
  const back8 = n > 8 ? rows[n - 9] : null;
  const last = n ? rows[n - 1] : null;
  const recentNews = D2.news.slice(0, 3);

  return (
    <div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginBottom: 18, alignItems: "flex-end" }}>
        <div style={{ flex: "2 1 220px" }}>
          <div className="dlabel">신호명</div>
          <div style={{ fontSize: 18, fontWeight: 600 }}>{s.name}</div>
          <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>{s.desc}</div>
        </div>
        <div style={{ flex: "1 1 120px" }}>
          <div className="dlabel">최신값</div>
          <div className="num" style={{ fontSize: 26, fontWeight: 600 }}>{s.value}</div>
        </div>
        <div style={{ flex: "0 1 auto" }}>
          <div className="dlabel">상태</div>
          {s.stale
            ? <Sig tone="alert" size="lg">갱신 중단</Sig>
            : <Sig tone={s.tone} size="lg">{s.tone === "pos" ? "긍정" : s.tone === "neg" ? "부정" : "중립"}</Sig>}
        </div>
        <div style={{ flex: "1 1 200px" }}>
          <div className="dlabel">수집</div>
          <div style={{ fontSize: 12, fontWeight: 500 }}>{s.source}</div>
          <div className="muted mono" style={{ fontSize: 10, marginTop: 2 }}>마지막 수집 {s.collectedAt || "—"} · 데이터 {s.asOf || "—"}</div>
        </div>
      </div>

      {s.stale && (
        <div className="banner">
          갱신 중단 — {s.staleReason}. 아래 값은 {s.dataSince} 이후 새로 바뀌지 않았으니 현재 상황 판단에 쓰지 마세요.
        </div>
      )}

      <div className="dlabel" style={{ marginBottom: 8 }}>최근 {n}주 실측 추이</div>
      <div className="card">
        {n > 1 ? (
          <LineChart
            width={1000} height={220}
            series={series}
            xLabels={[{ x: -(n - 1), label: rows[0].week }, { x: 0, label: rows[n - 1].week }]}
          />
        ) : <div className="muted" style={{ fontSize: 12 }}>표시할 이력이 없습니다.</div>}
      </div>

      {last && (
        <div className="muted" style={{ fontSize: 12, marginTop: 10 }}>
          {last.week} 기준 {fmtRaw(last.value)}
          {back8 && <> · 8주 전({back8.week}) {fmtRaw(back8.value)} 대비 <strong>{changeText(last.value, back8.value)}</strong></>}
        </div>
      )}

      <div className="dlabel" style={{ margin: "18px 0 8px" }}>최근 관측값 (최신 8개)</div>
      <table className="tbl">
        <thead><tr><th>주</th><th className="num">값</th><th className="num">전주 대비</th></tr></thead>
        <tbody>
          {rows.slice(-8).reverse().map((r, i, arr) => {
            const prev = arr[i + 1];
            return (
              <tr key={r.week}>
                <td className="mono">{r.week}</td>
                <td className="num" style={{ fontWeight: 600 }}>{fmtRaw(r.value)}</td>
                <td className="num muted">{prev ? changeText(r.value, prev.value) : "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {groupType === "B" && (
        <div style={{ marginTop: 18 }}>
          <div className="dlabel" style={{ marginBottom: 8 }}>참고: 최근 핵심 뉴스 (이 신호 계산에 쓰인 기사 목록은 아님)</div>
          <div className="card" style={{ padding: 0 }}>
            {recentNews.map((nw, i) => (
              <div key={i} className="tappable" onClick={() => onNav("S-007", { news: nw })}
                style={{ padding: "12px 16px", borderBottom: i < recentNews.length - 1 ? "1px solid var(--border)" : "none", display: "grid", gridTemplateColumns: "auto minmax(0, 1fr) auto", gap: 12, alignItems: "center", fontSize: 12.5, cursor: "pointer" }}>
                <Sig tone={nw.tone}>{nw.tone === "pos" ? "긍정" : nw.tone === "neg" ? "부정" : "중립"}</Sig>
                <div style={{ fontWeight: 500, overflowWrap: "anywhere" }}>{nw.title}</div>
                {/* 긴 출처명(예: finance.biggo.com)이 모바일 폭을 넘지 않도록 줄바꿈 허용 */}
                <span className="muted mono" style={{ fontSize: 11, maxWidth: 110, overflowWrap: "anywhere", textAlign: "right" }}>{nw.source} · {nw.date}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ==== S-007 News detail ====
function EffectsGrid({ effects }) {
  if (!effects) return null;
  const cols = [{ k: "short", l: "단기" }, { k: "mid", l: "중기" }, { k: "long", l: "장기" }].filter(p => effects[p.k]);
  if (!cols.length) return null;
  return (
    <div style={{ marginTop: 22 }}>
      <div className="dlabel" style={{ marginBottom: 8 }}>AI 추정 영향 — 검증되지 않은 해석</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        {cols.map(p => {
          const e = effects[p.k];
          return (
            <div key={p.k} className="card" style={{ flex: "1 1 150px", minWidth: 0 }}>
              <div className="dlabel">{p.l}</div>
              <div style={{ marginTop: 6, marginBottom: 8 }}><Sig tone={e.tone} size="lg">{e.tone === "pos" ? "긍정" : e.tone === "neg" ? "부정" : "중립"}</Sig></div>
              <div style={{ fontSize: 12, color: "var(--text-mid)" }}>{e.text}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function S007({ news, onClose }) {
  const n = news;
  return (
    <Modal title="뉴스 원문 & AI 요약" badge="S-007" size="lg" onClose={onClose}>
      <div className="modal-body">
        <div style={{ display: "flex", alignItems: "flex-start", gap: 14, marginBottom: 6 }}>
          <Sig tone={n.tone} size="lg">{n.tone === "pos" ? "긍정" : n.tone === "neg" ? "부정" : "중립"}</Sig>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 18, fontWeight: 600, letterSpacing: "-0.01em", lineHeight: 1.4 }}>{n.title}</div>
            <div className="muted mono" style={{ fontSize: 11, marginTop: 4 }}>{n.titleEn}</div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 16, fontSize: 11, color: "var(--text-dim)", marginBottom: 18, flexWrap: "wrap" }}>
          <span><span className="muted">출처</span> <strong className="mono" style={{ color: "var(--text)" }}>{n.source}</strong></span>
          <span><span className="muted">발행</span> <span className="mono">{n.date}</span></span>
          <span><span className="muted">AI 감성 점수</span> <span className="num" style={{ color: n.tone === "pos" ? "var(--sig-pos)" : n.tone === "neg" ? "var(--sig-neg)" : "var(--text)", fontWeight: 600 }}>{n.score > 0 ? "+" : ""}{n.score.toFixed(2)}</span></span>
          {n.conf !== undefined && <span><span className="muted">AI 확신도(자가평가)</span> <span className="num">{n.conf}%</span></span>}
        </div>

        <AiNote label="AI 요약">{n.summary || "—"}</AiNote>
        <EffectsGrid effects={n.effects} />

        {n.linked && n.linked.length > 0 && (
          <div style={{ marginTop: 22 }}>
            <div className="dlabel" style={{ marginBottom: 8 }}>AI 가 연결한 신호</div>
            <div className="card" style={{ padding: "10px 14px" }}>
              {n.linked.map((l, i) => (
                <div key={i} style={{ padding: "4px 0", fontSize: 12.5 }}>· {l}</div>
              ))}
            </div>
          </div>
        )}

        {n.link && (
          <div style={{ marginTop: 22, display: "flex", justifyContent: "flex-end" }}>
            <a className="btn primary" href={n.link} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>
              🌐 원문 기사 열기 →
            </a>
          </div>
        )}
      </div>
    </Modal>
  );
}

// ==== S-009 8주 전 vs 지금 ====
function S009({ onClose }) {
  const sp = D2.snapshotPast;
  if (!sp || !sp.date) {
    return (
      <Modal title="8주 전과 비교" badge="S-009" onClose={onClose}>
        <div className="modal-body muted" style={{ fontSize: 12 }}>비교할 데이터가 부족합니다.</div>
      </Modal>
    );
  }
  const unit = D2.meta.unitShort;
  const tone = sp.changePct > 0 ? "pos" : sp.changePct < 0 ? "neg" : "neu";
  return (
    <Modal title={`8주 전(${sp.date}) vs 지금`} badge="S-009" size="lg" onClose={onClose}>
      <div className="modal-body">
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginBottom: 22 }}>
          <div style={{ flex: "1 1 150px" }}><div className="dlabel">8주 전 {D2.meta.unitLabel}</div><div className="num" style={{ fontSize: 22, fontWeight: 600 }}>{sp.then.toFixed(1)} {unit}</div></div>
          <div style={{ flex: "1 1 150px" }}><div className="dlabel">지금</div><div className="num" style={{ fontSize: 22, fontWeight: 600 }}>{sp.now.toFixed(1)} {unit}</div></div>
          <div style={{ flex: "1 1 150px" }}><div className="dlabel">변화 (실측)</div><div style={{ marginTop: 6 }}><Sig tone={tone} size="lg">{sp.changePct > 0 ? "+" : ""}{sp.changePct.toFixed(1)}%</Sig></div></div>
        </div>

        <div className="dlabel" style={{ marginBottom: 8 }}>신호별 8주 전 → 지금 (수집값)</div>
        <table className="tbl">
          <thead><tr><th style={{ width: 60 }}>신호</th><th>이름</th><th className="num">8주 전</th><th className="num">지금</th><th>방향</th></tr></thead>
          <tbody>
            {sp.signals.map(x => (
              <tr key={x.id}>
                <td className="mono muted">{x.id}</td>
                <td>{x.name}</td>
                <td className="num">{x.then}</td>
                <td className="num">{x.now}</td>
                <td>
                  <span className={`arr ${x.direction === "up" ? "up" : x.direction === "down" ? "dn" : "flat"}`}>
                    {x.direction === "up" ? "↑" : x.direction === "down" ? "↓" : "↔"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="muted" style={{ fontSize: 11, marginTop: 10 }}>
          수집값을 그대로 비교한 것이며, 신호 변화와 가격 변화 사이의 인과관계를 뜻하지 않습니다.
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
            <div style={{ display: "flex", gap: 12, marginTop: 6, fontSize: 11, color: "var(--text-dim)", flexWrap: "wrap" }}>
              <span><span className="muted">유형</span> <strong style={{ color: "var(--text)" }}>{e.type}</strong></span>
              <span><span className="muted">지역</span> <strong style={{ color: "var(--text)" }}>{e.region}</strong></span>
              <span><span className="muted">발생일</span> <span className="mono">{e.date}</span></span>
              <span><span className="muted">위험도</span> AI 분류</span>
            </div>
          </div>
        </div>

        <AiNote label="AI 이벤트 요약">{e.summary}</AiNote>
        <EffectsGrid effects={e.effects} />

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
                    <Sig tone={n.tone}>{n.tone === "pos" ? "긍정" : n.tone === "neg" ? "부정" : "중립"}</Sig>
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
            <div className="dlabel" style={{ marginBottom: 8 }}>AI 가 연결한 신호</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {e.affects.map(sid => {
                const sig = [...D2.signalsA, ...D2.signalsB].find(x => x.id === sid);
                if (!sig) return null;
                return (
                  <button key={sid} className="chip" onClick={() => onNav(sid.startsWith("A") ? "S-003" : "S-004", { tab: sid })}>
                    <span className="mono">{sid}</span>
                    <span>{sig.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}

Object.assign(window, { S003, S004, S007, S009, S011 });

export { S003, S004, S007, S009, S011, SignalDetail }
