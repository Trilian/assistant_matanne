# Guide Sentry — Monitoring d'Erreurs

> **Stack** : `@sentry/nextjs` (frontend) — Backend non intégré (optionnel)  
> **Environnement** : Activé uniquement si `NEXT_PUBLIC_SENTRY_DSN` est défini  
> **Fichiers config** : `sentry.client.config.ts`, `sentry.server.config.ts`, `sentry.edge.config.ts`

---

## Configuration actuelle

### Variables d'environnement

```bash
# Dans .env.local (root du projet)
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@oxxxxx.ingest.sentry.io/xxxxx
NEXT_PUBLIC_ENVIRONMENT=production  # ou staging, development
```

> ⚠️ Si `NEXT_PUBLIC_SENTRY_DSN` est absent ou vide, Sentry est **silencieusement désactivé**.
> Aucune erreur n'est levée — le code est protégé par un `try/catch` dans chaque fichier config.

### Sampling rates

| Contexte | Paramètre | Valeur |
| --------- | ----------- | -------- |
| Client (browser) | `tracesSampleRate` | 10% |
| Client — Session Replay sur erreur | `replaysOnErrorSampleRate` | 100% |
| Client — Session Replay global | `replaysSessionSampleRate` | 10% |
| Server (Node.js) | `tracesSampleRate` | 10% |
| Edge (middleware) | `tracesSampleRate` | 10% |

### Session Replay

Le Replay masque **tout le texte** (`maskAllText: true`) et **tous les médias** (`blockAllMedia: true`).  
Cela protège les données personnelles (RGPD) : aucune donnée sensible n'apparaît dans le replay.

---

## Installation depuis zéro

### 1. Créer un projet Sentry

1. Aller sur [sentry.io](https://sentry.io) → Créer un projet **Next.js**
2. Copier le DSN (format `https://xxxxx@xxxxxxx.ingest.sentry.io/xxxxxx`)

### 2. Installer le package (si nécessaire)

```bash
cd frontend
npm install @sentry/nextjs
```

> Le package est en dépendance optionnelle — les fichiers config utilisent `require()` dynamique
> protégé par `try/catch` pour éviter les erreurs si le package n'est pas installé.

### 3. Configurer les variables

```bash
# .env.local (racine projet)
NEXT_PUBLIC_SENTRY_DSN=https://votre-dsn@o123456.ingest.sentry.io/123456
NEXT_PUBLIC_ENVIRONMENT=production
```

### 4. Configurer next.config.ts (si Sentry Webpack plugin nécessaire)

```typescript
// frontend/next.config.ts — optionnel pour source maps
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig = { ... };

export default withSentryConfig(nextConfig, {
  org: "votre-org",
  project: "assistant-matanne",
  silent: !process.env.CI,
  widenClientFileUpload: true,
  hideSourceMaps: true,
  disableLogger: true,
});
```

---

## Capturer des erreurs manuellement

### Dans les composants React

```tsx
import * as Sentry from "@sentry/nextjs";

function MonComposant() {
  const handleAction = async () => {
    try {
      await appelApi();
    } catch (error) {
      Sentry.captureException(error, {
        tags: { module: "cuisine", action: "creer-recette" },
        user: { email: utilisateur?.email },
      });
      toast.error("Une erreur est survenue");
    }
  };
}
```

### Error Boundaries React

```tsx
// frontend/src/composants/error-boundary.tsx
"use client";
import * as Sentry from "@sentry/nextjs";

export class ErrorBoundary extends React.Component {
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    Sentry.captureException(error, { extra: { componentStack: info.componentStack } });
  }
  render() {
    return this.state.hasError ? <FallbackUI /> : this.props.children;
  }
}
```

### Dans les Server Actions / API Routes Next.js

```typescript
import * as Sentry from "@sentry/nextjs";

export async function POST(request: Request) {
  try {
    const data = await request.json();
    // ...
  } catch (error) {
    Sentry.captureException(error);
    return Response.json({ error: "Erreur interne" }, { status: 500 });
  }
}
```

---

## Ajouter le contexte utilisateur

```typescript
// Dans le provider auth (frontend/src/fournisseurs/fournisseur-auth.tsx)
import * as Sentry from "@sentry/nextjs";

// Après connexion réussie :
Sentry.setUser({
  id: utilisateur.id,
  email: utilisateur.email,
});

// Lors de la déconnexion :
Sentry.setUser(null);
```

---

## Alertes et notifications Sentry

### Configuration recommandée

Dans le dashboard Sentry → Alerts → Create Alert Rule :

| Condition | Alerte |
| ----------- | -------- |
| Erreur nouvellement détectée | Notification immédiate |
| >10 occurrences en 1h | Notification critique |
| Performance dégradée (>2s) | Alerte performance |

---

## Mode développement

En développement (`NEXT_PUBLIC_ENVIRONMENT=development`), désactiver les logs de debug :

```bash
# .env.local
NEXT_PUBLIC_SENTRY_DSN=  # laisser vide pour désactiver
```

Ou laisser vide et Sentry sera silencieusement désactivé (comportement par défaut).

---

## Voir aussi

- [DEPLOYMENT.md](../DEPLOYMENT.md) — Variables d'environnement Railway / Vercel
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) — Dépannage général
