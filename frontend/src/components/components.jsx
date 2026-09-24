import React, { useState, useEffect, useRef, useMemo, useCallback, Fragment } from 'react'

// Shared components for Sixsense

// ==== Signal Badge ====
function Sig({ tone, children, size }) {
  const c = tone === "alert" ? "alert" : tone === "pos" ? "pos" : tone === "neg" ? "neg" : tone === "info" ? "info" : "neu";
  return (
    <span className={`sig ${c}`} style={size === "lg" ? { fontSize: 12, padding: "3px 9px" } : null}>
      <span className="dot"></span>
      {children}
    </span>
  );
}

// ==== Sparkline ====
function Sparkline({ data, tone = "pos", height = 36, area = true }) {
  if (!data || data.length === 0) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 100;
  const h = height;
  const pts = data.map((v, i) => [(i / (data.length - 1)) * w, h - ((v - min) / range) * (h - 4) - 2]);
  const path = pts.map((p, i) => (i === 0 ? `M${p[0]},${p[1]}` : `L${p[0]},${p[1]}`)).join(" ");
  const areaPath = `${path} L${w},${h} L0,${h} Z`;
  const color = tone === "alert" ? "var(--sig-alert)" : tone === "pos" ? "var(--sig-pos)" : tone === "neg" ? "var(--sig-neg)" : "var(--sig-neu)";
  return (
    <svg className="spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      {area && <path d={areaPath} fill={color} className="area" />}
      <path d={path} stroke={color} className="line" />
      <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r="2.5" fill={color} className="pt" stroke={color} />
    </svg>
  );
}

// ==== Modal Shell ====
function Modal({ children, title, badge, onClose, size }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = ""; };
  }, [onClose]);
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className={`modal ${size || ""}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div className="t">
            <span>{title}</span>
            {badge && <span className="badge">{badge}</span>}
          </div>
          <button className="x-btn" onClick={onClose} aria-label="닫기">✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}

// ==== Big number card ====
function MetricCard({ label, value, unit, change, changeTone, sub, onClick, hot, code }) {
  return (
    <div className={`card ${onClick ? "tappable" : ""}`} onClick={onClick}>
      <div className="card-h" style={{ marginBottom: 10 }}>
        <span>{label}</span>
        {onClick && <span className="code" style={{ textTransform: "none" }}>🔍 클릭</span>}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
        <span className="card-big num">{value}</span>
        {unit && <span className="muted num" style={{ fontSize: 12 }}>{unit}</span>}
      </div>
      {change !== undefined && (
        <div className="card-sub" style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 8 }}>
          <span className={`arr ${changeTone === "pos" ? "up" : changeTone === "neg" ? "dn" : "flat"}`}>
            {changeTone === "pos" ? "▲" : changeTone === "neg" ? "▼" : "—"}
          </span>
          <span className="num" style={{ color: changeTone === "pos" ? "var(--sig-pos)" : changeTone === "neg" ? "var(--sig-neg)" : "var(--text-mid)", fontWeight: 500 }}>
            {change}
          </span>
        </div>
      )}
      {code && <div className="muted mono" style={{ fontSize: 10, marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--border)" }}>{code}</div>}
    </div>
  );
}

// ==== Tab strip ====
function Tabs({ tabs, active, onChange }) {
  return (
    <div className="tabstrip">
      {tabs.map(t => (
        <button key={t.id} className={`tab ${active === t.id ? "active" : ""}`} onClick={() => onChange(t.id)}>
          {t.code && <span className="code">{t.code}</span>}
          {t.label}
        </button>
      ))}
    </div>
  );
}

// ==== Segmented control ====
function Seg({ options, value, onChange }) {
  return (
    <div className="seg">
      {options.map(o => (
        <button key={o.value} className={value === o.value ? "on" : ""} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

// ==== AI Note block ====
function AiNote({ children, label = "AI 생성 문장", source = "검증되지 않은 해석" }) {
  return (
    <div className="ai-note">
      <div className="label">{label} · {source}</div>
      <div>{children}</div>
    </div>
  );
}

// ==== Generic line chart ====
function LineChart({ width = 800, height = 280, series, xLabels, yDomain, refLines, bands, padding = { l: 44, r: 24, t: 16, b: 28 }, preserveAspectRatio = "xMidYMid meet" }) {
  const w = width, h = height;
  const cw = w - padding.l - padding.r;
  const ch = h - padding.t - padding.b;
  
  let ymin = yDomain ? yDomain[0] : Infinity, ymax = yDomain ? yDomain[1] : -Infinity;
  if (!yDomain) {
    series.forEach(s => s.data.forEach(d => { if (d.value < ymin) ymin = d.value; if (d.value > ymax) ymax = d.value; }));
    if (bands) bands.forEach(b => b.data.forEach(d => { if (d.lower < ymin) ymin = d.lower; if (d.upper > ymax) ymax = d.upper; }));
    const pad = (ymax - ymin) * 0.1 || Math.abs(ymax) * 0.05 || 1; ymin -= pad; ymax += pad;
  }
  
  const allX = series.flatMap(s => s.data.map(d => d.x));
  const xmin = Math.min(...allX), xmax = Math.max(...allX);
  
  const xs = (x) => padding.l + (xmax === xmin ? cw / 2 : ((x - xmin) / (xmax - xmin)) * cw);
  const ys = (y) => padding.t + ch - ((y - ymin) / (ymax - ymin)) * ch;
  
  // Y grid
  const yticks = 4;
  const yvals = Array.from({ length: yticks + 1 }, (_, i) => ymin + ((ymax - ymin) * i / yticks));
  
  return (
    <svg className="chart" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio={preserveAspectRatio} style={{ width: "100%", height: "auto" }}>
      {/* Grid */}
      <g className="grid">
        {yvals.map((v, i) => (
          <line key={i} x1={padding.l} x2={w - padding.r} y1={ys(v)} y2={ys(v)} />
        ))}
      </g>
      {/* Y axis labels */}
      <g className="axis">
        {yvals.map((v, i) => (
          <text key={i} x={padding.l - 6} y={ys(v) + 3} textAnchor="end">{typeof v === "number" ? v.toFixed(1) : v}</text>
        ))}
      </g>
      {/* X axis labels */}
      <g className="axis">
        {xLabels && xLabels.map((l, i) => (
          <text key={i} x={xs(l.x)} y={h - padding.b + 16} textAnchor="middle">{l.label}</text>
        ))}
        <line x1={padding.l} x2={w - padding.r} y1={h - padding.b} y2={h - padding.b} />
      </g>
      {/* Reference lines */}
      {refLines && refLines.map((r, i) => (
        <g key={i}>
          <line x1={padding.l} x2={w - padding.r} y1={ys(r.value)} y2={ys(r.value)} className="ref" stroke={r.color || "var(--text-faint)"} />
          {r.label && <text x={w - padding.r - 4} y={ys(r.value) - 4} textAnchor="end" fontFamily="var(--font-mono)" fontSize="10" fill={r.color || "var(--text-dim)"}>{r.label}</text>}
        </g>
      ))}
      {/* Confidence bands */}
      {bands && bands.map((b, i) => {
        const upper = b.data.map(d => `${xs(d.x)},${ys(d.upper)}`).join(" ");
        const lower = b.data.map(d => `${xs(d.x)},${ys(d.lower)}`).reverse().join(" ");
        return <polygon key={i} points={`${upper} ${lower}`} className="band" fill={b.color || "var(--text-mid)"} fillOpacity={b.opacity || null} />;
      })}
      {/* Series */}
      {series.map((s, i) => {
        const path = s.data.map((d, j) => `${j === 0 ? "M" : "L"}${xs(d.x)},${ys(d.value)}`).join(" ");
        return (
          <g key={i}>
            <path d={path} className="line" stroke={s.color || "var(--text)"} strokeDasharray={typeof s.dashed === "string" ? s.dashed : (s.dashed ? "4 3" : null)} strokeWidth={s.strokeWidth || null} />
            {s.dots && s.data.map((d, j) => (
              <circle key={j} cx={xs(d.x)} cy={ys(d.value)} r={s.dotR || 3} className="dot" stroke={s.color || "var(--text)"}
                      onClick={s.onDotClick ? () => s.onDotClick(d) : null} />
            ))}
            {s.endLabel && (
              <text x={xs(s.data[s.data.length-1].x) + 6} y={ys(s.data[s.data.length-1].value) + 4} fontFamily="var(--font-mono)" fontSize="10" fill={s.color || "var(--text)"} fontWeight="500">{s.endLabel}</text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

// ==== Compact filter dropdown ====
function FilterSelect({ label, value, options, onChange }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map(o => <option key={o.value} value={o.value}>{label}: {o.label}</option>)}
    </select>
  );
}

// ==== Section header ====
function SectionHead({ icon, num, title, sub, actions }) {
  return (
    <div className="section-head">
      <div className="title">
        {num && <span className="num-tag">{num}</span>}
        {icon && <span style={{ fontSize: 14 }}>{icon}</span>}
        <span>{title}</span>
        {sub && <span className="meta">{sub}</span>}
      </div>
      {actions && <div className="actions">{actions}</div>}
    </div>
  );
}

// USER-REQUESTED EXTENSION (2026-05-18 #3) — **bold** 마크다운을 <strong> 으로 렌더링
function renderInsightEmphasis(text) {
  if (!text) return null;
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    const m = part.match(/^\*\*([^*]+)\*\*$/);
    if (m) return <strong key={i} className="insight-emphasis">{m[1]}</strong>;
    return <span key={i}>{part}</span>;
  });
}

// ==== 시장 신호 요약 카드 ====
// 수집된 사실(주가지수·신호·뉴스·거시)을 Gemini 가 요약한 문장. 가격 예측·신뢰도는 없다
// (예측 모델이 검증 불합격 — honest_backtest.py). 카드 클릭 시 전체 문장을 모달로 표시.
function InsightCard({ insight }) {
  const [open, setOpen] = useState(false);
  if (!insight) {
    return (
      <div className="card insight-card" style={{ display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-dim)", fontSize: 12 }}>
        시장 신호 요약 — 데이터 준비 중
      </div>
    );
  }
  const toneClass = insight.tone === "pos" ? "pos" : insight.tone === "neg" ? "neg" : "neu";
  const sourceLabel = `AI 요약 · ${insight.model || "AI"} · 검증되지 않은 해석`;
  const KeySignals = () => (
    <div className="insight-keysig">
      <span className="insight-keysig-label">언급 신호</span>
      {(insight.keySignals || []).map((s) => (
        <span key={s} className="num insight-sig-chip">{s}</span>
      ))}
      {(!insight.keySignals || insight.keySignals.length === 0) && <span style={{ color: "var(--text-dim)" }}>—</span>}
    </div>
  );
  return (
    <>
      <div
        className={`card insight-card tappable insight-tone-${toneClass}`}
        onClick={() => setOpen(true)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setOpen(true); } }}
        title="클릭하여 전체 요약 보기"
      >
        <div className="insight-h">
          <div className="insight-title">
            <span className="insight-glyph">◆</span>
            <span>시장 신호 요약</span>
          </div>
          <div className="insight-meta">
            <span className="insight-expand">🔍 클릭</span>
          </div>
        </div>

        <div className="insight-main">
          <div className="insight-body insight-body-clamp">
            {renderInsightEmphasis(insight.summary || "(요약 없음)")}
          </div>

          <div className="ai-note insight-claude">
            <div className="label">{sourceLabel}</div>
            <div className="insight-headline">{insight.headline || "요약 중"}</div>
            <KeySignals />
          </div>
        </div>
      </div>

      {open && (
        <Modal title="시장 신호 요약 — 전체" badge={insight.model || "AI"} onClose={() => setOpen(false)} size="md">
          <div className={`insight-modal-body insight-tone-${toneClass}`}>
            <div className="ai-note insight-claude" style={{ marginBottom: 18 }}>
              <div className="label">{sourceLabel}</div>
              <div className="insight-headline" style={{ fontSize: 19, margin: "10px 0 8px" }}>{insight.headline || "요약 중"}</div>
              <KeySignals />
            </div>

            <div className="insight-modal-summary">
              {renderInsightEmphasis(insight.summary || "(요약 없음)")}
            </div>

            <div style={{ marginTop: 16, fontSize: 11, color: "var(--text-dim)", lineHeight: 1.6 }}>
              수집된 데이터를 AI 가 요약한 문장으로, 가격 예측이 아닙니다. 숫자는 원본 데이터로 확인하세요.
              {insight.generatedAt && <> · 생성 <span className="num">{insight.generatedAt}</span></>}
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}

Object.assign(window, {
  Sig, Sparkline, Modal, MetricCard, Tabs, Seg,
  AiNote, LineChart, FilterSelect, SectionHead, InsightCard
});


export { Sig, Sparkline, Modal, MetricCard, Tabs, Seg, AiNote, LineChart, FilterSelect, SectionHead, InsightCard }
