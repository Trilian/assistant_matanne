# Guide PWA / Mode Offline — Assistant Matanne

> **Service Worker** : `frontend/public/sw.js` (custom, non Workbox)  
> **Manifest** : `frontend/public/manifest.json`  
> **Composant install** : `frontend/src/composants/pwa/install-prompt.tsx`  
> **Enregistrement SW** : `frontend/src/composants/enregistrement-sw.tsx`

---

## Architecture PWA

```
frontend/
├── public/
│   ├── sw.js              ← Service Worker principal (stratégies de cache)
│   ├── manifest.json      ← Manifest PWA (icônes, nom, start_url)
│   └── offline.html       ← Page hors-ligne de fallback
├── src/composants/
│   ├── pwa/
│   │   └── install-prompt.tsx  ← Bouton "Installer l'app"
│   └── enregistrement-sw.tsx   ← Enregistrement du Service Worker
```

---

## Service Worker — Stratégies de cache

Le SW utilise **3 stratégies** selon le type de ressource :

### 1. Navigation (pages HTML) — Network-first avec fallback offline

```javascript
// sw.js — Navigation requests
if (event.request.mode === "navigate") {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache la page pour offline
        const clone = response.clone();
        caches.open(CACHE_NAME).then((c) => c.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(OFFLINE_URL))  // Fallback: /offline.html
  );
}
```

### 2. API (`/api/v1/*`) — Stale-While-Revalidate

Les endpoints API critiques sont servis depuis le cache pendant que la mise à jour se fait en arrière-plan.

```javascript
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

// Stratégie : retourne le cache immédiatement + fetch en background
```

### 3. Assets statiques (JS, CSS, images) — Cache-first

Les ressources statiques sont servies depuis le cache sans aller au réseau.

### 4. Autres requêtes — Network-only

Tout le reste (mutations POST/PUT/DELETE) va toujours au réseau.

---

## Pre-cache (install)

Les pages suivantes sont précachées lors de l'installation du SW :

```javascript
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
```

---

## Gestion des versions de cache

```javascript
const CACHE_NAME = "matanne-v3";     // Cache pages + assets
const API_CACHE = "matanne-api-v2";  // Cache API responses
```

**Mise à jour** : Lors de l'activation, tous les anciens caches (différents de `CACHE_NAME` et `API_CACHE`) sont supprimés automatiquement.

```javascript
// Activation — nettoyage des anciens caches
caches.keys().then((keys) =>
  Promise.all(
    keys
      .filter((k) => k !== CACHE_NAME && k !== API_CACHE)
      .map((k) => caches.delete(k))
  )
);
```

**Mise à jour de version** : Incrémenter `CACHE_NAME = "matanne-v4"` dans `sw.js` → le SW sera mis à jour à la prochaine visite.

---

## Manifest PWA

```json
{
  "name": "Assistant Matanne",
  "short_name": "Matanne",
  "description": "Hub de gestion familiale - Recettes, Courses, Planning",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#000000",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

---

## Enregistrement du Service Worker

Le composant `EnregistrementSW` s'enregistre au montage de l'application :

```tsx
// src/composants/enregistrement-sw.tsx
"use client";
useEffect(() => {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker
      .register("/sw.js", { scope: "/" })
      .then((registration) => {
        console.log("SW enregistré:", registration.scope);
      })
      .catch((error) => {
        console.warn("SW non enregistré:", error);
      });
  }
}, []);
```

---

## Page hors-ligne

La page `offline.html` s'affiche quand l'utilisateur tente une navigation sans connexion et que la page n'est pas en cache.

```html
<!-- public/offline.html — page statique autonome -->
<!DOCTYPE html>
<html lang="fr">
<head><title>Assistant Matanne — Hors ligne</title></head>
<body>
  <h1>Vous êtes hors ligne</h1>
  <p>Certaines fonctionnalités sont disponibles (recettes, planning, courses en cache).</p>
  <button onclick="window.location.reload()">Réessayer</button>
</body>
</html>
```

---

## Installer l'app sur Android (Google Chrome / tablette)

1. Ouvrir `https://matanne.vercel.app` dans Chrome
2. Menu Chrome → "Ajouter à l'écran d'accueil"
3. L'app s'ouvre en mode standalone (sans barre d'adresse)

---

## Notifications Push

Les notifications push sont gérées séparément des stratégies de cache (voir `docs/NOTIFICATIONS.md`).

Le SW écoute l'événement `push` :
```javascript
self.addEventListener("push", (event) => {
  const data = event.data?.json() ?? {};
  event.waitUntil(
    self.registration.showNotification(data.title ?? "Matanne", {
      body: data.body,
      icon: "/icons/icon-192.png",
    })
  );
});
```

---

## Mettre à jour le Service Worker

1. Modifier `frontend/public/sw.js`
2. Incrémenter `CACHE_NAME` si le contenu du cache change
3. Builder le frontend : `cd frontend && npm run build`
4. Déployer — les utilisateurs verront le nouveau SW à la prochaine visite

> ⚠️ Les changements au SW ne sont pas pris en compte immédiatement.  
> L'ancien SW continue à tourner jusqu'à ce que toutes les fenêtres soient fermées.  
> Pour forcer la mise à jour : `skipWaiting()` est appelé dans l'event `install` (déjà en place).

---

## Tester le mode offline

1. Ouvrir DevTools → Application → Service Workers
2. Cocher "Offline" dans le panneau Network
3. Naviguer vers `/cuisine` — devrait charger depuis le cache
4. Naviguer vers une page non-visitée — `offline.html` doit s'afficher

---

## Voir aussi

- [NOTIFICATIONS.md](../NOTIFICATIONS.md) — Notifications push
- [DEPLOYMENT.md](../DEPLOYMENT.md) — Variables d'env `VAPID_*`
