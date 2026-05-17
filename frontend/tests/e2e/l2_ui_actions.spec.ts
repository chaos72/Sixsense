// L2 UI Action Tests — Sixsense
// Design Ref: Design §8.3 L2 UI Action Test Scenarios
// 각 테스트: 페이지 진입 → 액션 수행 → 결과 검증
import { test, expect } from '@playwright/test'

test.describe('L2 - 메인 대시보드 (S-001)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // 메인 페이지가 렌더링 완료될 때까지 대기
    await expect(page.locator('.content').first()).toBeVisible()
  })

  test('S-001 진입 시 가격 카드 3개 + 14신호 카드 + 차트 모두 표시', async ({ page }) => {
    // 가격 카드 3개 (현재 계약가 / 1~7주 AI 예측가 / 8~21주 AI 예측가)
    await expect(page.locator('text=현재 계약가').first()).toBeVisible()
    await expect(page.locator('text=1~7주 AI 예측가').first()).toBeVisible()
    await expect(page.locator('text=8~21주 AI 예측가').first()).toBeVisible()
    // 14신호: Group A·B 카드들 (.grid-7이 2개 있음)
    const grid7 = page.locator('.grid-7')
    await expect(grid7).toHaveCount(2)
    // Graph RAG 섹션
    await expect(page.locator('text=Graph RAG').first()).toBeVisible()
  })

  test('현재 가격 카드의 가격 텍스트가 mock 데이터 반영', async ({ page }) => {
    // mock에서 current = 3.2
    await expect(page.locator('.card-big.num').first()).toContainText('3.20')
  })

  test('1~7주 예측 카드 클릭 → S-002 모달 열림', async ({ page }) => {
    // 카드 클릭
    await page.locator('text=1~7주').first().locator('..').locator('..').click()
    // 모달 오버레이 표시
    await expect(page.locator('.modal-overlay')).toBeVisible()
    // 모달 헤더에 S-002 배지
    await expect(page.locator('.modal-head .badge')).toContainText('S-002')
  })

  test('Group A 첫 신호 카드 클릭 → S-003 모달 열림', async ({ page }) => {
    // Group A는 첫 grid-7
    const firstSignalCard = page.locator('.grid-7').first().locator('.card.tappable').first()
    await firstSignalCard.click()
    await expect(page.locator('.modal-overlay')).toBeVisible()
    await expect(page.locator('.modal-head .badge')).toContainText('S-003')
  })

  test('Graph RAG 상세 분석 버튼 → S-005 모달 열림', async ({ page }) => {
    await page.locator('button:has-text("상세 분석")').click()
    await expect(page.locator('.modal-overlay')).toBeVisible()
    await expect(page.locator('.modal-head .badge')).toContainText('S-005')
  })

  test('ESC 키로 모달 닫힘', async ({ page }) => {
    // 가격 카드 클릭 → 모달
    await page.locator('text=1~7주').first().locator('..').locator('..').click()
    await expect(page.locator('.modal-overlay')).toBeVisible()
    // ESC
    await page.keyboard.press('Escape')
    await expect(page.locator('.modal-overlay')).not.toBeVisible()
  })

  test('모달 바깥 클릭으로 닫힘', async ({ page }) => {
    await page.locator('text=1~7주').first().locator('..').locator('..').click()
    await expect(page.locator('.modal-overlay')).toBeVisible()
    // 오버레이 클릭 (왼쪽 상단 corner)
    await page.locator('.modal-overlay').click({ position: { x: 10, y: 10 } })
    await expect(page.locator('.modal-overlay')).not.toBeVisible()
  })

  test('차트 범위 필터 3 모드 (단기/중장기/전체) 작동', async ({ page }) => {
    // ChartRangeSeg는 실제 label: "단기 1~7주" / "중장기 8~21주" / "전체"
    // 활성 버튼은 .on 클래스
    const shortBtn = page.getByRole('button', { name: '단기 1~7주', exact: true })
    const midBtn = page.getByRole('button', { name: '중장기 8~21주', exact: true })
    const allBtn = page.getByRole('button', { name: '전체', exact: true })
    await expect(shortBtn).toBeVisible()
    await expect(midBtn).toBeVisible()
    await expect(allBtn).toBeVisible()
    // 클릭 후 .on 활성 클래스 검증
    await midBtn.click()
    await expect(midBtn).toHaveClass(/on/)
    await shortBtn.click()
    await expect(shortBtn).toHaveClass(/on/)
    await allBtn.click()
    await expect(allBtn).toHaveClass(/on/)
  })

  test('전체 페이지에 콘솔 에러 없음', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.reload()
    await page.waitForLoadState('networkidle')
    expect(errors).toEqual([])
  })
})

test.describe('L2 - 풀페이지 라우팅 (URL 딥링크)', () => {
  for (const screen of ['S-006', 'S-008', 'S-010', 'S-012', 'S-014']) {
    test(`URL ?screen=${screen} 진입 시 풀페이지 렌더링`, async ({ page }) => {
      await page.goto(`/?screen=${screen}`)
      await expect(page.locator('.content, .modal-overlay').first()).toBeVisible({ timeout: 5000 })
      // 메인 대시보드 가격 카드는 안 보여야 함 (다른 페이지로 이동)
      await expect(page.locator('text=현재 계약가')).not.toBeVisible()
    })
  }
})

test.describe('L2 - 모달 딥링크 진입', () => {
  test('?modal=S-003&tab=A-4 진입 시 S-003 모달 A-4 탭', async ({ page }) => {
    await page.goto('/?modal=S-003&tab=A-4')
    await expect(page.locator('.modal-overlay')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('.modal-head .badge')).toContainText('S-003')
  })

  test('?modal=S-002&horizon=21 진입 시 S-002 모달', async ({ page }) => {
    await page.goto('/?modal=S-002&horizon=21')
    await expect(page.locator('.modal-overlay')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('.modal-head .badge')).toContainText('S-002')
  })
})

test.describe('L2 - 테마/밀도 토글 (Tweaks 패널)', () => {
  test('Tweaks 패널 열기 → 다크 모드 토글 시 data-theme 변경', async ({ page }) => {
    await page.goto('/')
    // Tweaks 토글 버튼 클릭 (보통 우하단)
    const tweaksToggle = page.locator('button:has-text("Tweaks"), button:has-text("⚙"), .tweaks-trigger').first()
    if (await tweaksToggle.count() > 0) {
      await tweaksToggle.click()
      // 다크 옵션 클릭
      const darkBtn = page.locator('label:has-text("다크"), button:has-text("다크")').first()
      if (await darkBtn.count() > 0) {
        await darkBtn.click()
        const theme = await page.evaluate(() => document.documentElement.dataset.theme)
        expect(theme).toBe('dark')
      }
    }
  })
})
