// 화면 40개 자동 검사 실행기 (v2.6.1 재발 방지 장치 3) — 사람 없이 돌아간다.
// 개발 서버를 띄우고 headless 브라우저에서 scripts/screen-check.js 를 그대로 실행한다(시간 제한 없이 한 번에).
// 사용: (frontend 폴더에서) node scripts/screen-check-run.mjs     → 통과 0, 실패 1
import { spawn } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from '@playwright/test'

const FRONT = join(dirname(fileURLToPath(import.meta.url)), '..')
const PORT = Number(process.env.SCREEN_CHECK_PORT || 5199)
const BASE = `http://localhost:${PORT}`

const server = spawn('npx', ['vite', '--port', String(PORT), '--strictPort'], { cwd: FRONT, stdio: 'ignore' })
const stop = () => { try { server.kill('SIGTERM') } catch { /* 이미 종료 */ } }

async function waitForServer(timeoutMs = 60000) {
  const t0 = Date.now()
  while (Date.now() - t0 < timeoutMs) {
    try { if ((await fetch(BASE)).ok) return } catch { /* 아직 준비 안 됨 */ }
    await new Promise((r) => setTimeout(r, 500))
  }
  throw new Error(`개발 서버가 ${timeoutMs / 1000}초 안에 뜨지 않음`)
}

let code = 1
try {
  await waitForServer()
  const browser = await chromium.launch()
  const page = await browser.newPage()
  const pageErrors = []
  page.on('pageerror', (e) => pageErrors.push(String(e).slice(0, 120)))
  await page.goto(BASE)
  const src = readFileSync(join(FRONT, 'scripts', 'screen-check.js'), 'utf8')
  const out = JSON.parse(await page.evaluate(`(async () => { ${src}; return await screenCheck(0); })()`))
  await browser.close()
  const ok = out.통과 && pageErrors.length === 0
  console.log(`[화면 검사] ${out.검사한_화면}/${out.전체}개 · 문제 ${out.bad.length} · 모바일 넘침 ${out.over.length} · ` +
              `불합격 표시 누락 ${out.fcNoFail.length} · 페이지 오류 ${pageErrors.length} → ${ok ? '✅ 통과' : '❌ 실패'}`)
  for (const b of out.bad) console.log('  ❌', JSON.stringify(b))
  for (const o of out.over) console.log('  ❌ 모바일 넘침', JSON.stringify(o))
  for (const q of out.fcNoFail) console.log('  ❌ 예측이 보이는데 불합격 표시 없음', q)
  for (const e of pageErrors) console.log('  ❌ 페이지 오류', e)
  code = ok ? 0 : 1
} catch (e) {
  console.log('  ❌ 화면 검사 실행 실패:', e.message)
} finally {
  stop()
}
process.exit(code)
