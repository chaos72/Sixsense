# Handoff: Sixsense — Server DRAM Price Intelligence Dashboard

## Overview

**Sixsense (식스센스)** is a B2B intelligence dashboard for forecasting server-grade DDR5 DRAM prices. The target user is a memory/semiconductor **strategy/planning team** who needs to make price calls based on 14 proxy signals (formal + informal data), AI predictions (1–7 week / 8–21 week), macroeconomic indicators, and geopolitical events.

The system is built around a **weekly auto-collection cycle** (every Tuesday 06:00 KST) and exposes 14 distinct screens that drill into the AI prediction logic, the underlying signals, news/event analysis, and the prediction-accuracy track record.

## About the Design Files

The files in this bundle are **design references created in HTML** — interactive prototypes that show the intended look, behavior, layout, and interactions. They are **not production code to copy directly**.

The task is to **recreate these HTML designs in the target codebase's existing environment** (React/Next.js, Vue, etc.) using its established patterns, design system, and component library. If no production environment exists yet, **React + TypeScript with a charting library (e.g., Recharts, Visx, or D3) is the recommended choice** given the data-density and chart-heavy nature of the UI.

Look at how `src/dashboard.jsx`, `src/modals.jsx`, `src/pages.jsx`, and `src/components.jsx` are structured — these reflect the intended component decomposition, but the implementation should use the target codebase's idioms (hooks, server components, state management, etc.).

## Fidelity

**High-fidelity (hifi).** The prototypes are pixel-accurate with:
- Final color palette (light + dark theme)
- Korean-first typography stack (Pretendard Variable + Inter for Latin/numbers + JetBrains Mono for code/values)
- Exact spacing, radii, and shadows
- Working interactions (modal stack, tabs, filters, chart range filter, theme toggle, density toggle, deep-linking via URL params)
- Realistic mock data (52-week DRAM price history, 21-week forecasts with confidence bands, 14 signal time series, news, events, accuracy history)

Recreate the UI **pixel-perfectly** within the codebase's existing libraries and patterns. The numbers in the mocks are placeholders — they should be wired to the real data API.

---

## Screen Map (14 screens)

| ID    | Type       | Name                              | Purpose                                                                                                                    |
| ----- | ---------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| S-001 | Full page  | 메인 대시보드                      | Entry point — current price + 1-7w/8-21w AI forecasts + 14 proxy signals + Graph RAG + events + accuracy + collection.     |
| S-002 | Modal      | AI 예측 근거 상세                  | Two-tab modal showing 14-signal contribution bars, confidence intervals, weekly forecast table, AI summary. + HITL panel.  |
| S-003 | Modal      | 정형 데이터 Group A 상세           | 7-tab modal (A-1…A-7). Per-signal 28-week trend chart + raw data table + AI interpretation. A-4 fires Red Alert at >100.   |
| S-004 | Modal      | 비정형 데이터 Group B 상세         | 7-tab modal (B-1…B-7). Per-signal 8-week sentiment trend + news article list + AI interpretation.                          |
| S-005 | Modal      | Graph RAG — 구리 ↔ DRAM 상관관계   | 52-week copper vs DRAM overlay + lead-time correlation bars + causal path diagram (PCB → packaging → DC investment).       |
| S-006 | Full page  | AI 뉴스 분석 전체 목록             | Filterable/sortable table of all collected news (by sentiment, source, date).                                              |
| S-007 | Modal      | 뉴스 원문 & AI 분석 상세           | Per-article AI summary + short/mid/long-term DRAM impact judgment + linked signals + open-source link.                     |
| S-008 | Full page  | 거시경제 지표 통합                  | 5-tab page (Fed Rate / DXY / PMI / USD/KRW / Copper). Per-indicator 52-week trend + monthly raw + DRAM correlation note.   |
| S-009 | Modal      | 주별 신호 스냅샷                    | Drill-down from chart click. Past week: shows the 14-signal state at that time + error vs actual. Future week: forecast.   |
| S-010 | Full page  | 글로벌 이벤트 전체 목록             | Filterable list of detected geopolitical/economic events with risk level + DRAM impact direction.                         |
| S-011 | Modal      | 글로벌 이벤트 상세                  | Per-event AI summary + short/mid/long-term DRAM impact + linked news articles + affected signals.                          |
| S-012 | Full page  | AI 예측 정확도 전체 이력            | MAPE tracking — line chart of cumulative error trend + filterable history table (7w / 21w / all).                         |
| S-013 | Modal      | 당시 신호 vs 현재 신호 비교         | For a past prediction, side-by-side 14-signal comparison (then vs now) + AI explanation of error source.                  |
| S-014 | Full page  | 데이터 수집 현황 상세               | Per-signal collection status (source, last-collected timestamp, new items, week-over-week delta, success/fail).            |

---

## Layout — S-001 Main Dashboard (the canonical screen)

**Page width**: `max-width: 1480px`, centered, `padding: 28px 24px 80px` (comfortable density) / `16px 20px 60px` (compact).

**Topbar**: 56px height, sticky, full-bleed white background, 1px bottom border. Contains brand (logo + "Sixsense" + subtitle "Server DRAM Price Intelligence"), breadcrumb, then right-aligned meta (auto-collection status, last-updated timestamp, theme toggle button).

**Content sections** (top-to-bottom, vertical stack with `margin-bottom: 28px`):

1. **가격 스냅샷 (Price Snapshot)** — 3-column grid, equal width
   - Card 1: 현재 계약가 — big mono number `$3.20` / unit `/ GB` / change `▲ +2.5% 전주 대비` / footer code `SPOT · DDR5 8Gb`.
   - Card 2: 1~7주 AI 예측가 — `$3.65` / `+14.1% 예상` / footer `prophet_v2.1 · 신뢰 81%`. **Clickable** → opens S-002 modal with horizon=7.
   - Card 3: 8~21주 AI 예측가 — `$4.10` / `+28.1% 예상` / footer `prophet_v2.1 · 신뢰 74%`. **Clickable** → S-002 horizon=21.
   - Tappable cards get `🔍 클릭` indicator in card-h.

2. **DRAM 52주 히스토리 + AI 예측** — single card containing a line chart.
   - Section header has a segmented control on the right with 3 options: `단기 1~7주` / `중장기 8~21주` / `전체`.
   - **Range filter is dynamic** — clicking changes the chart's x-axis range AND which forecast lines are visible:
     - `short`: 26w history + 1~7w forecast (blue dashed line + blue confidence band)
     - `mid`: 13w history + 1~7w forecast (blue, contextual) + **8~21w forecast (pastel green, emphasized — thicker line 2.6, larger dots)**
     - `all`: full 52w history + both forecasts (1~7w blue dashed, 8~21w pastel green dashed)
   - Reference line at `현재 $3.20` (current price), dashed, neutral color.
   - Future forecast points have clickable dots → opens S-009 modal with the clicked week.
   - Legend row below chart adapts to range mode.

3. **14개 프록시 신호 통합 현황** — section header with sub-headers `Group A · 정형 (7종)` and `Group B · 비정형 (7종)`, each with its own 7-column grid of signal cards.
   - Each signal card: ID code (top-left), tone badge (top-right: 긍정 / 중립 / 부정 / ALERT for A-4 only), label, big mono value, sparkline below.
   - **All signal cards clickable** → opens S-003 (Group A) or S-004 (Group B) with the clicked tab pre-selected.

4. **Graph RAG — 구리 vs DRAM 선행 영향도** — 2-column grid inside card.
   - Left: mini overlay chart (copper blue vs DRAM black, 104 weeks).
   - Right: big correlation coefficient `+0.72`, lead time `10주`, AI commentary in `.ai-note` callout.
   - Section header has `상세 분석 →` button to S-005 modal.

5. **AI 뉴스 & 감성 분석** + **거시경제 지표** — 2-column grid.
   - News card: stacked list of 3 hot news items. Each item: tone badge + title + source + score. Clickable → S-007 modal.
   - Macro card: stacked list of 5 indicators. Each: name + value + tone change + description. Clickable → S-008 page.

6. **글로벌 이벤트 모니터링** + **AI 예측 정확도 트래킹** — 2-column grid.
   - Events: 3 hot event chips. Clickable → S-011 modal.
   - Accuracy: 3 recent completed predictions in tight horizontal layout (`Nw전 | 예측 $X.XX | → | 실제 $Y.YY | 오차 Z.Z% | 당시 신호 →`). Clickable → S-013 modal.

7. **이번 주 새 수집 데이터 현황** — single "foot-bar" row (1px-border light card) with stat-pipe layout: `정형 241건 ✓ | 비정형 1106건 ✓ | 수집실패 0건 | 사이클 매주 화요일 06:00 KST | 다음 수집까지 6일 22시간`.

---

## Design Tokens

### Colors — Light Theme (default)

```css
--bg:            #fafaf8;   /* warm white, page background */
--bg-elev:       #f4f3ef;
--surface:       #ffffff;
--surface-2:     #fafaf8;   /* subtle alt for hover, table headers, etc. */
--border:        #e8e6e0;
--border-strong: #d8d4cc;

--text:          #1a1a1a;
--text-mid:      #4a4a48;
--text-dim:      #8a8884;
--text-faint:    #b8b6b0;

--accent:        #1a1a1a;   /* monochrome — used for active tab underline, primary button */
--grid:          #efede8;   /* chart grid lines */

/* Signal tones */
--sig-pos:       #16a34a;   --sig-pos-bg:   #ecfdf5;
--sig-neu:       #ca8a04;   --sig-neu-bg:   #fefce8;
--sig-neg:       #dc2626;   --sig-neg-bg:   #fef2f2;
--sig-alert:     #b91c1c;   --sig-alert-bg: #fee2e2;
--sig-info:      #2563eb;   --sig-info-bg:  #eff6ff;   /* 1~7w forecast color */

/* Forecast emphasis (8~21w) */
--forecast-mid:    #10b981;
--forecast-mid-bg: #d1fae5;
```

### Colors — Dark Theme

```css
--bg:            #0f0f10;
--bg-elev:       #161618;
--surface:       #1a1a1c;
--surface-2:     #202023;
--border:        #2a2a2d;
--border-strong: #3a3a3e;

--text:          #f4f3ef;
--text-mid:      #c6c4be;
--text-dim:      #8a8884;
--text-faint:    #5a5853;

--accent:        #f4f3ef;
--grid:          #232326;

--sig-pos:       #4ade80;   --sig-pos-bg:   rgba(22, 163, 74, 0.14);
--sig-neu:       #fbbf24;   --sig-neu-bg:   rgba(202, 138, 4, 0.16);
--sig-neg:       #f87171;   --sig-neg-bg:   rgba(220, 38, 38, 0.14);
--sig-alert:     #ef4444;   --sig-alert-bg: rgba(185, 28, 28, 0.18);
--sig-info:      #60a5fa;   --sig-info-bg:  rgba(37, 99, 235, 0.14);
--forecast-mid:  #6ee7b7;   --forecast-mid-bg: rgba(16, 185, 129, 0.18);
```

### Typography

```
Font stack:
  Sans   — "Pretendard Variable", Pretendard, Inter, -apple-system, sans-serif
  Mono   — "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace
```

Pretendard is a Korean-optimized variable font with good Latin coverage — use it as the primary stack. JetBrains Mono is used for ALL numeric values (`.num` class applies font-family + `font-variant-numeric: tabular-nums` + `letter-spacing: -0.01em` + `white-space: nowrap`).

```
Type scale:
  Base body:            13px / 1.5    (12px in compact density)
  Big metric value:     26px / 1.1    weight 600  (22px in compact)
  Section title:        15px          weight 600
  Page title (h1):      22px          weight 700
  Card label:           13px          weight 500
  Card-h / dlabel:      11px          weight 500   UPPERCASE  letter-spacing 0.02em
  Tab:                  13px          weight 500 (600 when active)
  Button:               12px          weight 500
  Table th:             11px          weight 500   UPPERCASE
  Table td:             12px
  Mono code small:      10px          weight 500
```

CSS uses `word-break: keep-all` on body to prevent mid-word breaks in Korean text. Important — without this, Korean text wraps awkwardly.

### Spacing & Layout

```
Density: comfortable (default)            compact
  --pad-x:    20px                        14px
  --pad-y:    16px                        10px
  --gap:      14px                        8px
  --row-h:    36px                        28px
```

Density toggles via `[data-density="compact"]` on `<html>`.

### Radii

```
--radius-sm:  4px
--radius:     6px         (default for cards, buttons, inputs)
--radius-lg:  10px        (modals)
```

### Shadows

```
--shadow-sm: 0 1px 2px rgba(20,18,12,0.04)
--shadow:    0 2px 8px rgba(20,18,12,0.06), 0 1px 2px rgba(20,18,12,0.04)
--shadow-lg: 0 12px 40px rgba(20,18,12,0.16), 0 4px 12px rgba(20,18,12,0.08)
```

Dark mode uses pure black shadows at higher opacity (0.4 / 0.6).

---

## Components

All components live in `src/components.jsx` and the screen-specific files. Key components to recreate:

### `<Sig tone="pos|neu|neg|alert|info">{label}</Sig>`
Signal badge. Pill with 6px dot + label. `.sig.alert` has pulsing animation. Used everywhere for sentiment, risk levels, status.

### `<Sparkline data={number[]} tone="pos|neg|neu|alert" height={28} />`
Inline mini-chart. Last point gets a dot. Light-toned area fill under line.

### `<MetricCard label code value unit change changeTone sub onClick>`
The big number card. Header row (label left, optional code badge right), big mono value + unit, change indicator with up/down arrow in tone color, optional code footer below a divider.

### `<LineChart width height series bands refLines xLabels yDomain padding>`
The workhorse chart. SVG-based. Series support `dashed`, `dots`, `strokeWidth`, `dotR`, `onDotClick`, `endLabel`. Bands are confidence intervals (polygon between upper/lower paths). RefLines are horizontal reference lines with optional labels.

**Critical**: when implementing in production, swap this for a real charting library (Recharts/Visx/D3) but preserve the same series prop shape so screens don't need to change.

### `<Modal title badge onClose size>`
Modal shell. Fixed overlay with backdrop-blur, centered modal panel with header (title + S-XXX badge + ✕ close), scrollable body, optional footer. ESC closes, click-outside closes, body scroll-locked while open. **Modal stack**: multiple modals can layer (e.g., S-011 → S-007).

### `<Tabs tabs active onChange>`
Top tab strip. Each tab has `id`, optional `code` (mono small), `label`. Active tab has accent underline.

### `<Seg options value onChange>`
Segmented control (chart range, etc.). Pill-like background, active option gets white surface + shadow.

### `<HITL rules={[{id, label, tone, desc, value, step, unit}]} />`
**Human-In-The-Loop panel** — appears at the bottom of every detail screen (S-002, S-003, S-004, S-006, S-007, S-008, S-009, S-010, S-011, S-012, S-013). Dashed-border subtle panel. Header: "AI 판단 근거 기준 조정 — HITL · 임계치(Threshold) / 가중치(Weight) 수정". Three rules by default (긍정 / 중립 / 부정) each with a tone badge, description, numeric input, unit, and `초기화` / `저장 & 재학습` action buttons.

This is a core product concept — users adjust the AI's classification thresholds and re-train.

### `<AiNote label source>{children}</AiNote>`
The Claude-generated commentary callout. Left-border accent (using `--accent`), surface-2 background, uppercase mini-label "AI 종합 판단 · Claude 자동 생성". Used everywhere AI output is shown.

### `<BarRow rank code label pct tone>`
Single row of the signal-contribution bar chart in S-002. Grid: 80px label + 1fr bar track + 60px pct + 50px badge.

### `<Tweaks Panel>`
Floating bottom-right panel (toggleable). In production, this should be replaced by an admin/settings page — it's only a prototype tool here. Contains theme toggle, density toggle, and dev shortcuts to all 14 screens.

---

## Interactions & Behavior

### Routing / navigation

- **Full pages**: `S-001`, `S-006`, `S-008`, `S-010`, `S-012`, `S-014` — these replace the current view in the same window.
- **Modals**: `S-002`, `S-003`, `S-004`, `S-005`, `S-007`, `S-009`, `S-011`, `S-013` — these overlay the current page. Multiple can stack. Close one returns to the underlying page or modal.

The prototype uses URL query params for deep-linking (used by the Design Canvas iframes):
```
?screen=S-008&tab=fed
?screen=S-001&modal=S-002&horizon=7
?screen=S-001&modal=S-003&tab=A-4
?screen=S-001&modal=S-007&newsIdx=0
?screen=S-001&modal=S-011&eventIdx=0
?screen=S-001&modal=S-013&rowIdx=5
```

In production, use the codebase's routing (React Router / Next.js App Router / Vue Router). Full pages should be real routes; modals can be route-as-modal (`/news/:id` parallel route in Next, or query-param controlled) or in-app state — match the codebase convention.

### Chart range filter (S-001 chart)

Three-way segmented control filters the DRAM history+forecast chart. State lifted up to the Dashboard component.
- `short` → 26w history + only 1~7w forecast (blue dashed + blue band)
- `mid`   → 13w history + 1~7w forecast (blue, context) + 8~21w forecast (**pastel green emphasis** — solid line, thicker stroke 2.6, larger dots 3.5px, green confidence band)
- `all`   → 52w history + 1~7w (blue dashed) + 8~21w (pastel green dashed)

The mid view is the most stylistically distinctive — the 8~21w segment is drawn solid (not dashed) and thicker to emphasize the focus range.

### Chart point clicks

Future-week forecast points (dots in blue/green segments) are clickable. Clicking opens S-009 modal with the week as a parameter. The S-009 modal shows either a past-week snapshot (14 signal state then vs now) or a future-week prediction breakdown.

### Theme toggle

`document.documentElement.dataset.theme = "light" | "dark"`. CSS variables drive everything. Toggle button in topbar right side AND in Tweaks panel.

### Density toggle

`document.documentElement.dataset.density = "comfortable" | "compact"`. Affects padding, gap, row height, base font size, big-number font size.

### Filter chips (S-006, S-010)

Chip-style filter buttons with active state. List filters by tone/risk. Plus dropdown filters by source/type. Plus sort dropdown (영향도순 / 신뢰도순 / 발행일순). Results count on right (`13건 표시`).

### Modal escape

ESC key closes top modal. Click on `.modal-overlay` (outside `.modal`) closes top modal. ✕ button closes.

### Hover states

- Tappable cards: `transform: translateY(-1px)`, `border-color: var(--border-strong)`, shadow appears. Transition 0.12s.
- Buttons: subtle bg darken via `--surface-2`.
- Table rows (clickable): `background: var(--surface-2)` on `tr.tappable:hover td`.
- Chart dots: `r` increases from 3 → 5 on hover (CSS transition).

---

## State Management

Recreate with the codebase's state pattern (Zustand / Redux / Context / server state). At minimum:

**Global / route state**
- `currentRoute` — which screen (S-001 / S-006 / etc.)
- `modalStack` — array of `{ id: 'S-002', params: {...} }` for layered modals
- `theme` — `"light" | "dark"` — persist to localStorage
- `density` — `"comfortable" | "compact"` — persist to localStorage

**Per-screen state (S-001)**
- `chartRange` — `"short" | "mid" | "all"`

**Per-screen state (S-006)**
- `filter` — sentiment filter
- `source` — source filter
- `sort` — sort key

**Per-screen state (S-010)**
- `risk` — risk-level filter
- `type` — event-type filter

**Per-screen state (S-012)**
- `filter` — horizon filter (all / 7 / 21)

**Data fetching**
- All data is currently mocked in `src/data.js`. In production, expect:
  - `GET /api/snapshot` — current price + forecasts + meta (model, confidence, updated timestamp)
  - `GET /api/history` — 52-week price history + forecast bands
  - `GET /api/signals` — 14 signals with current values, tones, sparklines
  - `GET /api/signals/:id` — full signal detail (28-week trend, raw data, AI interpretation)
  - `GET /api/news` — paginated news with filters
  - `GET /api/news/:id` — full article + AI analysis
  - `GET /api/macro` — 5 macro indicators
  - `GET /api/macro/:id` — full macro detail (52-week trend, monthly raw)
  - `GET /api/events` — events with filters
  - `GET /api/events/:id` — event detail + linked news + affected signals
  - `GET /api/forecast/:horizon` — forecast detail (contributions, weekly table, AI summary)
  - `GET /api/accuracy` — accuracy history (paginated)
  - `GET /api/accuracy/:date/:horizon` — accuracy detail (then vs now signal compare)
  - `GET /api/collection` — collection status for the current week
  - `POST /api/hitl/rules` — save user-adjusted thresholds + trigger re-training
- Use React Query / SWR / TanStack Query — most screens benefit from caching since the data updates only weekly.

---

## Assets

- **Fonts**: Pretendard Variable (loaded from jsdelivr CDN) — replace with self-hosted in production. Inter, JetBrains Mono from Google Fonts.
- **Icons**: SVG inline (search, settings, arrows). No icon library used.
- **Images / logos**: None. Brand logo is a CSS-only `S` glyph in a 22px square with mono font.
- **Mock data**: `src/data.js` — all numbers are realistic placeholders. Do not ship; wire to real API.

---

## Files in this bundle

```
Sixsense.html               — Main interactive prototype entry point. Loads all src/*.jsx via Babel.
Sixsense Canvas.html        — Design Canvas: 14 screens laid out side-by-side as zoomable artboards (iframes).
design-canvas.jsx           — DesignCanvas / DCSection / DCArtboard components (starter — only used by Canvas.html).

src/styles.css              — All CSS. Design tokens at top, then component styles.
src/data.js                 — Mock data (history, signals, news, events, macro, accuracy, collection).
src/components.jsx          — Shared components: Sig, Sparkline, Modal, MetricCard, Tabs, Seg, HITL, AiNote, BarRow, LineChart, etc.
src/dashboard.jsx           — S-001 main dashboard layout + DramChart + ChartRangeSeg + SignalCard + GraphRagMini.
src/modals.jsx              — S-002, S-003, S-004, S-005, S-007, S-009, S-011, S-013 (modal-based screens).
src/pages.jsx               — S-006, S-008, S-010, S-012, S-014 (full-page screens).
src/app.jsx                 — Root: routing, modal stack, theme/density wiring, deep-link URL parsing, Tweaks panel.
src/tweaks-panel.jsx        — Tweaks panel framework (starter component — strip in production, replace with admin).
```

---

## Implementation Notes & Pitfalls

1. **Korean line-breaking is fragile.** Always set `word-break: keep-all` on prose containers. For numeric values, `white-space: nowrap`. This prevents Korean labels and dollar values from breaking mid-content. The prototype had to fight this — see `src/styles.css` `.num`, `.card-big`, `.card-h`, `.card-label`.

2. **Modal stack ordering.** Each modal is a separate fixed-position overlay. Stacking via array. ESC and click-outside should only close the topmost modal. Body scroll lock should only release when stack is empty.

3. **Chart confidence bands stacking with CSS opacity.** The `.band` SVG polygon uses CSS `opacity: 0.13` for visual subtlety. **Do not** add a `fillOpacity` prop on top — it multiplies and the band becomes invisible. Use solid CSS opacity only. (This was a fixed bug.)

4. **`useTweaks` returns a tuple `[values, setTweak]`**, NOT an object. Always destructure: `const [t, setTweak] = useTweaks(defaults);`. If you treat it as an object (`t.setTweak`), every persist call silently no-ops.

5. **HITL panel appears on every detail screen.** Do not duplicate this UI — make it a shared component that takes a rule schema. The default rules are 긍정 ≥ 0.30 / 중립 ± 0.15 / 부정 ≤ -0.30. Saving should be a single API call.

6. **A-4 Red Alert** is a special case. When `재고/출하 지수 > 100`, the signal card on S-001 shows an `alert` tone (red with pulsing dot) instead of pos/neu/neg, and S-003 with `tab=A-4` shows a top banner. Build this rule into the signal classifier.

7. **Density toggle is real**, not cosmetic. The CSS variables `--pad-x`, `--pad-y`, `--gap`, `--row-h`, `--font-base`, `--font-num` all change. Tables, cards, content padding — all respond. Use the same approach: `[data-density="compact"]` selector overrides at the `:root` level.

8. **Forecast colors are semantically meaningful.** Blue `var(--sig-info)` is short-horizon (1~7w). Pastel green `var(--forecast-mid)` is mid-horizon (8~21w). Don't swap or merge them.

9. **All numbers use `.num` class** with mono font + tabular-nums + nowrap. This is a strict rule across the design.

10. **Tweaks panel is dev-only.** In production, theme/density should live in user settings, and there should be no floating panel.

---

## Next Steps for the Developer

1. Open `Sixsense.html` in a browser to see the full prototype. Use the Tweaks panel (bottom-right) to navigate quickly between all 14 screens.
2. Open `Sixsense Canvas.html` to see all 14 screens laid out side-by-side (zoom/pan with mouse wheel).
3. Read `src/data.js` to understand the data shape. Mirror it in your API types.
4. Implement the shared components first (Sig, MetricCard, LineChart with bands, Modal, Tabs, HITL, AiNote) — these are used everywhere.
5. Build S-001 first — it's the integration point that proves the data layer, routing, and theme system all work.
6. Layer in the modals one screen at a time, then the full pages.
7. Wire HITL save endpoint last (it requires backend changes).

---

**Questions?** The prototype is fully working — when in doubt, open the HTML files and inspect the live behavior.
