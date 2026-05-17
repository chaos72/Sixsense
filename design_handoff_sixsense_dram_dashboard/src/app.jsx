// Main app — routing, tweaks, layout shell
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "light",
  "density": "comfortable",
  "showTweaks": false
}/*EDITMODE-END*/;

function App() {
  // Parse URL params for deep-link (used by Canvas iframes)
  const initial = (() => {
    try {
      const u = new URL(window.location.href);
      const screen = u.searchParams.get("screen") || "S-001";
      const modal = u.searchParams.get("modal");
      const params = {};
      ["tab", "horizon", "newsIdx", "eventIdx", "week", "rowIdx"].forEach(k => {
        const v = u.searchParams.get(k);
        if (v !== null) params[k] = isNaN(+v) ? v : +v;
      });
      return { screen, modal, params };
    } catch (e) { return { screen: "S-001", params: {} }; }
  })();
  
  const FULL_PAGES = ["S-001", "S-006", "S-008", "S-010", "S-012", "S-014"];
  const MODAL_IDS = ["S-002", "S-003", "S-004", "S-005", "S-007", "S-009", "S-011", "S-013"];
  
  const expand = (id, p) => {
    const D = window.SIXSENSE_DATA;
    const out = { ...p };
    if (p.newsIdx !== undefined) out.news = D.news[p.newsIdx];
    if (p.eventIdx !== undefined) out.event = D.events[p.eventIdx];
    if (p.rowIdx !== undefined) out.row = D.accuracy[p.rowIdx];
    return out;
  };
  
  const startPage = FULL_PAGES.includes(initial.screen) ? initial.screen : "S-001";
  const startStack = (() => {
    if (initial.modal && MODAL_IDS.includes(initial.modal)) return [{ id: initial.modal, params: expand(initial.modal, initial.params) }];
    if (!FULL_PAGES.includes(initial.screen) && MODAL_IDS.includes(initial.screen)) return [{ id: initial.screen, params: expand(initial.screen, initial.params) }];
    return [];
  })();

  const [route, setRoute] = useState({ page: startPage, params: initial.params });
  const [modalStack, setModalStack] = useState(startStack);
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  useEffect(() => {
    document.documentElement.dataset.theme = t.theme;
    document.documentElement.dataset.density = t.density;
  }, [t.theme, t.density]);

  const onNav = (id, params = {}) => {
    // Modal screens
    const MODAL_IDS = ["S-002", "S-003", "S-004", "S-005", "S-007", "S-009", "S-011", "S-013"];
    if (MODAL_IDS.includes(id)) {
      setModalStack(s => [...s, { id, params }]);
    } else {
      // Full-page screens
      setRoute({ page: id, params });
      setModalStack([]);
      window.scrollTo(0, 0);
    }
  };

  const closeTop = () => setModalStack(s => s.slice(0, -1));
  const goMain = () => { setRoute({ page: "S-001", params: {} }); setModalStack([]); window.scrollTo(0, 0); };

  // Determine current page label
  const pageLabel = (() => {
    const m = {
      "S-001": "메인 대시보드",
      "S-006": "AI 뉴스 분석 전체 목록",
      "S-008": "거시경제 지표 통합 상세",
      "S-010": "글로벌 이벤트 모니터링",
      "S-012": "AI 예측 정확도 전체 이력",
      "S-014": "데이터 수집 현황 상세",
    };
    return m[route.page];
  })();

  return (
    <div className="app">
      <Topbar pageLabel={pageLabel} pageId={route.page} onHome={goMain} t={t} setTweak={setTweak} />
      
      {route.page === "S-001" && <Dashboard onNav={onNav} />}
      {route.page === "S-006" && <S006 onClose={goMain} onNav={onNav} />}
      {route.page === "S-008" && <S008 tab={route.params.tab} onClose={goMain} />}
      {route.page === "S-010" && <S010 onClose={goMain} onNav={onNav} />}
      {route.page === "S-012" && <S012 onClose={goMain} onNav={onNav} />}
      {route.page === "S-014" && <S014 onClose={goMain} />}

      {/* Modal stack */}
      {modalStack.map((m, i) => {
        const isTop = i === modalStack.length - 1;
        const onCloseModal = isTop ? closeTop : () => {};
        const params = m.params || {};
        return (
          <Fragment key={i}>
            {m.id === "S-002" && <S002 horizon={params.horizon} onClose={onCloseModal} onNav={onNav} />}
            {m.id === "S-003" && <S003 tab={params.tab} onClose={onCloseModal} onNav={onNav} />}
            {m.id === "S-004" && <S004 tab={params.tab} onClose={onCloseModal} onNav={onNav} />}
            {m.id === "S-005" && <S005 onClose={onCloseModal} />}
            {m.id === "S-007" && <S007 news={params.news} onClose={onCloseModal} onNav={onNav} />}
            {m.id === "S-009" && <S009 week={params.week} onClose={onCloseModal} />}
            {m.id === "S-011" && <S011 event={params.event} onClose={onCloseModal} onNav={onNav} />}
            {m.id === "S-013" && <S013 row={params.row} onClose={onCloseModal} />}
          </Fragment>
        );
      })}

      <TweaksPanel title="Tweaks" defaultPos="bottom-right">
        <TweakSection title="외관">
          <TweakRadio label="테마" value={t.theme} onChange={(v) => setTweak("theme", v)} options={[{ value: "light", label: "라이트" }, { value: "dark", label: "다크" }]} />
          <TweakRadio label="정보 밀도" value={t.density} onChange={(v) => setTweak("density", v)} options={[{ value: "comfortable", label: "Comfortable" }, { value: "compact", label: "Compact" }]} />
        </TweakSection>
        <TweakSection title="화면 바로가기">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
            <button className="btn sm" onClick={goMain}>S-001 대시보드</button>
            <button className="btn sm" onClick={() => onNav("S-002", { horizon: 7 })}>S-002 예측 근거</button>
            <button className="btn sm" onClick={() => onNav("S-003", { tab: "A-4" })}>S-003 정형 (A-4)</button>
            <button className="btn sm" onClick={() => onNav("S-004", { tab: "B-4" })}>S-004 비정형 (B-4)</button>
            <button className="btn sm" onClick={() => onNav("S-005")}>S-005 Graph RAG</button>
            <button className="btn sm" onClick={() => onNav("S-006")}>S-006 뉴스 목록</button>
            <button className="btn sm" onClick={() => onNav("S-007", { news: window.SIXSENSE_DATA.news[0] })}>S-007 뉴스 상세</button>
            <button className="btn sm" onClick={() => onNav("S-008", { tab: "fed" })}>S-008 거시경제</button>
            <button className="btn sm" onClick={() => onNav("S-009", { week: -3 })}>S-009 주별 스냅샷</button>
            <button className="btn sm" onClick={() => onNav("S-010")}>S-010 이벤트 목록</button>
            <button className="btn sm" onClick={() => onNav("S-011", { event: window.SIXSENSE_DATA.events[0] })}>S-011 이벤트 상세</button>
            <button className="btn sm" onClick={() => onNav("S-012")}>S-012 예측 정확도</button>
            <button className="btn sm" onClick={() => onNav("S-013", { row: window.SIXSENSE_DATA.accuracy[5] })}>S-013 당시 신호</button>
            <button className="btn sm" onClick={() => onNav("S-014")}>S-014 수집 현황</button>
          </div>
        </TweakSection>
        <TweakSection title="비교 보기">
          <div className="muted" style={{ fontSize: 11, marginBottom: 8 }}>14개 화면을 한눈에 보려면 Design Canvas로 이동.</div>
          <a className="btn sm primary" href="Sixsense Canvas.html" style={{ width: "100%", justifyContent: "center", textDecoration: "none" }}>
            14 화면 일람 (Canvas) →
          </a>
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}

function Topbar({ pageLabel, pageId, onHome, t, setTweak }) {
  const [time, setTime] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="topbar">
      <div className="brand" onClick={onHome} style={{ cursor: "pointer" }}>
        <span className="logo">S</span>
        <span>Sixsense</span>
        <span className="sub">Server DRAM Price Intelligence</span>
      </div>
      <div className="crumbs">
        <span>대시보드</span>
        {pageId !== "S-001" && (
          <>
            <span className="sep">/</span>
            <span className="now">{pageLabel}</span>
          </>
        )}
      </div>
      <div className="meta">
        <span><span className="dot"></span>매주 화요일 06:00 자동 수집</span>
        <span className="mono">마지막 갱신 · 2026-04-22 06:00</span>
        <button className="btn sm" onClick={() => setTweak("theme", t.theme === "dark" ? "light" : "dark")}>
          {t.theme === "dark" ? "☀ 라이트" : "☾ 다크"}
        </button>
      </div>
    </div>
  );
}

// Render
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
