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
