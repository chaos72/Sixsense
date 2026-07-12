// Sixsense PWA service worker — 앱 설치/오프라인 지원용.
// 전략: 온라인이면 항상 네트워크 우선(최신 데이터), 실패 시에만 캐시 폴백.
// 데이터 대시보드이므로 오래된 화면이 굳지 않도록 network-first 로 유지한다.
const CACHE = 'sixsense-v1';
const SHELL = ['/', '/index.html', '/manifest.webmanifest', '/apple-touch-icon.png', '/icon-192.png', '/icon-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  // 같은 출처의 GET 요청만 처리 (API/외부는 그대로 통과)
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  e.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match('/index.html')))
  );
});
