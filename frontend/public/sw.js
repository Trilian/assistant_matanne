const CACHE_NAME = "matanne-v4";
const API_CACHE = "matanne-api-v3";
const OFFLINE_URL = "/offline.html";
const SYNC_QUEUE = "matanne-sync-queue";

const PRECACHE_URLS = [
  "/",
  "/offline.html",
  "/manifest.json",
  "/cuisine",
  "/famille",
  "/maison",
  "/jeux",
  "/parametres",
  "/planning",
];

// API paths to cache (stale-while-revalidate)
const CACHEABLE_API = [
  "/api/v1/recettes",
  "/api/v1/preferences",
  "/api/v1/maison/hub/stats",
  "/api/v1/dashboard",
  "/api/v1/planning/semaine",
  "/api/v1/courses",
  "/api/v1/inventaire",
  "/api/v1/famille/activites",
  "/api/v1/maison/charges",
  "/api/v1/push/rappels/evaluer",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== CACHE_NAME && k !== API_CACHE)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Navigation requests: network-first with offline fallback
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cache successful navigation for offline
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request).then((c) => c || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // API mutations: network with offline queue fallback
  const isApiMutation =
    url.pathname.startsWith("/api/") &&
    ["POST", "PUT", "PATCH", "DELETE"].includes(event.request.method);

  if (isApiMutation) {
    event.respondWith(
      fetch(event.request.clone()).catch(async () => {
        const body = await event.request.text().catch(() => null);
        const headers = {};
        event.request.headers.forEach((v, k) => { headers[k] = v; });
        await mettreDansFile({
          url: event.request.url,
          method: event.request.method,
          headers,
          body,
          timestamp: Date.now(),
        });
        if (self.registration.sync) {
          await self.registration.sync.register(SYNC_QUEUE);
        }
        return new Response(
          JSON.stringify({ offline: true, message: "Requête enregistrée pour synchronisation" }),
          { status: 202, headers: { "Content-Type": "application/json" } }
        );
      })
    );
    return;
  }

  // API requests: stale-while-revalidate for cacheable endpoints
  if (url.pathname.startsWith("/api/") && event.request.method === "GET") {
    const isCacheable = CACHEABLE_API.some((p) => url.pathname.startsWith(p));
    if (isCacheable) {
      event.respondWith(
        caches.open(API_CACHE).then((cache) =>
          cache.match(event.request).then((cached) => {
            const fetchPromise = fetch(event.request)
              .then((response) => {
                if (response.ok) {
                  cache.put(event.request, response.clone());
                }
                return response;
              })
              .catch(() => cached);

            return cached || fetchPromise;
          })
        )
      );
      return;
    }
    // Non-cacheable API: network only
    return;
  }

  // Static assets: cache-first
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        // Cache static assets (JS, CSS, images)
        if (response.ok && (url.pathname.match(/\.(js|css|png|jpg|svg|woff2?)$/))) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      });
    })
  );
});

self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || "Assistant Matanne";
  const options = {
    body: data.body || "Nouvelle notification",
    icon: "/icons/icon-192x192.png",
    badge: "/icons/icon-72x72.png",
    tag: data.tag || "matanne-notification",
    data: data.data || {},
    actions: data.actions || [],
    vibrate: data.vibrate || [100, 50, 100],
    requireInteraction: Boolean(data.requireInteraction),
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const payload = event.notification.data || {};
  const action = event.action;

  if (action === "dismiss") {
    return;
  }

  let urlCible = payload.url || "/";
  if (action === "add_to_cart") {
    const article = payload.article_nom;
    if (article) {
      urlCible = `/?action=add-stock&article=${encodeURIComponent(String(article))}`;
    } else {
      urlCible = "/?action=add-stock";
    }
  } else if (action === "voir_recette") {
    urlCible = payload.url || "/cuisine/recettes?filtre=anti-gaspillage";
  }

  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if ("focus" in client) {
          client.focus();
          if ("navigate" in client) {
            return client.navigate(urlCible);
          }
          return client;
        }
      }
      return self.clients.openWindow(urlCible);
    })
  );
});

// ─── Background Sync (mutations hors-ligne) ─────────────────


/**
 * Lorsque la connectivité est rétablie, rejoue les requêtes
 * POST/PUT/PATCH/DELETE mises en file d'attente hors-ligne.
 */
self.addEventListener("sync", (event) => {
  if (event.tag === SYNC_QUEUE) {
    event.waitUntil(rejouerFileDAttente());
  }
});

async function rejouerFileDAttente() {
  const db = await ouvrirIDB();
  const tx = db.transaction("queue", "readwrite");
  const store = tx.objectStore("queue");
  const items = await storeGetAll(store);

  for (const item of items) {
    try {
      await fetch(item.url, {
        method: item.method,
        headers: item.headers,
        body: item.body,
      });
      await store.delete(item.id);
    } catch {
      // Connexion toujours absente — on garde la requête en file
    }
  }
  await tx.done;
}

// ─── Helpers IndexedDB ──────────────────────────────────────

function ouvrirIDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open("matanne-sync", 1);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains("queue")) {
        db.createObjectStore("queue", { keyPath: "id", autoIncrement: true });
      }
    };
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror = (e) => reject(e.target.error);
  });
}

async function mettreDansFile(item) {
  const db = await ouvrirIDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction("queue", "readwrite");
    tx.objectStore("queue").add(item);
    tx.oncomplete = resolve;
    tx.onerror = (e) => reject(e.target.error);
  });
}

function storeGetAll(store) {
  return new Promise((resolve, reject) => {
    const req = store.getAll();
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror = (e) => reject(e.target.error);
  });
}
