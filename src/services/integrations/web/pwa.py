"""
Configuration PWA (Progressive Web App) pour l'Assistant Matanne.

Ce module génère les fichiers nécessaires pour transformer
l'application Streamlit en PWA installable:
- manifest.json
- Service Worker
- Icônes
- Configuration offline

Usage:
    from src.services.integrations.web import generate_pwa_files, inject_pwa_meta

    # Générer les fichiers PWA (static/ par défaut)
    generate_pwa_files()

    # Injecter les meta tags
    inject_pwa_meta()
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION PWA
# ═══════════════════════════════════════════════════════════


PWA_CONFIG = {
    "name": "Assistant Matanne",
    "short_name": "Matanne",
    "description": "Hub de gestion familiale - Recettes, Courses, Planning",
    "start_url": "/",
    "display": "standalone",
    "orientation": "portrait-primary",
    "background_color": "#ffffff",
    "theme_color": "#667eea",
    "scope": "/",
    "lang": "fr-FR",
    "categories": ["lifestyle", "productivity", "food"],
    "icons": [
        {
            "src": "/static/icons/icon-72x72.png",
            "sizes": "72x72",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-96x96.png",
            "sizes": "96x96",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-128x128.png",
            "sizes": "128x128",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-144x144.png",
            "sizes": "144x144",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-152x152.png",
            "sizes": "152x152",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-384x384.png",
            "sizes": "384x384",
            "type": "image/png",
            "purpose": "maskable any",
        },
        {
            "src": "/static/icons/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable any",
        },
    ],
    "shortcuts": [
        {
            "name": "Recettes",
            "short_name": "Recettes",
            "description": "Accéder aux recettes",
            "url": "/?module=cuisine.recettes",
            "icons": [{"src": "/static/icons/recipe-96x96.png", "sizes": "96x96"}],
        },
        {
            "name": "Liste de courses",
            "short_name": "Courses",
            "description": "Voir la liste de courses",
            "url": "/?module=cuisine.courses",
            "icons": [{"src": "/static/icons/cart-96x96.png", "sizes": "96x96"}],
        },
        {
            "name": "Planning",
            "short_name": "Planning",
            "description": "Voir le planning des repas",
            "url": "/?module=planning",
            "icons": [{"src": "/static/icons/calendar-96x96.png", "sizes": "96x96"}],
        },
    ],
    "screenshots": [
        {
            "src": "/static/screenshots/home.png",
            "sizes": "1280x720",
            "type": "image/png",
            "form_factor": "wide",
            "label": "Tableau de bord",
        },
        {
            "src": "/static/screenshots/mobile.png",
            "sizes": "750x1334",
            "type": "image/png",
            "form_factor": "narrow",
            "label": "Vue mobile",
        },
    ],
    "related_applications": [],
    "prefer_related_applications": False,
}


# ═══════════════════════════════════════════════════════════
# SERVICE WORKER
# ═══════════════════════════════════════════════════════════


SERVICE_WORKER_JS = """
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
    '/static/css/styles.css',
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
    // Ignorer les requêtes non-GET
    if (event.request.method !== 'GET') return;

    // Ignorer les WebSockets (Streamlit)
    if (event.request.url.includes('_stcore')) return;

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Cloner la réponse pour la mettre en cache
                const responseClone = response.clone();

                // Ne mettre en cache que les ressources statiques
                if (response.ok && isStaticAsset(event.request.url)) {
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }

                return response;
            })
            .catch(() => {
                // Fallback sur le cache
                return caches.match(event.request)
                    .then((cachedResponse) => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }

                        // Page offline pour les documents HTML
                        if (event.request.destination === 'document') {
                            return caches.match(OFFLINE_URL);
                        }

                        return new Response('Offline', {
                            status: 503,
                            statusText: 'Service Unavailable'
                        });
                    });
            })
    );
});

// Vérifier si c'est une ressource statique
function isStaticAsset(url) {
    const staticExtensions = ['.css', '.js', '.png', '.jpg', '.svg', '.ico', '.woff2'];
    return staticExtensions.some(ext => url.endsWith(ext));
}

// Gestion des notifications push
self.addEventListener('push', (event) => {
    console.log('[SW] Push received');

    const data = event.data ? event.data.json() : {};
    const title = data.title || 'Assistant Matanne';
    const options = {
        body: data.body || 'Nouvelle notification',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: data.data || {},
        actions: data.actions || [],
        tag: data.tag || 'default',
        renotify: data.renotify || false,
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// Clic sur notification
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked');
    event.notification.close();

    const urlToOpen = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Chercher une fenêtre existante
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                // Ouvrir une nouvelle fenêtre
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// Synchronisation en arrière-plan
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);

    if (event.tag === 'sync-shopping-list') {
        event.waitUntil(syncShoppingList());
    } else if (event.tag === 'sync-offline-changes') {
        event.waitUntil(syncOfflineChanges());
    }
});

// ═══════════════════════════════════════════════════════════
// INDEXEDDB POUR STOCKAGE OFFLINE
// ═══════════════════════════════════════════════════════════

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            // Store pour la liste de courses
            if (!db.objectStoreNames.contains('shopping_list')) {
                const store = db.createObjectStore('shopping_list', { keyPath: 'id', autoIncrement: true });
                store.createIndex('synced', 'synced', { unique: false });
                store.createIndex('achete', 'achete', { unique: false });
            }

            // Store pour les modifications en attente
            if (!db.objectStoreNames.contains('pending_changes')) {
                const store = db.createObjectStore('pending_changes', { keyPath: 'id', autoIncrement: true });
                store.createIndex('timestamp', 'timestamp', { unique: false });
                store.createIndex('type', 'type', { unique: false });
            }

            // Store pour les recettes favorites (lecture offline)
            if (!db.objectStoreNames.contains('favorite_recipes')) {
                const store = db.createObjectStore('favorite_recipes', { keyPath: 'id' });
            }
        };
    });
}

async function saveToOfflineStore(storeName, data) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const request = store.put(data);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function getFromOfflineStore(storeName) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function clearOfflineStore(storeName) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

// ═══════════════════════════════════════════════════════════
// SYNCHRONISATION LISTE DE COURSES
// ═══════════════════════════════════════════════════════════

async function syncShoppingList() {
    console.log('[SW] Syncing shopping list...');

    try {
        // Récupérer les modifications en attente
        const pendingChanges = await getFromOfflineStore('pending_changes');

        if (pendingChanges.length === 0) {
            console.log('[SW] No pending changes');
            return;
        }

        // Envoyer les modifications au serveur
        for (const change of pendingChanges) {
            try {
                const response = await fetch('/api/courses/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(change)
                });

                if (response.ok) {
                    // Supprimer la modification de la file d'attente
                    await deleteFromOfflineStore('pending_changes', change.id);
                    console.log('[SW] Synced change:', change.id);
                }
            } catch (error) {
                console.error('[SW] Failed to sync change:', change.id, error);
            }
        }

        // Notifier l'utilisateur
        await self.registration.showNotification('Synchronisation terminée', {
            body: `${pendingChanges.length} modification(s) synchronisée(s)`,
            icon: '/static/icons/icon-192x192.png',
            tag: 'sync-complete'
        });

    } catch (error) {
        console.error('[SW] Sync error:', error);
    }
}

async function deleteFromOfflineStore(storeName, id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

async function syncOfflineChanges() {
    console.log('[SW] Syncing all offline changes...');
    await syncShoppingList();
}

// ═══════════════════════════════════════════════════════════
// MESSAGES DEPUIS L'APPLICATION
// ═══════════════════════════════════════════════════════════

self.addEventListener('message', (event) => {
    console.log('[SW] Message received:', event.data);

    if (event.data.type === 'SAVE_OFFLINE') {
        // Sauvegarder des données pour utilisation offline
        saveToOfflineStore(event.data.store, event.data.data)
            .then(() => {
                event.ports[0].postMessage({ success: true });
            })
            .catch((error) => {
                event.ports[0].postMessage({ success: false, error: error.message });
            });
    }

    if (event.data.type === 'GET_OFFLINE') {
        // Récupérer des données offline
        getFromOfflineStore(event.data.store)
            .then((data) => {
                event.ports[0].postMessage({ success: true, data });
            })
            .catch((error) => {
                event.ports[0].postMessage({ success: false, error: error.message });
            });
    }

    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data.type === 'REQUEST_SYNC') {
        // Demander une synchronisation
        self.registration.sync.register('sync-shopping-list')
            .then(() => {
                event.ports[0].postMessage({ success: true });
            })
            .catch((error) => {
                event.ports[0].postMessage({ success: false, error: error.message });
            });
    }
});
"""


OFFLINE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hors ligne - Assistant Matanne</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            text-align: center;
            padding: 20px;
        }
        .container {
            max-width: 400px;
        }
        .icon {
            font-size: 80px;
            margin-bottom: 20px;
        }
        h1 {
            font-size: 24px;
            margin-bottom: 16px;
        }
        p {
            opacity: 0.9;
            line-height: 1.6;
            margin-bottom: 24px;
        }
        button {
            background: white;
            color: #667eea;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: scale(1.05);
        }
        .tips {
            margin-top: 40px;
            font-size: 14px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📴</div>
        <h1>Vous êtes hors ligne</h1>
        <p>
            L'application nécessite une connexion internet pour fonctionner.
            Vérifiez votre connexion et réessayez.
        </p>
        <button onclick="location.reload()">Réessayer</button>
        <div class="tips">
            <p>💡 Astuce: Les données consultées récemment sont disponibles en mode hors ligne.</p>
        </div>
    </div>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE GÉNÉRATION
# ═══════════════════════════════════════════════════════════


def generate_manifest(output_path: str | Path) -> Path:
    """
    Génère le fichier manifest.json.

    Args:
        output_path: Chemin du dossier de sortie

    Returns:
        Chemin du fichier créé
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    manifest_path = output_path / "manifest.json"
    manifest_path.write_text(json.dumps(PWA_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"✅ Manifest généré: {manifest_path}")
    return manifest_path


def generate_service_worker(output_path: str | Path) -> Path:
    """
    Génère le Service Worker.

    Args:
        output_path: Chemin du dossier de sortie

    Returns:
        Chemin du fichier créé
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    sw_path = output_path / "sw.js"
    sw_path.write_text(SERVICE_WORKER_JS, encoding="utf-8")

    logger.info(f"✅ Service Worker généré: {sw_path}")
    return sw_path


def generate_offline_page(output_path: str | Path) -> Path:
    """
    Génère la page offline.

    Args:
        output_path: Chemin du dossier de sortie

    Returns:
        Chemin du fichier créé
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    offline_path = output_path / "offline.html"
    offline_path.write_text(OFFLINE_HTML, encoding="utf-8")

    logger.info(f"✅ Page offline générée: {offline_path}")
    return offline_path


def generate_pwa_files(output_path: str | Path = "static") -> dict[str, Path]:
    """
    Génère tous les fichiers PWA.

    Args:
        output_path: Chemin du dossier de sortie

    Returns:
        Dictionnaire des fichiers créés
    """
    output_path = Path(output_path)

    files = {
        "manifest": generate_manifest(output_path),
        "service_worker": generate_service_worker(output_path),
        "offline": generate_offline_page(output_path),
    }

    # Créer le dossier des icônes
    icons_path = output_path / "icons"
    icons_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"✅ Tous les fichiers PWA générés dans: {output_path}")
    return files


# ═══════════════════════════════════════════════════════════
# INJECTION DANS STREAMLIT
# ═══════════════════════════════════════════════════════════


def is_pwa_installed() -> bool:
    """
    Vérifie si l'app est installée en PWA.

    Note: Ne fonctionne que côté client via JavaScript.
    """
    # Cette vérification doit être faite côté client
    return False


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION D'ICÔNES
# ═══════════════════════════════════════════════════════════


def generate_icon_svg(size: int = 512) -> str:
    """
    Génère un SVG d'icône par défaut.

    Args:
        size: Taille de l'icône

    Returns:
        Code SVG
    """
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
        <rect width="{size}" height="{size}" rx="{size // 8}" fill="url(#grad)"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
              font-size="{size // 2}" font-family="Arial" fill="white">🏠</text>
    </svg>
    """


__all__ = [
    "PWA_CONFIG",
    "generate_manifest",
    "generate_service_worker",
    "generate_offline_page",
    "generate_pwa_files",
    "is_pwa_installed",
    "generate_icon_svg",
]
