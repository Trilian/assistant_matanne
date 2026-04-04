# Audit OWASP — Phase 2

> Mise à jour : **04/04/2026**  
> Scope : backend FastAPI, frontend Next.js, endpoints sensibles et stockages chiffrés.

## Résumé

La base de sécurité est **bonne et active** sur les points critiques : authentification JWT, contrôle d'accès par dépendances, rate limiting, headers HTTP de sécurité, CORS strict et chiffrement des exports/valeurs sensibles.

La vague Phase 2 a renforcé le coffre-fort `mots_de_passe_maison` pour garantir un **chiffrement au stockage côté API** avant écriture en base.

## Checklist OWASP Top 10

| Catégorie | Statut | Éléments vérifiés | Références |
| --- | --- | --- | --- |
| A01 — Broken Access Control | ✅ | `require_auth`, `require_role`, routes admin protégées | `src/api/dependencies.py`, `src/api/routes/admin_*.py` |
| A02 — Cryptographic Failures | ✅ | JWT signés, exports chiffrés, coffre-fort maison chiffré au stockage | `src/api/auth.py`, `src/services/utilitaires/export_service.py`, `src/api/routes/utilitaires.py` |
| A03 — Injection | ✅ | SQLAlchemy ORM + validation Pydantic + sanitation centralisée | `src/core/validation/sanitizer.py`, `src/api/schemas/` |
| A04 — Insecure Design | 🟡 | Garde-fous présents, revue continue des flux legacy à finir | `PLANNING_IMPLEMENTATION.html`, `src/services/**/inter_module_*.py` |
| A05 — Security Misconfiguration | ✅ | CORS fail-fast, `SecurityHeadersMiddleware`, secrets via env | `src/api/main.py`, `src/api/utils/security_headers.py` |
| A06 — Vulnerable Components | 🟡 | Dépendances centralisées, revue régulière à maintenir | `pyproject.toml`, `frontend/package.json` |
| A07 — Identification & Authentication Failures | ✅ | JWT, 2FA, rate limiting anti brute-force | `src/api/auth.py`, `src/api/routes/auth.py` |
| A08 — Software & Data Integrity Failures | 🟡 | Pipeline/lockfiles existants, audit dépendances à poursuivre | `requirements.txt`, `frontend/package-lock.json` |
| A09 — Security Logging & Monitoring Failures | ✅ | Logs admin/sécurité + métriques Prometheus | `src/api/routes/admin_audit.py`, `src/api/prometheus.py` |
| A10 — SSRF | 🟡 | Appels externes encapsulés et limités, revue continue sur intégrations | `src/core/decorators/validation.py`, `src/services/integrations/` |

## Points livrés pendant cette phase

- ✅ Chiffrement au stockage des entrées `mots_de_passe_maison` avant `INSERT` / `UPDATE`
- ✅ Tests de non-régression backend sur ce chiffrement
- ✅ Couverture frontend renforcée sur les composants structurants (`barre-laterale`, `en-tete`, `fil-ariane`, `coquille-app`)
- ✅ Documentation `API_SCHEMAS.md` régénérée

## Reste à suivre

- Consolider les bridges legacy encore dispersés dans `src/services/**/inter_module_*.py`
- Continuer la revue des tables SQL legacy déjà auditées dans la vague SQL
- Maintenir la revue régulière des dépendances Python/Node lors des montées de version
