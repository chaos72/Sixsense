// S-001 Main Dashboard
const D = window.SIXSENSE_DATA;

function Dashboard({ onNav }) {
  const m = D.meta;
  const [chartRange, setChartRange] = useState("all");
  
  return (
    <div className="content">
      {/* Top 3 cards */}
      <div className="section">
        <SectionHead num="01" icon="◉" title="가격 스냅샷" sub="2026-04-22 (화) 기준 — 매주 화요일 06:00 자동 갱신" />
        <div className="grid-3">
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
            code="prophet_v2.1 · 신뢰 81%"
            value={`$${m.pred7.toFixed(2)}`}
            unit="/ GB"
            change={`${m.pred7Change} 예상`}
            changeTone="pos"
            sub="🔍 클릭하여 근거 보기"
            onClick={() => onNav("S-002", { horizon: 7 })}
          />
          <MetricCard
            label="8~21주 AI 예측가"
            code="prophet_v2.1 · 신뢰 74%"
            value={`$${m.pred21.toFixed(2)}`}
            unit="/ GB"
            change={`${m.pred21Change} 예상`}
            changeTone="pos"
            sub="🔍 클릭하여 근거 보기"
            onClick={() => onNav("S-002", { horizon: 21 })}
          />
        </div>
      </div>

      {/* DRAM Chart */}
      <div className="section">
        <SectionHead num="02" icon="◢" title="DRAM 52주 히스토리 + AI 예측" sub="차트의 특정 주 클릭 → 주별 스냅샷" actions={<ChartRangeSeg value={chartRange} onChange={setChartRange} />} />
        <div className="card">
          <DramChart range={chartRange} onPointClick={(d) => onNav("S-009", { week: d.x })} />
          <ChartLegend range={chartRange} />
        </div>
      </div>

      {/* 14 signals */}
      <div className="section">
        <SectionHead num="03" icon="◧" title="14개 프록시 신호 통합 현황" sub="각 카드 클릭 → 상세" />
        
        <div style={{ marginBottom: 18 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
            <div className="dlabel">Group A · 정형 (7종)</div>
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
            <div className="dlabel">Group B · 비정형 (7종)</div>
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

      {/* Graph RAG */}
      <div className="section">
        <SectionHead num="04" icon="⌖" title="Graph RAG — 구리 vs DRAM 선행 영향도" actions={<button className="btn sm" onClick={() => onNav("S-005")}>상세 분석 →</button>} />
        <div className="card" style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 28, alignItems: "center" }}>
          <GraphRagMini />
          <div>
            <div className="dlabel">상관계수 · 선행 시차</div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginBottom: 6 }}>
              <span className="num" style={{ fontSize: 28, fontWeight: 600, color: "var(--sig-pos)" }}>+0.72</span>
              <span className="muted" style={{ fontSize: 13 }}>/ 선행 <strong className="num" style={{ color: "var(--text)" }}>10주</strong></span>
            </div>
            <AiNote label="현재 시사점" source="Claude · Graph RAG">
              "구리 <strong>+8.3%</strong> · 6주 연속 상승 → 약 <strong>10주 후 DRAM 6~8% 상승 가능</strong>. 신뢰도 74%"
            </AiNote>
          </div>
        </div>
      </div>

      {/* News + Macro */}
      <div className="section">
        <div className="grid-2">
          <div>
            <SectionHead num="05" icon="◳" title="AI 뉴스 & 감성 분석" actions={<button className="btn sm" onClick={() => onNav("S-006")}>전체 목록 →</button>} />
            <div className="card" style={{ padding: 0 }}>
              {D.news.filter(n => n.hot).map((n, i) => (
                <div key={i} className="card tappable flat" onClick={() => onNav("S-007", { news: n })}
                     style={{ border: "none", borderBottom: i < 2 ? "1px solid var(--border)" : "none", borderRadius: 0, padding: "12px 18px", display: "flex", alignItems: "center", gap: 12 }}>
                  <Sig tone={n.tone}>{n.tone === "pos" ? "긍정" : n.tone === "neg" ? "부정" : "중립"}</Sig>
                  <div style={{ flex: 1, fontSize: 13, fontWeight: 500 }}>{n.title}</div>
                  <span className="muted mono" style={{ fontSize: 11 }}>{n.source}</span>
                  <span className="num" style={{ fontSize: 11, color: n.tone === "pos" ? "var(--sig-pos)" : n.tone === "neg" ? "var(--sig-neg)" : "var(--sig-neu)", fontWeight: 500 }}>
                    {n.score > 0 ? "+" : ""}{n.score.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <SectionHead num="06" icon="◔" title="거시경제 지표" actions={<button className="btn sm" onClick={() => onNav("S-008", { tab: "fed" })}>전체 →</button>} />
            <div className="card" style={{ padding: 0 }}>
              {D.macro.map((mi, i) => (
                <div key={i} className="card tappable flat" onClick={() => onNav("S-008", { tab: mi.id })}
                     style={{ border: "none", borderBottom: i < D.macro.length - 1 ? "1px solid var(--border)" : "none", borderRadius: 0, padding: "10px 18px", display: "grid", gridTemplateColumns: "1.2fr 0.7fr 1fr auto", alignItems: "center", gap: 12 }}>
                  <span style={{ fontSize: 12.5, fontWeight: 500 }}>{mi.name}</span>
                  <span className="num" style={{ fontSize: 13, fontWeight: 600 }}>{mi.value}</span>
                  <Sig tone={mi.tone}>{mi.change}</Sig>
                  <span className="muted" style={{ fontSize: 11 }}>{mi.desc}</span>
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
            <SectionHead num="07" icon="⚠" title="글로벌 이벤트 모니터링" actions={<button className="btn sm" onClick={() => onNav("S-010")}>전체 목록 →</button>} />
            <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {D.events.slice(0, 3).map((e) => (
                <div key={e.id} className="card tappable flat" onClick={() => onNav("S-011", { event: e })}
                     style={{ padding: "10px 14px", display: "flex", alignItems: "center", gap: 10, background: "var(--surface-2)" }}>
                  <Sig tone={e.risk === "high" ? "neg" : e.risk === "mid" ? "neu" : "pos"}>
                    {e.risk === "high" ? "고위험" : e.risk === "mid" ? "중위험" : "저위험"}
                  </Sig>
                  <span style={{ flex: 1, fontSize: 12.5, fontWeight: 500 }}>{e.title}</span>
                  <span className="mono muted" style={{ fontSize: 11 }}>{e.region}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <SectionHead num="08" icon="▤" title="AI 예측 정확도 트래킹" actions={<button className="btn sm" onClick={() => onNav("S-012")}>전체 이력 →</button>} />
            <div className="card" style={{ padding: 0 }}>
              {D.accuracy.filter(a => a.actual !== null).slice(0, 3).map((a, i) => (
                <div key={i} style={{ padding: "12px 16px", borderBottom: i < 2 ? "1px solid var(--border)" : "none", display: "grid", gridTemplateColumns: "auto auto auto 1fr auto", alignItems: "center", gap: 14, fontSize: 12 }}>
                  <span className="muted mono">{Math.round((Date.parse("2026-04-22") - Date.parse(a.predDate)) / (1000 * 60 * 60 * 24 * 7))}주전</span>
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
        <SectionHead num="09" icon="▤" title="이번 주 새 수집 데이터 현황" actions={<button className="btn sm" onClick={() => onNav("S-014")}>수집 현황 →</button>} />
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
            <span className="num" style={{ marginLeft: 8, fontWeight: 600 }}>6일 22시간</span>
          </div>
        </div>
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
      />
    </div>
  );
}

function ChartLegend({ range }) {
  return (
    <div style={{ display: "flex", gap: 24, marginTop: 12, paddingLeft: 44, fontSize: 11, color: "var(--text-dim)", flexWrap: "wrap" }}>
      <span className="chart-legend-item">
        <svg width="20" height="2"><line x1="0" y1="1" x2="20" y2="1" stroke="var(--text)" strokeWidth="1.75"/></svg> 실측 ({range === "short" ? "26주" : range === "mid" ? "13주" : "52주"})
      </span>
      {(range === "short" || range === "mid" || range === "all") && (
        <span className="chart-legend-item">
          <svg width="20" height="6"><line x1="0" y1="3" x2="20" y2="3" stroke="var(--sig-info)" strokeWidth="1.75" strokeDasharray="4 3"/></svg>
          1~7주 예측 · 신뢰구간
        </span>
      )}
      {(range === "mid" || range === "all") && (
        <span className="chart-legend-item">
          <svg width="20" height="6"><line x1="0" y1="3" x2="20" y2="3" stroke="var(--forecast-mid)" strokeWidth={range === "mid" ? "2.4" : "1.75"} strokeDasharray={range === "mid" ? null : "4 3"}/></svg>
          8~21주 예측 · 신뢰구간 {range === "mid" && <span style={{ color: "var(--forecast-mid)", fontWeight: 600, marginLeft: 4 }}>(중점)</span>}
        </span>
      )}
      <span className="muted" style={{ marginLeft: "auto", whiteSpace: "nowrap" }}>예측 데이터 포인트 클릭 → S-009</span>
    </div>
  );
}

function GraphRagMini() {
  // mini overlay chart copper vs DRAM
  const cuData = [0, 0.1, 0.05, 0.15, 0.3, 0.4, 0.55, 0.65, 0.72, 0.8, 0.83, 0.78, 0.7];
  const dramData = [0.05, 0.1, 0.12, 0.1, 0.08, 0.12, 0.15, 0.2, 0.28, 0.4, 0.55, 0.68, 0.72];
  
  return (
    <div>
      <LineChart
        width={600} height={180}
        padding={{ l: 36, r: 70, t: 12, b: 24 }}
        series={[
          { data: cuData.map((v, i) => ({ x: i, value: v })), color: "var(--sig-info)", endLabel: "구리 (선행)" },
          { data: dramData.map((v, i) => ({ x: i, value: v })), color: "var(--text)", endLabel: "DRAM" },
        ]}
        xLabels={[
          { x: 0, label: "52주전" },
          { x: 6, label: "26주전" },
          { x: 12, label: "현재" },
        ]}
      />
    </div>
  );
}

Object.assign(window, { Dashboard, SignalCard });
