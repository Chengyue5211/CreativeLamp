/**
 * 绘创前程 — Service Worker
 * 离线缓存策略：Shell带版本缓存 + API网络优先 + 图片stale-while-revalidate
 */
const CACHE_VERSION = 'hc-v2';
const SHELL_URLS = [
    '/static/css/main.css',
    '/static/js/app.js',
    '/static/js/line-svg.js',
    '/static/js/transform-svg.js',
    '/static/js/contour-svg.js',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
];

// 安装：预缓存Shell资源（不缓存HTML，确保用户总能获取最新版本）
self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_VERSION)
            .then(cache => cache.addAll(SHELL_URLS))
            .then(() => self.skipWaiting())
    );
});

// 激活：清理旧版本缓存
self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k)))
        ).then(() => self.clients.claim())
    );
});

// 请求拦截
self.addEventListener('fetch', (e) => {
    const url = new URL(e.request.url);

    // HTML页面：始终走网络（确保获取最新版本）
    if (e.request.mode === 'navigate') {
        e.respondWith(
            fetch(e.request).catch(() =>
                caches.match('/').then(cached => cached || new Response('离线中，请检查网络连接', {
                    status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' },
                }))
            )
        );
        return;
    }

    // API请求：网络优先，失败返回错误
    if (url.pathname.startsWith('/api/')) {
        e.respondWith(
            fetch(e.request).catch(() =>
                new Response(JSON.stringify({ detail: '网络连接失败，请检查网络后重试' }), {
                    status: 503,
                    headers: { 'Content-Type': 'application/json' },
                })
            )
        );
        return;
    }

    // 图片：缓存优先+后台更新
    if (e.request.destination === 'image') {
        e.respondWith(
            caches.match(e.request).then(cached => {
                const fetchPromise = fetch(e.request).then(resp => {
                    if (resp.ok) {
                        const clone = resp.clone();
                        caches.open(CACHE_VERSION).then(c => c.put(e.request, clone));
                    }
                    return resp;
                }).catch(() => cached);
                return cached || fetchPromise;
            })
        );
        return;
    }

    // 静态资源(JS/CSS)：缓存优先，缺失时走网络
    e.respondWith(
        caches.match(e.request).then(cached => {
            if (cached) return cached;
            return fetch(e.request).then(resp => {
                if (resp.ok) {
                    const clone = resp.clone();
                    caches.open(CACHE_VERSION).then(c => c.put(e.request, clone));
                }
                return resp;
            });
        })
    );
});
