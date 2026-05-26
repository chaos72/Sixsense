// USER-REQUESTED EXTENSION (#16, 2026-05-27) — 매주 화요일 06:00 KST 동적 계산
// 사용자 보고: S-014 "다음 수집 일정" 이 2026-04-29 화요일 로 고정됨.
// → 모든 "다음 수집" / "마지막 갱신" / "잔여 시간" 을 런타임 동적 계산으로 교체.
// 사용자가 페이지 새로고침할 때마다 항상 최신 상태로 표시.

const KST_OFFSET_MS = 9 * 60 * 60 * 1000;  // KST = UTC+9

/** 현재 시각의 KST 기준 Date (브라우저 로컬 시각 대신). */
function nowKST() {
  const utc = new Date();
  return new Date(utc.getTime() + (utc.getTimezoneOffset() * 60 * 1000) + KST_OFFSET_MS);
}

/**
 * 다음 화요일 06:00 KST 시점 반환.
 * - 오늘이 화요일 06:00 이전이면 오늘
 * - 오늘이 화요일 06:00 이후 또는 화요일 외이면 다음 주 화요일
 */
export function nextTuesday06KST() {
  const k = nowKST();
  const day = k.getDay();  // 0=Sun, 1=Mon, 2=Tue
  let daysUntil = (2 - day + 7) % 7;
  if (daysUntil === 0 && k.getHours() >= 6) daysUntil = 7;
  const next = new Date(k);
  next.setDate(k.getDate() + daysUntil);
  next.setHours(6, 0, 0, 0);
  return next;
}

/** 가장 최근 화요일 06:00 KST 시점 (실제 데이터 갱신 시점 추정). */
export function lastTuesday06KST() {
  const k = nowKST();
  const day = k.getDay();
  let daysSince = (day - 2 + 7) % 7;
  if (daysSince === 0 && k.getHours() < 6) daysSince = 7;
  const last = new Date(k);
  last.setDate(k.getDate() - daysSince);
  last.setHours(6, 0, 0, 0);
  return last;
}

/** "YYYY-MM-DD (화) 06:00 KST" 형식 포맷. */
export function formatTuesdayKST(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd} (화) 06:00 KST`;
}

/** "YYYY-MM-DD (화)" 짧은 포맷. */
export function formatTuesdayShort(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd} (화)`;
}

/** "YYYY-MM-DD HH:MM" 포맷. */
export function formatDateTimeKST(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`;
}

/** 잔여 시간 "N일 M시간" 포맷. 음수면 "지금 갱신 중". */
export function formatTimeUntil(target) {
  const diff = target.getTime() - nowKST().getTime();
  if (diff <= 0) return "지금 갱신 중";
  const days = Math.floor(diff / (24 * 60 * 60 * 1000));
  const hours = Math.floor((diff % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
  if (days === 0) return `${hours}시간`;
  return `${days}일 ${hours}시간`;
}

/** 두 날짜 사이 주(week) 차이. */
export function weeksBetween(date1, date2) {
  return Math.round((date2.getTime() - date1.getTime()) / (1000 * 60 * 60 * 24 * 7));
}
