// Playwright config — Sixsense L2/L3 tests
// Design Ref: Design §8 Test Plan (L2 UI Action / L3 E2E)
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false, // dev server, sequential for stability
  retries: 0,
  workers: 1,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]],
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    viewport: { width: 1440, height: 900 },
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Servers are expected to be running externally:
  //   - Frontend dev:  npm run dev (port 5173)
  //   - Backend FastAPI: ../backend/.venv/bin/uvicorn ... (port 8000)
})
