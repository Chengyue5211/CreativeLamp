/**
 * 绘创前程 — Service Worker
 * 离线缓存策略：Shell优先缓存 + API网络优先
 */
const CACHE_NAME = 'hc-v1';
const SHELL_URLS = [
    '/',
    '/static/css/main.css',
    '/static/js/app.js',
    '/static/js/line-svg.js',
    '/static/js/transform-svg.js',
    '/static/js/contour-svg.js',
    '/static/manifest.json',
];

// 安装：预缓存Shell资源
self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(SHELL_URLS))
            .then(() => self.skipWaiting())
    );
});

// 激活：清理旧缓存
self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

// 请求拦截
self.addEventListener('fetch', (e) => {
    const url = new URL(e.request.url);

    // API请求：网络优先
    if (url.pathname.startsWith('/api/')) {
        e.respondWith(
            fetch(e.request).catch(() => {
                return new Response(JSON.stringify({ detail: '网络连接失败，请检查网络后重试' }), {
                    status: 503,
                    headers: { 'Content-Type': 'application/json' },
                });
            })
        );
        return;
    }

    // 图片：缓存优先+后台更新
    if (e.request.destination === 'image') {
        e.respondWith(
            caches.match(e.request).then(cached => {
                const fetched = fetch(e.request).then(resp => {
                    if (resp.ok) {
                        const clone = resp.clone();
                        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
                    }
                    return resp;
                }).catch(() => cached);
                return cached || fetched;
            })
        );
        return;
    }

    // Shell资源：缓存优先
    e.respondWith(
        caches.match(e.request).then(cached => cached || fetch(e.request))
    );
});
