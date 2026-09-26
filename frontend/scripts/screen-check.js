// 화면 40개 자동 검사 (v2.6 재발 방지 장치 3) — 개발 서버(http://localhost:5173) 탭의 콘솔에서 실행.
// 사용: 이 파일 내용을 실행하면 window.screenCheck 가 준비된다. 한 번 호출이 45초를 넘지 않게 나눠 부른다:
//   await screenCheck(0, 20)   →   await screenCheck(20)      (결과는 호출마다 누적)
// 결과: { 검사한_화면, 전체, bad(금지 표현·콘솔 오류·NaN·모달 미표시·빈 화면), over(모바일 375px 넘침),
//         fcNoFail(예측이 보이는데 '불합격' 없음), 통과 } — 모든 목록이 비어 있어야 통과.
// 화면 목록은 화면 데이터(신호·거시·뉴스·이벤트 수)에서 자동으로 만든다.
window.screenCheck = async (from = 0, to = Infinity) => {
  const D = await import('/src/mocks/data.js').then((m) => m.SIXSENSE_DATA);
  const urls = ['?screen=S-001', '?screen=S-006', '?screen=S-010', '?screen=S-012', '?screen=S-014', '?screen=S-001&modal=S-009'];
  D.macro.forEach((m) => urls.push(`?screen=S-008&tab=${m.id}`));
  D.signalsA.forEach((s) => urls.push(`?screen=S-001&modal=S-003&tab=${s.id}`));
  D.signalsB.forEach((s) => urls.push(`?screen=S-001&modal=S-004&tab=${s.id}`));
  (D.news || []).forEach((_, i) => urls.push(`?screen=S-001&modal=S-007&newsIdx=${i}`));
  (D.events || []).forEach((_, i) => urls.push(`?screen=S-001&modal=S-011&eventIdx=${i}`));
  // 과거에 화면에 있었던 가짜·허위 표시 — 다시 나타나면 안 됨
  const forbidden = ['현재 계약가', 'DDR5 8Gb', '/ GB', '/GB', 'CLAUDE', 'Claude', '신뢰 81', '신뢰 74', '예측가', 'HITL',
    '저장 & 재학습', 'Graph RAG', '구리 선행', '재학습 시 오차', '가중치 상향', '100% 성공', '재시도 3회', 'Red Alert', '공급과잉',
    'NaN', 'undefined', 'Infinity', '예측분석 인사이트', '정확도 트래킹', 'GBR ★', 'LSTM ★', '4.54%', '6.86%', '9.19%', '2026-00',
    'Polymarket', 'ICE', 'S&P Global', 'BOK API', 'LME Public', 'DRAMeXchange', 'TrendForce', 'p4d.24xlarge',
    '예측 수치를 표시하지', '예측선 없음', '부호검정', '우연히 이 정도로', '4.92M', '전자부품 재고지수'];
  const R = (window.__screenCheckResult = from === 0 ? { done: 0, bad: [], over: [], fcNoFail: [] } : window.__screenCheckResult);
  const { bad, over, fcNoFail } = R;
  for (const q of urls.slice(from, to)) {
    for (const w of [1280, 375]) {
      const f = document.createElement('iframe');
      f.style.cssText = `position:fixed;left:-5000px;width:${w}px;height:860px`;
      document.body.appendChild(f);
      const errs = [];
      await new Promise((r) => { f.onload = r; f.src = '/' + q; });
      const oe = f.contentWindow.console.error;
      f.contentWindow.console.error = (...a) => { errs.push(a.map(String).join(' ').slice(0, 100)); oe.apply(f.contentWindow.console, a); };
      await new Promise((r) => setTimeout(r, 700));
      const d = f.contentDocument, t = d.body.innerText;
      if (w === 1280) {
        const hits = forbidden.filter((x) => t.includes(x));
        const nan = [...d.querySelectorAll('svg *')].some((el) => [...el.attributes].some((a) => /NaN/.test(a.value)));
        const noModal = q.includes('modal=') && !d.querySelector('.modal');
        if (hits.length || errs.length || nan || noModal || t.length < 200) bad.push({ q, hits, errs, nan, noModal });
        if ((t.includes('AI 예측') || t.includes('4주 뒤 예측')) && !t.includes('불합격')) fcNoFail.push(q);
      } else {
        const mb = d.querySelector('.modal-body');
        const o = Math.max(d.documentElement.scrollWidth - w, mb ? mb.scrollWidth - mb.clientWidth : 0);
        if (o > 2) over.push({ q, over: o });
      }
      f.remove();
    }
    R.done++;
  }
  return JSON.stringify({ 검사한_화면: R.done, 전체: urls.length, bad, over, fcNoFail,
    통과: R.done === urls.length && !bad.length && !over.length && !fcNoFail.length });
};
"screenCheck 준비 완료 — await screenCheck(0, 20) 후 await screenCheck(20)";
