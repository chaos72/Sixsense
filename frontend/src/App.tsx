// PORTED FROM: design_handoff_sixsense_dram_dashboard/Sixsense.html
// Thin TS wrapper that mounts the hand-off App (JSX, ported from src/app.jsx).
// Design Ref: PRD §07 Direct Port Strategy, Do v0.2
// @ts-expect-error — JSX module without explicit types (intentional, do.md §5.4)
import HandoffApp from './screens/app.jsx'

export default function App() {
  return <HandoffApp />
}
