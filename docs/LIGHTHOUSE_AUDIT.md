# Audit Lighthouse — Assistant Matanne

## Optimisations en place

### Images

| Technique | État | Détails |
|-----------|------|---------|
| `next/image` (recettes grid) | ✅ | `fill` + `sizes` responsive, lazy loading auto |
| `next/image` (habitat plans/déco) | ✅ | Déjà configuré |
| `loading="lazy"` (IA previews) | ✅ | estimation-travaux, diagnostic-plante, analyse-photo, analyse-document |
| `loading="lazy"` (calendrier mosaïque) | ✅ | Vignettes repas dans le planning |
| Formats modernes (avif/webp) | ✅ | `next.config.ts` → `formats: ["image/avif", "image/webp"]` |
| Cache images 30 jours | ✅ | `minimumCacheTTL: 2592000` |

### Code Splitting / Lazy Loading

| Technique | État | Détails |
|-----------|------|---------|
| `next/dynamic` recharts | ✅ | SSR=false sur tous les graphiques (jeux, famille, habitat) |
| Route-based splitting | ✅ | App Router split automatique par page |
| Composants lourds dynamiques | ✅ | Heatmap côtes, graphiques marché, performance charts |

### Fonts

| Technique | État | Détails |
|-----------|------|---------|
| `next/font/google` | ✅ | Geist Sans + Geist Mono, self-hosted |
| `subsets: ["latin"]` | ✅ | Réduit la taille du bundle police |
| CSS variables | ✅ | `--font-geist-sans`, `--font-geist-mono` |

### Réseau

| Technique | État | Détails |
|-----------|------|---------|
| DNS prefetch (picsum.photos) | ✅ | `<link rel="dns-prefetch">` dans layout.tsx |
| Route prefetch (sidebar) | ✅ | `onMouseEnter` + `onFocus` prefetch |
| Route prefetch (nav mobile) | ✅ | `onMouseEnter` + `onTouchStart` prefetch |

### Sécurité & Headers

| Technique | État | Détails |
|-----------|------|---------|
| CSP strict | ✅ | Défini dans next.config.ts |
| HSTS | ✅ | max-age=63072000, includeSubDomains, preload |
| Security headers complets | ✅ | X-Frame-Options, X-Content-Type-Options, Referrer-Policy |

### Monitoring

| Technique | État | Détails |
|-----------|------|---------|
| Sentry (conditionnel) | ✅ | Chargé uniquement si DSN configuré |
| Bundle analyzer | ✅ | `@next/bundle-analyzer` disponible via `ANALYZE=true` |

## Non applicable (justifié)

| Technique | Raison |
|-----------|--------|
| ISR / `revalidate` | App 100% `'use client'` avec auth JWT — pas de pages statiques |
| `generateStaticParams` | Contenu dynamique authentifié uniquement |
| CDN images hero | Images générées par IA ou uploadées par l'utilisateur |

## Commandes utiles

```bash
# Analyse du bundle
cd frontend && ANALYZE=true npm run build

# Lighthouse CLI (nécessite Chrome)
npx lighthouse http://localhost:3000 --output=html --output-path=./lighthouse-report.html
```
