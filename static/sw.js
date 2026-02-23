// Service Worker pour Assistant Matanne PWA
// Version auto-incrémentée pour cache busting
const CACHE_VERSION = 3;
const CACHE_NAME = `matanne-cache-v${CACHE_VERSION}`;
const OFFLINE_URL = '/offline.html';
const DB_NAME = 'matanne-offline-db';
const DB_VERSION = 1;

// Ressources à mettre en cache immédiatement (app shell)
const PRECACHE_URLS = [
    '/',
    '/offline.html',
    '/static/manifest.json',
];

// Routes critiques à cacher en priorité après navigation
const RUNTIME_CACHE_ROUTES = [
    '/api/v1/recettes',
    '/api/v1/courses',
];

// Durée max pour les requêtes réseau (ms)
const NETWORK_TIMEOUT_MS = 5000;

// Installation du Service Worker
self.addEventListener('install', (event) => {
    console.log(`[SW] Installing v${CACHE_VERSION}...`);
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
    console.log(`[SW] Activating v${CACHE_VERSION}...`);
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name.startsWith('matanne-cache-') && name !== CACHE_NAME)
                    .map((name) => {
                        console.log(`[SW] Deleting old cache: ${name}`);
                        return caches.delete(name);
                    })
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
            await syncWithRetry(change);
        }
    } catch (error) {
        console.error('[SW] Sync error:', error);
        throw error; // Re-throw to trigger retry by Background Sync API
    }
}

// Sync individuel avec retry exponentiel
async function syncWithRetry(change, maxRetries = 3) {
    let lastError;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await fetch('/api/v1/courses/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(change)
            });
            if (response.ok) {
                // Supprimer de pending_changes après succès
                const db = await openDB();
                const tx = db.transaction('pending_changes', 'readwrite');
                tx.objectStore('pending_changes').delete(change.id);
                console.log(`[SW] Synced change ${change.id}`);
                return;
            }
            lastError = new Error(`HTTP ${response.status}`);
        } catch (e) {
            lastError = e;
            console.warn(`[SW] Sync attempt ${attempt + 1}/${maxRetries} failed:`, e);
            // Backoff exponentiel: 1s, 2s, 4s
            await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000));
        }
    }
    console.error(`[SW] Sync failed after ${maxRetries} retries:`, lastError);
    throw lastError;
}

// Message handling
self.addEventListener('message', (event) => {
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    if (event.data.type === 'REGISTER_PERIODIC_SYNC') {
        registerPeriodicSync();
    }
});

// Periodic Background Sync (si supporté)
async function registerPeriodicSync() {
    if ('periodicSync' in self.registration) {
        const status = await navigator.permissions.query({ name: 'periodic-background-sync' });
        if (status.state === 'granted') {
            try {
                await self.registration.periodicSync.register('sync-recipes-cache', {
                    minInterval: 24 * 60 * 60 * 1000, // 24h
                });
                console.log('[SW] Periodic sync registered');
            } catch (e) {
                console.warn('[SW] Periodic sync not available:', e);
            }
        }
    }
}

// Periodic sync handler
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'sync-recipes-cache') {
        event.waitUntil(updateRecipesCache());
    }
});

// Rafraîchir le cache des recettes en arrière-plan
async function updateRecipesCache() {
    console.log('[SW] Updating recipes cache...');
    try {
        const cache = await caches.open(CACHE_NAME);
        const response = await fetch('/api/v1/recettes?page_size=50');
        if (response.ok) {
            await cache.put('/api/v1/recettes?page_size=50', response.clone());
            console.log('[SW] Recipes cache updated');
        }
    } catch (e) {
        console.warn('[SW] Failed to update recipes cache:', e);
    }
}
