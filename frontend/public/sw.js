const CACHE_NAME = "matanne-v2";
const API_CACHE = "matanne-api-v1";
const OFFLINE_URL = "/offline.html";

const PRECACHE_URLS = [
  "/",
  "/offline.html",
  "/manifest.json",
  "/cuisine",
  "/famille",
  "/maison",
  "/jeux",
  "/parametres",
];

// API paths to cache (stale-while-revalidate)
const CACHEABLE_API = [
  "/api/v1/recettes",
  "/api/v1/preferences",
  "/api/v1/maison/hub/stats",
  "/api/v1/dashboard",
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
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clients) => {
      if (clients.length > 0) return clients[0].focus();
      return self.clients.openWindow("/");
    })
  );
});
