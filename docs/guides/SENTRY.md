# Guide Sentry â€” Monitoring d'Erreurs

> **Stack** : `@sentry/nextjs` (frontend) â€” Backend non intÃ©grÃ© (optionnel)  
> **Environnement** : ActivÃ© uniquement si `NEXT_PUBLIC_SENTRY_DSN` est dÃ©fini  
> **Fichiers config** : `sentry.client.config.ts`, `sentry.server.config.ts`, `sentry.edge.config.ts`

---

## Configuration actuelle

### Variables d'environnement

```bash
# Dans .env.local (root du projet)
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@oxxxxx.ingest.sentry.io/xxxxx
NEXT_PUBLIC_ENVIRONMENT=production  # ou staging, development
```

> âš ï¸ Si `NEXT_PUBLIC_SENTRY_DSN` est absent ou vide, Sentry est **silencieusement dÃ©sactivÃ©**.
> Aucune erreur n'est levÃ©e â€” le code est protÃ©gÃ© par un `try/catch` dans chaque fichier config.

### Sampling rates

| Contexte | ParamÃ¨tre | Valeur |
| --------- | ----------- | -------- |
| Client (browser) | `tracesSampleRate` | 10% |
| Client â€” Session Replay sur erreur | `replaysOnErrorSampleRate` | 100% |
| Client â€” Session Replay global | `replaysSessionSampleRate` | 10% |
| Server (Node.js) | `tracesSampleRate` | 10% |
| Edge (middleware) | `tracesSampleRate` | 10% |

### Session Replay

Le Replay masque **tout le texte** (`maskAllText: true`) et **tous les mÃ©dias** (`blockAllMedia: true`).  
Cela protÃ¨ge les donnÃ©es personnelles (RGPD) : aucune donnÃ©e sensible n'apparaÃ®t dans le replay.

---

## Installation depuis zÃ©ro

### 1. CrÃ©er un projet Sentry

1. Aller sur [sentry.io](https://sentry.io) â†’ CrÃ©er un projet **Next.js**
2. Copier le DSN (format `https://xxxxx@xxxxxxx.ingest.sentry.io/xxxxxx`)

### 2. Installer le package (si nÃ©cessaire)

```bash
cd frontend
npm install @sentry/nextjs
```

> Le package est en dÃ©pendance optionnelle â€” les fichiers config utilisent `require()` dynamique
> protÃ©gÃ© par `try/catch` pour Ã©viter les erreurs si le package n'est pas installÃ©.

### 3. Configurer les variables

```bash
# .env.local (racine projet)
NEXT_PUBLIC_SENTRY_DSN=https://votre-dsn@o123456.ingest.sentry.io/123456
NEXT_PUBLIC_ENVIRONMENT=production
```

### 4. Configurer next.config.ts (si Sentry Webpack plugin nÃ©cessaire)

```typescript
// frontend/next.config.ts â€” optionnel pour source maps
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

// AprÃ¨s connexion rÃ©ussie :
Sentry.setUser({
  id: utilisateur.id,
  email: utilisateur.email,
});

// Lors de la dÃ©connexion :
Sentry.setUser(null);
```

---

## Alertes et notifications Sentry

### Configuration recommandÃ©e

Dans le dashboard Sentry â†’ Alerts â†’ Create Alert Rule :

| Condition | Alerte |
| ----------- | -------- |
| Erreur nouvellement dÃ©tectÃ©e | Notification immÃ©diate |
| >10 occurrences en 1h | Notification critique |
| Performance dÃ©gradÃ©e (>2s) | Alerte performance |

---

## Mode dÃ©veloppement

En dÃ©veloppement (`NEXT_PUBLIC_ENVIRONMENT=development`), dÃ©sactiver les logs de debug :

```bash
# .env.local
NEXT_PUBLIC_SENTRY_DSN=  # laisser vide pour dÃ©sactiver
```

Ou laisser vide et Sentry sera silencieusement dÃ©sactivÃ© (comportement par dÃ©faut).

---

## Voir aussi

- [DEPLOYMENT.md](../DEPLOYMENT.md) â€” Variables d'environnement Railway / Vercel
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) â€” DÃ©pannage gÃ©nÃ©ral
