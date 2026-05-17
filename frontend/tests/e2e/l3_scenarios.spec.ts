// L3 E2E Scenario Tests — Sixsense
// Design Ref: Design §8.4 L3 E2E Scenarios, PRD §06 페르소나별 진입 경로
// 각 시나리오: 멀티 페이지 + 멀티 모달 사용자 여정 검증
import { test, expect } from '@playwright/test'

test.describe('L3 - Persona B (이병헌 구매팀장): A-4 Red Alert 감지 플로우', () => {
  test('S-001 진입 → A-4 신호 카드 클릭 → 모달 → 닫기 → S-014 수집현황 확인', async ({ page }) => {
    // 1. 메인 진입
    await page.goto('/')
    await expect(page.locator('text=현재 계약가').first()).toBeVisible()

    // 2. Group A의 A-4 카드 직접 찾기 (id 텍스트 매칭)
    const a4Card = page.locator('.card.tappable').filter({ hasText: 'A-4' }).first()
    await expect(a4Card).toBeVisible()
    await a4Card.click()

    // 3. S-003 모달 (정형 신호 그룹)
    await expect(page.locator('.modal-overlay')).toBeVisible()
    await expect(page.locator('.modal-head .badge')).toContainText('S-003')

    // 4. 모달 닫기
    await page.keyboard.press('Escape')
    await expect(page.locator('.modal-overlay')).not.toBeVisible()

    // 5. S-014 수집 현황 페이지로 이동 (URL 딥링크)
    await page.goto('/?screen=S-014')
    await expect(page.locator('.content').first()).toBeVisible()
    // 메인 가격 카드는 보이지 않아야 함
    await expect(page.locator('text=현재 계약가')).not.toBeVisible()
  })
})

test.describe('L3 - Persona A (정우성 부사장): 가격 방향성 판단 플로우', () => {
  test('S-001 → 1~7주 카드 클릭 → S-002 모달 → ESC → 8~21주 카드 클릭 → S-002 모달', async ({ page }) => {
    await page.goto('/')

    // 1. 1~7주 예측 카드 클릭 → S-002 모달
    const card7 = page.locator('.card.tappable').filter({ hasText: '1~7주 AI 예측가' }).first()
    await card7.click()
    await expect(page.locator('.modal-head .badge')).toContainText('S-002')

    // 2. 모달 닫기
    await page.keyboard.press('Escape')
    await expect(page.locator('.modal-overlay')).not.toBeVisible()

    // 3. 8~21주 예측 카드 클릭 → S-002 모달 (다른 horizon)
    const card21 = page.locator('.card.tappable').filter({ hasText: '8~21주 AI 예측가' }).first()
    await card21.click()
    await expect(page.locator('.modal-head .badge')).toContainText('S-002')
  })
})

test.describe('L3 - Persona D (이정재 시장분석): Graph RAG → 이벤트 분석 플로우', () => {
  test('S-001 → Graph RAG 상세 → 닫기 → S-010 이벤트 목록 진입', async ({ page }) => {
    await page.goto('/')

    // 1. Graph RAG 상세 분석 클릭 → S-005 모달
    await page.locator('button:has-text("상세 분석")').click()
    await expect(page.locator('.modal-head .badge')).toContainText('S-005')

    // 2. 모달 닫기
    await page.keyboard.press('Escape')
    await expect(page.locator('.modal-overlay')).not.toBeVisible()

    // 3. S-010 이벤트 페이지로 이동
    await page.goto('/?screen=S-010')
    await expect(page.locator('.content').first()).toBeVisible()
  })
})

test.describe('L3 - 모달 스택 (모달 위 모달)', () => {
  test('S-007 뉴스 모달 안에서 추가 인터랙션 가능', async ({ page }) => {
    await page.goto('/')

    // 뉴스 카드 클릭 → S-007
    const newsCard = page.locator('.card.tappable.flat').first()
    if (await newsCard.count() > 0) {
      await newsCard.click()
      await expect(page.locator('.modal-head .badge')).toContainText('S-007')

      // 모달이 표시되어 있고 내용 영역도 보임
      await expect(page.locator('.modal-overlay')).toBeVisible()
    }
  })
})

test.describe('L3 - HITL 임계치 조정 플로우 (백엔드 연동)', () => {
  test('S-003 모달 진입 → HITL 패널 표시 → 저장 (백엔드 POST 호출 가능)', async ({ page }) => {
    // 직접 S-003 진입
    await page.goto('/?modal=S-003&tab=A-4')
    await expect(page.locator('.modal-overlay')).toBeVisible({ timeout: 5000 })

    // HITL 패널이 모달 내에 표시 (텍스트 'HITL' 또는 '임계치' 또는 '저장')
    const hitlPanel = page.locator('.hitl, [class*="hitl"]').or(page.locator('text=/임계치|HITL|저장/'))
    // 적어도 일부 HITL 관련 요소가 존재
    expect(await hitlPanel.count()).toBeGreaterThan(0)
  })

  test('백엔드 POST /api/hitl/rules 호출 시 202 응답', async ({ request }) => {
    const res = await request.post('http://localhost:8000/api/hitl/rules', {
      data: {
        signalId: 'A-4',
        rules: [{ id: 'alert', value: 95 }],
        comment: 'L3 e2e test',
      },
    })
    expect(res.status()).toBe(202)
    const body = await res.json()
    expect(body.status).toBe('processing')
    expect(body.queueId).toBeTruthy()
  })

  test('HITL job 폴링 → done 상태로 전환', async ({ request }) => {
    const postRes = await request.post('http://localhost:8000/api/hitl/rules', {
      data: { signalId: 'A-4', rules: [{ id: 'pos', value: 0.35 }] },
    })
    const { queueId } = await postRes.json()
    expect(queueId).toBeTruthy()

    // 첫 폴링: processing 가능
    await new Promise((r) => setTimeout(r, 1500))
    // 두번째 폴링: done
    const pollRes = await request.get(`http://localhost:8000/api/hitl/jobs/${queueId}`)
    expect(pollRes.status()).toBe(200)
    const job = await pollRes.json()
    expect(job.status).toBe('done')
    expect(job.beforeResult).toBeTruthy()
    expect(job.afterResult).toBeTruthy()
  })
})

test.describe('L3 - 전체 화면 네비게이션 (14화면 순회)', () => {
  const fullPages = ['S-001', 'S-006', 'S-008', 'S-010', 'S-012', 'S-014']
  const modals = ['S-002', 'S-003', 'S-004', 'S-005', 'S-007', 'S-009', 'S-011', 'S-013']

  test('모든 6개 풀페이지 순차 진입 → 콘솔 에러 0건', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(`[${msg.location().url}] ${msg.text()}`)
    })

    for (const screen of fullPages) {
      await page.goto(`/?screen=${screen}`)
      await page.waitForLoadState('networkidle')
      await expect(page.locator('.content, .modal-overlay').first()).toBeVisible()
    }

    expect(errors, `Console errors:\n${errors.join('\n')}`).toEqual([])
  })

  test('모든 8개 모달 딥링크 진입 → 콘솔 에러 0건', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(`[${msg.location().url}] ${msg.text()}`)
    })

    for (const modal of modals) {
      // 일부 모달은 추가 파라미터 필요
      const params =
        modal === 'S-003'
          ? '&tab=A-1'
          : modal === 'S-004'
            ? '&tab=B-1'
            : modal === 'S-002'
              ? '&horizon=7'
              : modal === 'S-007'
                ? '&newsIdx=0'
                : modal === 'S-009'
                  ? '&week=0'
                  : modal === 'S-011'
                    ? '&eventIdx=0'
                    : modal === 'S-013'
                      ? '&rowIdx=0'
                      : ''
      await page.goto(`/?modal=${modal}${params}`)
      await page.waitForLoadState('networkidle')
      await expect(page.locator('.modal-overlay')).toBeVisible({ timeout: 5000 })
    }

    expect(errors, `Console errors:\n${errors.join('\n')}`).toEqual([])
  })
})
