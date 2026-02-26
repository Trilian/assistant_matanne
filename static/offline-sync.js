/**
 * Offline Sync Manager — Innovation 3.1
 *
 * Bidirectional sync between IndexedDB (client) and Supabase (server).
 * Designed for shopping lists in-store with connectivity issues.
 *
 * Usage in Streamlit:
 *   import streamlit.components.v1 as components
 *   with open("static/offline-sync.js") as f:
 *       components.html(f"<script>{f.read()}</script>", height=0)
 *
 * API via postMessage:
 *   window.OfflineSync.ajouterArticle({nom, quantite, unite, categorie})
 *   window.OfflineSync.supprimerArticle(id)
 *   window.OfflineSync.modifierArticle(id, {quantite: 3})
 *   window.OfflineSync.obtenirListe() → Promise<Article[]>
 *   window.OfflineSync.synchroniser() → Promise<SyncResult>
 *   window.OfflineSync.estEnLigne() → boolean
 */

(function () {
    'use strict';

    const DB_NAME = 'matanne-offline-db';
    const DB_VERSION = 2; // Upgraded from v1
    const STORES = {
        SHOPPING: 'shopping_list',
        PENDING: 'pending_changes',
        INVENTAIRE: 'inventaire_cache',
        META: 'sync_meta',
    };

    // ═══════════════════════════════════════════════════
    // IndexedDB Setup
    // ═══════════════════════════════════════════════════

    function openDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);
            request.onerror = () => reject(request.error);
            request.onsuccess = () => resolve(request.result);
            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Shopping list store
                if (!db.objectStoreNames.contains(STORES.SHOPPING)) {
                    const store = db.createObjectStore(STORES.SHOPPING, {
                        keyPath: 'id',
                        autoIncrement: true,
                    });
                    store.createIndex('synced', 'synced', { unique: false });
                    store.createIndex('categorie', 'categorie', { unique: false });
                    store.createIndex('coche', 'coche', { unique: false });
                }

                // Pending changes queue
                if (!db.objectStoreNames.contains(STORES.PENDING)) {
                    const pending = db.createObjectStore(STORES.PENDING, {
                        keyPath: 'id',
                        autoIncrement: true,
                    });
                    pending.createIndex('timestamp', 'timestamp', { unique: false });
                    pending.createIndex('type', 'type', { unique: false });
                }

                // Inventaire cache
                if (!db.objectStoreNames.contains(STORES.INVENTAIRE)) {
                    db.createObjectStore(STORES.INVENTAIRE, {
                        keyPath: 'id',
                    });
                }

                // Sync metadata
                if (!db.objectStoreNames.contains(STORES.META)) {
                    db.createObjectStore(STORES.META, {
                        keyPath: 'key',
                    });
                }
            };
        });
    }

    // ═══════════════════════════════════════════════════
    // CRUD Operations
    // ═══════════════════════════════════════════════════

    async function ajouterArticle(article) {
        const db = await openDB();
        const item = {
            ...article,
            coche: false,
            synced: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };

        return new Promise((resolve, reject) => {
            const tx = db.transaction([STORES.SHOPPING, STORES.PENDING], 'readwrite');
            const store = tx.objectStore(STORES.SHOPPING);
            const req = store.add(item);

            req.onsuccess = () => {
                const id = req.result;
                // Queue for sync
                const pending = tx.objectStore(STORES.PENDING);
                pending.add({
                    type: 'add',
                    store: STORES.SHOPPING,
                    data: { ...item, id },
                    timestamp: Date.now(),
                });
                resolve(id);
            };
            req.onerror = () => reject(req.error);
        });
    }

    async function modifierArticle(id, changes) {
        const db = await openDB();
        return new Promise((resolve, reject) => {
            const tx = db.transaction([STORES.SHOPPING, STORES.PENDING], 'readwrite');
            const store = tx.objectStore(STORES.SHOPPING);
            const getReq = store.get(id);

            getReq.onsuccess = () => {
                const item = getReq.result;
                if (!item) {
                    reject(new Error(`Article ${id} non trouvé`));
                    return;
                }
                const updated = {
                    ...item,
                    ...changes,
                    synced: false,
                    updated_at: new Date().toISOString(),
                };
                store.put(updated);

                // Queue
                const pending = tx.objectStore(STORES.PENDING);
                pending.add({
                    type: 'update',
                    store: STORES.SHOPPING,
                    data: updated,
                    timestamp: Date.now(),
                });
                resolve(updated);
            };
            getReq.onerror = () => reject(getReq.error);
        });
    }

    async function supprimerArticle(id) {
        const db = await openDB();
        return new Promise((resolve, reject) => {
            const tx = db.transaction([STORES.SHOPPING, STORES.PENDING], 'readwrite');
            tx.objectStore(STORES.SHOPPING).delete(id);

            const pending = tx.objectStore(STORES.PENDING);
            pending.add({
                type: 'delete',
                store: STORES.SHOPPING,
                data: { id },
                timestamp: Date.now(),
            });

            tx.oncomplete = () => resolve(true);
            tx.onerror = () => reject(tx.error);
        });
    }

    async function cocherArticle(id) {
        return modifierArticle(id, { coche: true });
    }

    async function obtenirListe(filtreCategorie) {
        const db = await openDB();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(STORES.SHOPPING, 'readonly');
            const store = tx.objectStore(STORES.SHOPPING);

            let req;
            if (filtreCategorie) {
                const index = store.index('categorie');
                req = index.getAll(filtreCategorie);
            } else {
                req = store.getAll();
            }

            req.onsuccess = () => {
                const items = req.result.filter((i) => !i._deleted);
                resolve(items);
            };
            req.onerror = () => reject(req.error);
        });
    }

    // ═══════════════════════════════════════════════════
    // Bidirectional Sync
    // ═══════════════════════════════════════════════════

    async function synchroniser() {
        if (!navigator.onLine) {
            return { success: false, reason: 'offline', pending: await countPending() };
        }

        const result = {
            success: true,
            uploaded: 0,
            downloaded: 0,
            conflicts: 0,
            errors: [],
        };

        try {
            // Phase 1: Push local changes to server
            const pushResult = await pushChanges();
            result.uploaded = pushResult.count;
            result.errors.push(...pushResult.errors);

            // Phase 2: Pull server state
            const pullResult = await pullFromServer();
            result.downloaded = pullResult.count;

            // Phase 3: Update last sync timestamp
            await setMeta('last_sync', {
                key: 'last_sync',
                timestamp: Date.now(),
                iso: new Date().toISOString(),
            });

            // Notify Streamlit if available
            if (window.parent && window.parent.postMessage) {
                window.parent.postMessage(
                    {
                        type: 'SYNC_COMPLETE',
                        result: result,
                    },
                    '*'
                );
            }
        } catch (e) {
            result.success = false;
            result.errors.push(e.message);
        }

        return result;
    }

    async function pushChanges() {
        const db = await openDB();
        const tx = db.transaction(STORES.PENDING, 'readonly');
        const store = tx.objectStore(STORES.PENDING);

        const pending = await new Promise((resolve, reject) => {
            const req = store.getAll();
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });

        let count = 0;
        const errors = [];

        for (const change of pending) {
            try {
                const response = await fetch('/api/v1/courses/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        action: change.type,
                        data: change.data,
                        client_timestamp: change.timestamp,
                    }),
                });

                if (response.ok) {
                    // Remove from pending
                    const delTx = (await openDB()).transaction(STORES.PENDING, 'readwrite');
                    delTx.objectStore(STORES.PENDING).delete(change.id);

                    // Mark as synced in shopping list
                    if (change.data && change.data.id && change.type !== 'delete') {
                        const syncTx = (await openDB()).transaction(
                            STORES.SHOPPING,
                            'readwrite'
                        );
                        const item = await new Promise((res) => {
                            const req = syncTx
                                .objectStore(STORES.SHOPPING)
                                .get(change.data.id);
                            req.onsuccess = () => res(req.result);
                            req.onerror = () => res(null);
                        });
                        if (item) {
                            item.synced = true;
                            syncTx.objectStore(STORES.SHOPPING).put(item);
                        }
                    }

                    count++;
                } else {
                    errors.push(`HTTP ${response.status} pour ${change.type}`);
                }
            } catch (e) {
                errors.push(`Push error: ${e.message}`);
            }
        }

        return { count, errors };
    }

    async function pullFromServer() {
        const lastSync = await getMeta('last_sync');
        const since = lastSync ? lastSync.iso : '1970-01-01T00:00:00Z';

        try {
            const response = await fetch(
                `/api/v1/courses/sync?since=${encodeURIComponent(since)}`
            );

            if (!response.ok) {
                return { count: 0 };
            }

            const serverItems = await response.json();
            if (!Array.isArray(serverItems)) {
                return { count: 0 };
            }

            const db = await openDB();
            const tx = db.transaction(STORES.SHOPPING, 'readwrite');
            const store = tx.objectStore(STORES.SHOPPING);

            let count = 0;
            for (const item of serverItems) {
                // Conflict resolution: server wins if client is synced
                const existing = await new Promise((res) => {
                    if (item.local_id) {
                        const req = store.get(item.local_id);
                        req.onsuccess = () => res(req.result);
                        req.onerror = () => res(null);
                    } else {
                        res(null);
                    }
                });

                if (existing && !existing.synced) {
                    // Local has unsynced changes — skip (client wins)
                    continue;
                }

                // Upsert from server
                store.put({
                    ...item,
                    synced: true,
                    server_id: item.id,
                });
                count++;
            }

            return { count };
        } catch (e) {
            console.warn('[OfflineSync] Pull failed:', e);
            return { count: 0 };
        }
    }

    // ═══════════════════════════════════════════════════
    // Helpers
    // ═══════════════════════════════════════════════════

    async function countPending() {
        const db = await openDB();
        return new Promise((resolve) => {
            const tx = db.transaction(STORES.PENDING, 'readonly');
            const req = tx.objectStore(STORES.PENDING).count();
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => resolve(0);
        });
    }

    async function getMeta(key) {
        const db = await openDB();
        return new Promise((resolve) => {
            const tx = db.transaction(STORES.META, 'readonly');
            const req = tx.objectStore(STORES.META).get(key);
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => resolve(null);
        });
    }

    async function setMeta(key, value) {
        const db = await openDB();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(STORES.META, 'readwrite');
            tx.objectStore(STORES.META).put(value);
            tx.oncomplete = () => resolve();
            tx.onerror = () => reject(tx.error);
        });
    }

    function estEnLigne() {
        return navigator.onLine;
    }

    // ═══════════════════════════════════════════════════
    // Auto-sync on connectivity change
    // ═══════════════════════════════════════════════════

    window.addEventListener('online', () => {
        console.log('[OfflineSync] Back online — auto-syncing...');
        synchroniser().then((result) => {
            console.log('[OfflineSync] Auto-sync result:', result);
        });
    });

    // Register background sync if SW supports it
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready.then((registration) => {
            registration.sync.register('sync-shopping-list').catch((e) => {
                console.warn('[OfflineSync] BG sync registration failed:', e);
            });
        });
    }

    // ═══════════════════════════════════════════════════
    // Offline status indicator (UI)
    // ═══════════════════════════════════════════════════

    function injecterIndicateur() {
        if (document.getElementById('offline-indicator')) return;

        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.style.cssText = `
            position: fixed;
            bottom: 16px;
            right: 16px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            z-index: 10000;
            transition: all 0.3s ease;
            pointer-events: none;
            opacity: 0;
        `;
        document.body.appendChild(indicator);

        function updateIndicator() {
            if (navigator.onLine) {
                indicator.textContent = '✅ En ligne';
                indicator.style.background = '#e6f4ea';
                indicator.style.color = '#137333';
                indicator.style.opacity = '1';
                setTimeout(() => {
                    indicator.style.opacity = '0';
                }, 3000);
            } else {
                indicator.textContent = '📴 Hors ligne';
                indicator.style.background = '#fce8e6';
                indicator.style.color = '#c5221f';
                indicator.style.opacity = '1';
            }
        }

        window.addEventListener('online', updateIndicator);
        window.addEventListener('offline', updateIndicator);
    }

    // Inject on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injecterIndicateur);
    } else {
        injecterIndicateur();
    }

    // ═══════════════════════════════════════════════════
    // Public API
    // ═══════════════════════════════════════════════════

    window.OfflineSync = {
        ajouterArticle,
        modifierArticle,
        supprimerArticle,
        cocherArticle,
        obtenirListe,
        synchroniser,
        estEnLigne,
        countPending,
        getMeta,
        DB_NAME,
        DB_VERSION,
    };

    console.log('[OfflineSync] Module loaded. Online:', navigator.onLine);
})();
