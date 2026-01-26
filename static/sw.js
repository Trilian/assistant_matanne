// Service Worker pour Assistant Matanne PWA
const CACHE_NAME = 'matanne-cache-v2';
const OFFLINE_URL = '/offline.html';
const DB_NAME = 'matanne-offline-db';
const DB_VERSION = 1;

// Ressources à mettre en cache immédiatement
const PRECACHE_URLS = [
    '/',
    '/offline.html',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/static/manifest.json',
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
    console.log('[SW] Installing v2...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Precaching app shell');
                return cache.addAll(PRECACHE_URLS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME)
                    .map((name) => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// Stratégie de fetch: Network First avec fallback Cache
self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    if (event.request.url.includes('_stcore')) return;

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                const responseClone = response.clone();
                if (response.ok && isStaticAsset(event.request.url)) {
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) return cachedResponse;
                        if (event.request.destination === 'document') {
                            return caches.match(OFFLINE_URL);
                        }
                        return new Response('Offline', { status: 503 });
                    });
            })
    );
});

function isStaticAsset(url) {
    const staticExtensions = ['.css', '.js', '.png', '.jpg', '.svg', '.ico', '.woff2'];
    return staticExtensions.some(ext => url.endsWith(ext));
}

// Push notifications
self.addEventListener('push', (event) => {
    const data = event.data ? event.data.json() : {};
    const options = {
        body: data.body || 'Nouvelle notification',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [100, 50, 100],
        data: data.data || {},
        tag: data.tag || 'default',
    };
    event.waitUntil(
        self.registration.showNotification(data.title || 'Assistant Matanne', options)
    );
});

// Click notification
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const urlToOpen = event.notification.data?.url || '/';
    event.waitUntil(
        clients.matchAll({ type: 'window' })
            .then((clientList) => {
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// Background sync
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-shopping-list') {
        event.waitUntil(syncShoppingList());
    }
});

// IndexedDB for offline storage
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('shopping_list')) {
                const store = db.createObjectStore('shopping_list', { keyPath: 'id', autoIncrement: true });
                store.createIndex('synced', 'synced', { unique: false });
            }
            if (!db.objectStoreNames.contains('pending_changes')) {
                db.createObjectStore('pending_changes', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

async function syncShoppingList() {
    console.log('[SW] Syncing shopping list...');
    try {
        const db = await openDB();
        const tx = db.transaction('pending_changes', 'readonly');
        const store = tx.objectStore('pending_changes');
        const pending = await new Promise((resolve, reject) => {
            const req = store.getAll();
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });

        for (const change of pending) {
            try {
                await fetch('/api/courses/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(change)
                });
            } catch (e) {
                console.error('[SW] Sync failed:', e);
            }
        }
    } catch (error) {
        console.error('[SW] Sync error:', error);
    }
}

// Message handling
self.addEventListener('message', (event) => {
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
