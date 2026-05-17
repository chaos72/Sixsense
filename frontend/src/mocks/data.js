// Mock data for Sixsense DRAM dashboard
export const SIXSENSE_DATA = (() => {
  // 52-week DRAM price history + 21-week forecast
  // Generate semi-realistic price curve
  const seed = (n) => Math.sin(n * 12.9898) * 43758.5453 % 1;
  const noise = (i, amp = 0.04) => (seed(i + 1) - Math.floor(seed(i + 1))) * amp - amp / 2;

  const history = [];
  let p = 2.35;
  for (let i = 0; i < 52; i++) {
    p += noise(i, 0.06) + (i < 20 ? -0.005 : i < 35 ? 0.02 : 0.015);
    p = Math.max(2.0, Math.min(3.4, p));
    history.push({ week: i - 51, value: +p.toFixed(3), type: "actual" });
  }
  history[51].value = 3.20;

  const forecast7 = [];
  let f = 3.20;
  for (let i = 1; i <= 7; i++) {
    f += 0.065 + noise(100 + i, 0.02);
    const w = i / 7;
    forecast7.push({
      week: i,
      value: +f.toFixed(3),
      lower: +(f - 0.08 - w * 0.04).toFixed(3),
      upper: +(f + 0.08 + w * 0.04).toFixed(3),
      type: "f7",
    });
  }

  const forecast21 = [];
  let f2 = forecast7[6].value;
  for (let i = 8; i <= 21; i++) {
    f2 += 0.034 + noise(200 + i, 0.025);
    const w = (i - 7) / 14;
    forecast21.push({
      week: i,
      value: +f2.toFixed(3),
      lower: +(f2 - 0.12 - w * 0.10).toFixed(3),
      upper: +(f2 + 0.12 + w * 0.10).toFixed(3),
      type: "f21",
    });
  }
  forecast21[13].value = 4.10;

  // 14 signals
  const signalsA = [
    { id: "A-1", name: "대만 공급망", source: "TSE 공시·뉴스", value: "+8.2%", num: 0.082, tone: "pos", desc: "TSMC·UMC 가동률 상승", spark: [0.45, 0.5, 0.48, 0.6, 0.65, 0.72, 0.78, 0.82] },
    { id: "A-2", name: "빅테크 CapEx", source: "Big4 IR 공시", value: "+12.4%", num: 0.124, tone: "pos", desc: "AWS·MSFT·GOOGL·META 합산", spark: [0.3, 0.35, 0.4, 0.5, 0.62, 0.78, 0.92, 1.0] },
    { id: "A-3", name: "관세청 수출", source: "관세청 Open API", value: "-1.2%", num: -0.012, tone: "neu", desc: "메모리 반도체 수출액 MoM", spark: [0.6, 0.65, 0.7, 0.68, 0.62, 0.58, 0.55, 0.52] },
    { id: "A-4", name: "재고/출하 지수", source: "KOSIS Open API", value: "102.4", num: 102.4, tone: "alert", desc: "100 초과 = 공급과잉 (Red Alert)", spark: [82, 88, 92, 95, 97, 100.7, 101.2, 102.4] },
    { id: "A-5", name: "AWS Spot 가격", source: "AWS Pricing API", value: "+5.1%", num: 0.051, tone: "pos", desc: "p4d.24xlarge 가용성 강세", spark: [0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.68, 0.71] },
    { id: "A-6", name: "Polymarket 봉쇄확률", source: "Polymarket Public", source2: "대만해협 봉쇄 6M", value: "18%", num: 0.18, tone: "neu", desc: "지정학 리스크 확률 시장가", spark: [0.08, 0.1, 0.12, 0.14, 0.15, 0.16, 0.17, 0.18] },
    { id: "A-7", name: "구리 선물가", source: "LME Public", value: "+8.3%", num: 0.083, tone: "pos", desc: "10주 선행 → DRAM 영향", spark: [0.35, 0.42, 0.48, 0.55, 0.65, 0.72, 0.78, 0.83] },
  ];

  const signalsB = [
    { id: "B-1", name: "Earnings Call", source: "FactSet Transcripts", value: "+0.81", num: 0.81, tone: "pos", desc: "메모리 4사 콜 감성", spark: [0.42, 0.5, 0.58, 0.62, 0.7, 0.74, 0.78, 0.81] },
    { id: "B-2", name: "대만 뉴스 감성", source: "Reuters·Bloomberg 등", value: "+0.74", num: 0.74, tone: "pos", desc: "주간 평균 감성 점수", spark: [0.3, 0.4, 0.48, 0.55, 0.6, 0.65, 0.7, 0.74] },
    { id: "B-3", name: "Reddit/X", source: "Pushshift·X API", value: "+0.12", num: 0.12, tone: "neu", desc: "r/hardware DRAM 멘션", spark: [0.05, 0.08, 0.06, 0.09, 0.1, 0.11, 0.115, 0.12] },
    { id: "B-4", name: "지정학 리스크", source: "GDELT 2.0", value: "-0.68", num: -0.68, tone: "neg", desc: "수출규제·군사 뉴스 볼륨", spark: [-0.2, -0.3, -0.35, -0.4, -0.5, -0.58, -0.64, -0.68] },
    { id: "B-5", name: "LTA 비율", source: "DRAMeXchange", value: "+0.65", num: 0.65, tone: "pos", desc: "장기 계약가/현물가", spark: [0.4, 0.45, 0.5, 0.55, 0.58, 0.6, 0.62, 0.65] },
    { id: "B-6", name: "HBM/D램 믹스", source: "TrendForce", value: "+0.08", num: 0.08, tone: "neu", desc: "HBM 비중 변화", spark: [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.075, 0.08] },
    { id: "B-7", name: "BOM 신호", source: "Supply-chain 트랜스크립트", value: "+0.55", num: 0.55, tone: "pos", desc: "PCB·기판 가격 동향", spark: [0.2, 0.28, 0.35, 0.4, 0.45, 0.5, 0.52, 0.55] },
  ];

  // News this week
  const news = [
    { date: "2026-04-21", title: "삼성, DDR5 서버용 D램 2분기 15% 감산 발표", titleEn: "Samsung announces DDR5 production cuts", source: "Reuters", score: 0.87, tone: "pos", conf: 87, hot: true,
      summary: "삼성전자가 DDR5 서버용 D램 생산량을 2분기 대비 15% 감축한다고 발표. 단기 공급 감소로 현물가 상승 압력 예상. AI 서버 수요 지속 상황에서 핵심 촉매제로 작용 가능.",
      effects: { short: { tone: "pos", text: "공급 감소 즉각 반영 가능" }, mid: { tone: "pos", text: "재고 소진 시 본격 상승" }, long: { tone: "neu", text: "경쟁사 증산 여부에 달림" } },
      linked: ["A-4 재고/출하 지수와 상충 (재고 현재 과잉)", "B-1 Earnings Call 긍정 신호와 일치"] },
    { date: "2026-04-21", title: "AWS, AI 서버 인프라 투자 2027년까지 800억$ 확대", titleEn: "AWS expands AI server investment to $80B by 2027", source: "Bloomberg", score: 0.82, tone: "pos", conf: 82, hot: true,
      summary: "AWS가 향후 2년간 AI 인프라에 추가 800억 달러 투자를 발표. 핵심은 GPU 클러스터 확대로 HBM 및 DDR5 수요 견인.",
      effects: { short: { tone: "pos", text: "CapEx 신호 강화" }, mid: { tone: "pos", text: "수요 견인 본격화" }, long: { tone: "pos", text: "구조적 수요 확보" } },
      linked: ["A-2 빅테크 CapEx 신호와 정합", "A-5 AWS Spot 강세와 일치"] },
    { date: "2026-04-21", title: "BIS, 12개 중국 반도체 기업 추가 수출규제", titleEn: "US BIS expands chip export ban", source: "Reuters", score: -0.85, tone: "neg", conf: 85, hot: true,
      summary: "미국 상무부가 12개 중국 반도체 기업에 대한 수출 통제를 추가 발동. 첨단 DRAM 관련 장비·소재 수출 제한 포함.",
      effects: { short: { tone: "neg", text: "공급망 불확실성 즉각 반영" }, mid: { tone: "neu", text: "우회 공급망 구축 가능성" }, long: { tone: "pos", text: "한·대만 점유율 확대 기대" } },
      linked: ["B-4 지정학 리스크 신호 악화", "A-1 대만 공급망에 영향"] },
    { date: "2026-04-20", title: "TSMC, CoWoS 패키징 캡 30% 증설 발표", titleEn: "TSMC accelerates CoWoS expansion", source: "TechNews", score: 0.76, tone: "pos", conf: 79 },
    { date: "2026-04-20", title: "대만해협 군사 긴장 고조, 中 군용기 진입 사상최대", titleEn: "Taiwan Strait tensions rise", source: "FT", score: -0.79, tone: "neg", conf: 81 },
    { date: "2026-04-19", title: "Micron, 데이터센터 수요 견조 가이던스 상향", titleEn: "Micron lifts DC demand guidance", source: "SA", score: 0.71, tone: "pos", conf: 75 },
    { date: "2026-04-19", title: "중국 CXMT, 17nm DDR5 양산 진입 보도", titleEn: "China DRAM self-sufficiency progress", source: "Digitimes", score: -0.65, tone: "neg", conf: 68 },
    { date: "2026-04-18", title: "SK하이닉스, HBM3E 12단 양산 본격화", titleEn: "SK Hynix mass-produces HBM3E 12-Hi", source: "Korea Herald", score: 0.68, tone: "pos", conf: 78 },
    { date: "2026-04-18", title: "WTO, 한국 반도체 보조금 분쟁 패널 설치", titleEn: "WTO panel on Korean semi subsidies", source: "FT", score: -0.42, tone: "neu", conf: 64 },
    { date: "2026-04-17", title: "메타, Llama4 학습용 GPU 12만장 조달 추진", titleEn: "Meta orders 120k GPUs for Llama4", source: "The Information", score: 0.74, tone: "pos", conf: 71 },
    { date: "2026-04-17", title: "오라클, OCI Gen3 클라우드 DRAM 발주 확대", titleEn: "Oracle OCI Gen3 DRAM orders rising", source: "Bloomberg", score: 0.61, tone: "pos", conf: 70 },
    { date: "2026-04-16", title: "일본 키오시아·WD, NAND 가격 인상 협의", titleEn: "Kioxia, WD discuss NAND price hike", source: "Nikkei", score: 0.42, tone: "neu", conf: 62 },
    { date: "2026-04-16", title: "엔비디아 Rubin GPU HBM4 채택 확정", titleEn: "NVIDIA Rubin adopts HBM4", source: "Reuters", score: 0.78, tone: "pos", conf: 84 },
  ];

  // Macro indicators
  const macro = [
    { id: "fed", name: "미국 금리", value: "4.50%", change: "동결", tone: "neu", desc: "다음 FOMC 2026-05-07", history: [5.5, 5.5, 5.25, 5.0, 4.75, 4.5, 4.5] },
    { id: "dxy", name: "달러 인덱스 (DXY)", value: "104.2", change: "↑ 부정", tone: "neg", desc: "강달러 = DRAM 수출 부정", history: [98, 100, 101, 102, 103, 104, 104.2] },
    { id: "pmi", name: "글로벌 제조업 PMI", value: "52.3", change: "↑ 긍정", tone: "pos", desc: "50 초과 = 확장 국면", history: [48, 49, 50.5, 51.0, 51.5, 52.0, 52.3] },
    { id: "krw", name: "USD/KRW", value: "1,380", change: "↑ 부정", tone: "neg", desc: "원화 약세 = 수입 원가↑", history: [1310, 1325, 1340, 1355, 1370, 1375, 1380] },
    { id: "cu", name: "구리 가격 (LME)", value: "$4.82", change: "↑ 긍정", tone: "pos", desc: "10주 선행지표", history: [4.21, 4.30, 4.45, 4.55, 4.68, 4.75, 4.82] },
  ];

  // Global events
  const events = [
    { id: "ev1", type: "정치·외교", region: "미국·중국", risk: "high", title: "BIS 반도체 수출규제 강화", impact: "공급↓", date: "2026-04-21",
      summary: "미국 상무부가 12개 중국 반도체 기업에 대한 수출 통제를 추가 발동. 첨단 DRAM 관련 장비·소재 수출 제한 포함.",
      effects: { short: { tone: "neg", text: "중국발 공급망 불확실성 즉각 반영" }, mid: { tone: "neu", text: "우회 공급망 구축 가능성" }, long: { tone: "pos", text: "한국·대만 DRAM 점유율 확대 기대" } },
      links: [0, 4], affects: ["B-4", "A-1"] },
    { id: "ev2", type: "군사", region: "대만", risk: "high", title: "대만해협 군사 긴장 고조", impact: "공급↓", date: "2026-04-20",
      summary: "中 군용기 대만 방공식별구역 진입 사상 최대치 기록. TSMC·Micron 대만 공장 리스크 증가.",
      effects: { short: { tone: "neg", text: "리스크 프리미엄 즉시 반영" }, mid: { tone: "neg", text: "공급망 다변화 비용 발생" }, long: { tone: "neu", text: "장기적 점진 안정화" } },
      links: [4], affects: ["B-4", "A-1", "A-6"] },
    { id: "ev3", type: "정치·외교", region: "한국", risk: "high", title: "WTO 반도체 보조금 분쟁 제소", impact: "가격?", date: "2026-04-19",
      summary: "EU 주도 WTO 패널이 한국 반도체 보조금 분쟁 심사 개시. 최종 결정 시 가격 정책 영향 가능성.",
      effects: { short: { tone: "neu", text: "단기 직접 영향 제한" }, mid: { tone: "neu", text: "심사 결과 모니터링" }, long: { tone: "neg", text: "보조금 축소 시 원가 부담" } },
      links: [8], affects: ["A-3"] },
    { id: "ev4", type: "자연재해", region: "일본", risk: "mid", title: "구마모토 지진 피해 발생", impact: "공급↓", date: "2026-04-18",
      summary: "규모 6.2 지진으로 키오시아·소니 일부 라인 단기 중단. 48시간 내 복구 예정.",
      effects: { short: { tone: "neg", text: "NAND 일시 공급 감소" }, mid: { tone: "neu", text: "주변 라인 보완 가동" }, long: { tone: "neu", text: "구조적 영향 없음" } },
      links: [], affects: ["B-7"] },
    { id: "ev5", type: "파업", region: "미국", risk: "mid", title: "LA·롱비치 항만 노조 파업 예고", impact: "물류↑", date: "2026-04-17",
      summary: "ILWU 파업 예고로 美 서부 항만 물류 차질 가능성. 컨테이너 운임 단기 급등 우려.",
      effects: { short: { tone: "neg", text: "물류비 단기 상승" }, mid: { tone: "neu", text: "협상 진행 모니터링" }, long: { tone: "neu", text: "구조적 영향 제한" } },
      links: [], affects: ["B-7"] },
    { id: "ev6", type: "지정학", region: "중동", risk: "mid", title: "이란-이스라엘 긴장 재고조", impact: "유가↑", date: "2026-04-17",
      summary: "호르무즈 해협 인근 군사 충돌 가능성 보도. 원유·LNG 가격 상승 가능성.",
      effects: { short: { tone: "neg", text: "에너지 원가 상승" }, mid: { tone: "neu", text: "외교적 해결 가능성" }, long: { tone: "neu", text: "장기 영향 제한" } },
      links: [], affects: ["A-7"] },
    { id: "ev7", type: "경제", region: "유럽", risk: "mid", title: "독일 자동차 수요 둔화 보고", impact: "수요?", date: "2026-04-16",
      summary: "VW·BMW 자동차 부문 수요 가이던스 하향. 자동차용 DRAM 수요 영향 가능.",
      effects: { short: { tone: "neu", text: "자동차 비중 작음" }, mid: { tone: "neu", text: "지속 모니터링" }, long: { tone: "neg", text: "수요 다각화 필요" } },
      links: [], affects: [] },
    { id: "ev8", type: "정치·외교", region: "미국", risk: "low", title: "美 반도체 R&D 보조금 35억$ 승인", impact: "공급↑", date: "2026-04-15",
      summary: "CHIPS Act 후속 R&D 보조금 35억 달러 승인. 장기 미국 내 메모리 생산 확대 신호.",
      effects: { short: { tone: "neu", text: "단기 영향 제한" }, mid: { tone: "neu", text: "투자 가시화 시작" }, long: { tone: "neg", text: "공급 증가 압력" } },
      links: [], affects: [] },
    { id: "ev9", type: "경제", region: "글로벌", risk: "low", title: "AI 칩 수요 가이던스 일제 상향", impact: "수요↑", date: "2026-04-15",
      summary: "NVIDIA·AMD·인텔 일제히 AI 칩 수요 가이던스 상향. HBM·DDR5 수요 동반 강세 전망.",
      effects: { short: { tone: "pos", text: "수요 강세 확인" }, mid: { tone: "pos", text: "본격적 수요 확장" }, long: { tone: "pos", text: "구조적 성장 지속" } },
      links: [9, 11], affects: ["A-2", "B-1"] },
  ];

  // Accuracy history
  const accuracy = [
    { predDate: "2026-04-22", horizon: "7주", pred: 3.65, actual: null, error: null, tone: null },
    { predDate: "2026-04-22", horizon: "21주", pred: 4.10, actual: null, error: null, tone: null },
    { predDate: "2026-04-15", horizon: "7주", pred: 3.42, actual: null, error: null, tone: null },
    { predDate: "2026-04-08", horizon: "7주", pred: 3.10, actual: 3.20, error: 3.2, tone: "pos" },
    { predDate: "2026-04-01", horizon: "7주", pred: 3.05, actual: 3.18, error: 4.3, tone: "pos" },
    { predDate: "2026-03-25", horizon: "7주", pred: 3.00, actual: 3.18, error: 6.0, tone: "neu" },
    { predDate: "2026-03-18", horizon: "7주", pred: 2.95, actual: 3.10, error: 5.1, tone: "pos" },
    { predDate: "2026-03-11", horizon: "7주", pred: 2.90, actual: 3.25, error: 12.0, tone: "neg" },
    { predDate: "2026-03-04", horizon: "7주", pred: 2.85, actual: 2.92, error: 2.5, tone: "pos" },
    { predDate: "2026-02-25", horizon: "7주", pred: 2.80, actual: 2.96, error: 5.7, tone: "pos" },
    { predDate: "2026-04-08", horizon: "21주", pred: 3.80, actual: null, error: null, tone: null },
    { predDate: "2026-04-01", horizon: "21주", pred: 3.72, actual: null, error: null, tone: null },
    { predDate: "2026-03-25", horizon: "21주", pred: 3.65, actual: null, error: null, tone: null },
    { predDate: "2026-02-04", horizon: "21주", pred: 2.95, actual: 3.18, error: 7.8, tone: "neu" },
    { predDate: "2026-01-28", horizon: "21주", pred: 2.90, actual: 3.20, error: 10.3, tone: "neg" },
  ];

  // S-009 signal snapshot at past date
  const snapshotPast = {
    date: "2026-03-25",
    actual: 3.18,
    predicted: 3.00,
    error: 6.0,
    signals: [
      { id: "A-1", name: "대만 공급망", then: "+0.12", thenTone: "neu", now: "+0.82", nowTone: "pos", direction: "up", change: "크게 개선" },
      { id: "A-2", name: "빅테크 CapEx", then: "+0.31", thenTone: "neu", now: "+0.74", nowTone: "pos", direction: "up", change: "개선" },
      { id: "A-3", name: "관세청", then: "+0.45", thenTone: "pos", now: "-0.012", nowTone: "neu", direction: "down", change: "소폭 약화" },
      { id: "A-4", name: "재고지수", then: "91.2", thenTone: "pos", now: "102.4", nowTone: "alert", direction: "down", change: "악화" },
      { id: "A-5", name: "AWS Spot", then: "+0.18", thenTone: "neu", now: "+0.51", nowTone: "pos", direction: "up", change: "개선" },
      { id: "A-6", name: "Poly", then: "22%", thenTone: "neu", now: "18%", nowTone: "neu", direction: "flat", change: "유사" },
      { id: "A-7", name: "구리", then: "$4.21", thenTone: "neu", now: "$4.82", nowTone: "pos", direction: "up", change: "개선" },
      { id: "B-1", name: "실적콜", then: "+0.51", thenTone: "pos", now: "+0.81", nowTone: "pos", direction: "up", change: "강화" },
      { id: "B-2", name: "대만뉴스", then: "+0.22", thenTone: "neu", now: "+0.74", nowTone: "pos", direction: "up", change: "크게 개선" },
      { id: "B-3", name: "Reddit", then: "+0.08", thenTone: "neu", now: "+0.12", nowTone: "neu", direction: "flat", change: "유사" },
      { id: "B-4", name: "지정학", then: "-0.31", thenTone: "neu", now: "-0.68", nowTone: "neg", direction: "down", change: "악화" },
      { id: "B-5", name: "LTA비율", then: "+0.42", thenTone: "pos", now: "+0.65", nowTone: "pos", direction: "up", change: "강화" },
      { id: "B-6", name: "HBM/D램", then: "+0.11", thenTone: "neu", now: "+0.08", nowTone: "neu", direction: "flat", change: "유사" },
      { id: "B-7", name: "BOM", then: "+0.19", thenTone: "neu", now: "+0.55", nowTone: "pos", direction: "up", change: "개선" },
    ],
  };

  // Collection status
  const collection = {
    summary: { total: 70, success: 70, fail: 0, newCount: 1247 },
    week: "2026-04-22",
    groupA: [
      { id: "A-1", name: "대만 공급망", source: "TSE 공시·뉴스 크롤", time: "2026-04-22 06:02", newItems: 47, prev: 41, status: "ok" },
      { id: "A-2", name: "빅테크 CapEx", source: "Big4 IR API", time: "2026-04-22 06:01", newItems: 12, prev: 4, status: "ok" },
      { id: "A-3", name: "관세청 수출", source: "관세청 Open API", time: "2026-04-22 06:00", newItems: 1, prev: 1, status: "ok" },
      { id: "A-4", name: "재고/출하 지수", source: "KOSIS Open API", time: "2026-04-22 06:00", newItems: 1, prev: 1, status: "ok" },
      { id: "A-5", name: "AWS Spot", source: "AWS Pricing API", time: "2026-04-22 06:03", newItems: 168, prev: 168, status: "ok" },
      { id: "A-6", name: "Polymarket", source: "Polymarket Public", time: "2026-04-22 06:01", newItems: 7, prev: 7, status: "ok" },
      { id: "A-7", name: "구리 (LME)", source: "LME Public", time: "2026-04-22 06:00", newItems: 5, prev: 5, status: "ok" },
    ],
    groupB: [
      { id: "B-1", name: "Earnings Call", source: "FactSet Transcripts", time: "2026-04-22 06:08", newItems: 8, prev: 6, status: "ok" },
      { id: "B-2", name: "대만 뉴스", source: "Reuters·Bloomberg 등", time: "2026-04-22 06:12", newItems: 142, prev: 128, status: "ok" },
      { id: "B-3", name: "Reddit/X", source: "Pushshift·X API", time: "2026-04-22 06:15", newItems: 824, prev: 802, status: "ok" },
      { id: "B-4", name: "지정학 (GDELT)", source: "GDELT 2.0", time: "2026-04-22 06:18", newItems: 74, prev: 51, status: "ok" },
      { id: "B-5", name: "LTA 비율", source: "DRAMeXchange", time: "2026-04-22 06:05", newItems: 1, prev: 1, status: "ok" },
      { id: "B-6", name: "HBM/D램 믹스", source: "TrendForce", time: "2026-04-22 06:04", newItems: 1, prev: 1, status: "ok" },
      { id: "B-7", name: "BOM 신호", source: "공급망 트랜스크립트", time: "2026-04-22 06:09", newItems: 56, prev: 48, status: "ok" },
    ],
  };

  return {
    meta: {
      current: 3.20,
      currentChange: "+2.5%",
      pred7: 3.65, pred7Change: "+14.1%",
      pred21: 4.10, pred21Change: "+28.1%",
      updated: "2026-04-22 (화) 06:00",
      model: "prophet_v2.1",
      confidence: 81,
    },
    history, forecast7, forecast21,
    signalsA, signalsB,
    news, macro, events, accuracy,
    snapshotPast, collection,
  };
})();
