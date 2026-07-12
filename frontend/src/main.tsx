import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
// Hand-off styles (single source of truth — replaces tokens.css + globals.css)
import './styles/styles.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// PWA — 서비스 워커 등록 (홈 화면 설치 + 오프라인 지원). 배포(프로덕션) 환경에서만 활성.
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}
