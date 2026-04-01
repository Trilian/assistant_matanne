# Référence des Composants UI

Guide des composants UI du frontend Next.js (shadcn/ui + composants layout).

Snapshot phase 10:

- 29 composants UI dans `frontend/src/composants/ui/`
- 82 composants metier/layout hors dossier UI

## Architecture

```
frontend/src/
├── composants/ui/           # Composants shadcn/ui (29 fichiers)
│   ├── avatar.tsx           # Avatar utilisateur
│   ├── badge.tsx            # Badge statut/tag
│   ├── button.tsx           # Bouton (variants: default, outline, ghost, destructive)
│   ├── card.tsx             # Card, CardHeader, CardContent, CardFooter, CardTitle
│   ├── command.tsx          # Command palette (recherche)
│   ├── dialog.tsx           # Dialog modal (Dialog, DialogTrigger, DialogContent)
│   ├── dropdown-menu.tsx    # Menu déroulant contextuel
│   ├── input-group.tsx      # Groupe d'inputs avec icône
│   ├── input.tsx            # Champ texte
│   ├── label.tsx            # Label formulaire
│   ├── scroll-area.tsx      # Zone scrollable
│   ├── select.tsx           # Select dropdown
│   ├── separator.tsx        # Séparateur horizontal
│   ├── sheet.tsx            # Panneau latéral (Sheet/Drawer)
│   ├── sidebar.tsx          # Sidebar navigation complète
│   ├── skeleton.tsx         # Skeleton loader
│   ├── sonner.tsx           # Toasts (notifications via Sonner)
│   ├── table.tsx            # Table, TableHeader, TableBody, TableRow, TableCell
│   ├── tabs.tsx             # Onglets (Tabs, TabsList, TabsTrigger, TabsContent)
│   ├── textarea.tsx         # Zone de texte multilignes
│   └── tooltip.tsx          # Tooltip au survol
├── composants/disposition/  # Composants layout app (5 fichiers)
│   ├── coquille-app.tsx     # Shell principal (sidebar + content)
│   ├── barre-laterale.tsx   # Sidebar avec navigation modules
│   ├── en-tete.tsx          # Header avec breadcrumbs + actions
│   ├── fil-ariane.tsx       # Breadcrumbs
│   └── nav-mobile.tsx       # Bottom navigation bar mobile
├── fournisseurs/            # Providers React
│   ├── fournisseur-query.tsx   # TanStack Query provider
│   ├── fournisseur-auth.tsx    # Protection routes authentifiées
│   └── fournisseur-theme.tsx   # Thème clair/sombre (next-themes)
├── crochets/                # Hooks React personnalisés
│   ├── utiliser-api.ts      # utiliserRequete, utiliserMutation, utiliserInvalidation
│   ├── utiliser-auth.ts     # utiliserAuth (user, login, logout)
│   ├── utiliser-delai.ts    # Debounce de valeurs
│   └── use-mobile.ts        # Détection mobile
└── magasins/                # Zustand stores
    ├── store-auth.ts        # État auth (utilisateur, estConnecte)
    ├── store-ui.ts          # État UI (sidebar, recherche)
    └── store-notifications.ts # File de notifications
```

---

## Composants shadcn/ui

Tous les composants UI de base proviennent de [shadcn/ui](https://ui.shadcn.com/) et sont dans `frontend/src/composants/ui/`. Ils utilisent Tailwind CSS v4 avec les tokens CSS du thème.

### Button

```tsx
import { Button } from "@/components/ui/button"

<Button>Défaut</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Supprimer</Button>
<Button size="sm">Petit</Button>
<Button size="lg">Grand</Button>
```

### Card

```tsx
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"

<Card>
  <CardHeader><CardTitle>Titre</CardTitle></CardHeader>
  <CardContent>Contenu</CardContent>
  <CardFooter>Actions</CardFooter>
</Card>
```

### Dialog

```tsx
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"

<Dialog open={ouvert} onOpenChange={setOuvert}>
  <DialogTrigger asChild><Button>Ouvrir</Button></DialogTrigger>
  <DialogContent>
    <DialogHeader><DialogTitle>Titre</DialogTitle></DialogHeader>
    {/* Formulaire */}
    <DialogFooter><Button onClick={sauvegarder}>Sauvegarder</Button></DialogFooter>
  </DialogContent>
</Dialog>
```

### Tabs

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Onglet 1</TabsTrigger>
    <TabsTrigger value="tab2">Onglet 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Contenu 1</TabsContent>
  <TabsContent value="tab2">Contenu 2</TabsContent>
</Tabs>
```

### Table

```tsx
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow><TableHead>Nom</TableHead><TableHead>Statut</TableHead></TableRow>
  </TableHeader>
  <TableBody>
    <TableRow><TableCell>Item</TableCell><TableCell>Actif</TableCell></TableRow>
  </TableBody>
</Table>
```

### Skeleton (chargement)

```tsx
import { Skeleton } from "@/components/ui/skeleton"

<Skeleton className="h-8 w-full" />        {/* Ligne */}
<Skeleton className="h-32 w-full" />       {/* Carte */}
<Skeleton className="h-4 w-[200px]" />     {/* Texte court */}
```

### Autres composants

| Composant | Usage |
|-----------|-------|
| `Badge` | Tags statut (couleur via `variant`) |
| `Input` | Champ texte avec `placeholder` |
| `Textarea` | Zone texte multiligne |
| `Select` | Dropdown sélection |
| `Label` | Label pour formulaire |
| `Separator` | Ligne séparatrice |
| `Avatar` | Photo/initiales utilisateur |
| `Tooltip` | Info-bulle au survol |
| `Sheet` | Panneau latéral (mobile) |
| `ScrollArea` | Zone scrollable personnalisée |
| `DropdownMenu` | Menu contextuel |
| `Sonner` | Notifications toast |

---

## Composants Layout

### CoquilleApp (coquille-app.tsx)

Wrapper principal de l'application : sidebar + zone de contenu.

```tsx
import { CoquilleApp } from "@/composants/disposition/coquille-app"

<CoquilleApp>{children}</CoquilleApp>
```

### BarreLaterale (barre-laterale.tsx)

Navigation principale : modules Cuisine, Famille, Maison, Jeux, Outils, Paramètres. Repliable sur desktop, sheet sur mobile.

### EnTete (en-tete.tsx)

Header avec fil d'ariane et actions (recherche, notifications).

### NavMobile (nav-mobile.tsx)

Bottom bar mobile avec 5 icônes de navigation rapide.

---

## Hooks personnalisés

### utiliserRequete / utiliserMutation / utiliserInvalidation

```tsx
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api"

// Requête
const { data, isLoading, error } = utiliserRequete(["recettes"], listerRecettes)

// Mutation
const mutation = utiliserMutation(creerRecette, {
  onSuccess: () => invalider(["recettes"])
})

// Invalidation
const invalider = utiliserInvalidation()
invalider(["recettes"])  // Rafraîchit les requêtes recettes
```

### utiliserAuth

```tsx
import { utiliserAuth } from "@/crochets/utiliser-auth"

const { utilisateur, estConnecte, connexion, deconnexion } = utiliserAuth()
```

---

## Stores Zustand

### store-auth

```tsx
import { utiliserStoreAuth } from "@/magasins/store-auth"

const { utilisateur, estConnecte, definirUtilisateur, reinitialiser } = utiliserStoreAuth()
```

### store-ui

```tsx
import { utiliserStoreUI } from "@/magasins/store-ui"

const { sidebarOuverte, basculerSidebar, rechercheOuverte, basculerRecherche } = utiliserStoreUI()
```

---

## Pattern CRUD typique (page)

Chaque page avec CRUD suit ce pattern :

```tsx
'use client'

import { useState } from "react"
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api"
import { listerItems, creerItem, supprimerItem } from "@/bibliotheque/api/mon-domaine"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"

export default function MonModulePage() {
  const [dialogOuvert, setDialogOuvert] = useState(false)
  const invalider = utiliserInvalidation()

  const { data: items, isLoading } = utiliserRequete(["items"], listerItems)

  const mutationCreer = utiliserMutation(creerItem, {
    onSuccess: () => { invalider(["items"]); setDialogOuvert(false) }
  })

  if (isLoading) return <Skeleton className="h-32 w-full" />

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Mon Module</h1>
        <Button onClick={() => setDialogOuvert(true)}>Ajouter</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items?.map(item => (
          <Card key={item.id}>
            <CardHeader><CardTitle>{item.nom}</CardTitle></CardHeader>
            <CardContent>{/* Détails */}</CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nouvel item</DialogTitle></DialogHeader>
          {/* Formulaire */}
          <DialogFooter>
            <Button onClick={() => mutationCreer.mutate(formData)}>
              Créer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
```

---

## Icônes

L'application utilise [lucide-react](https://lucide.dev/) pour les icônes :

```tsx
import { Plus, Pencil, Trash2, Search, Star, Calendar, Home } from "lucide-react"

<Plus className="h-4 w-4" />
<Button><Pencil className="mr-2 h-4 w-4" /> Modifier</Button>
```

---

## Intégrations (integrations/)

### Google Calendar

```python
from src.ui.integrations import (
    verifier_config_google,
    afficher_config_google_calendar,
    afficher_statut_sync_google,
    afficher_bouton_sync_rapide,
    GOOGLE_SCOPES,
    REDIRECT_URI_LOCAL
)

# Vérifier la configuration
if verifier_config_google():
    afficher_statut_sync_google()
    afficher_bouton_sync_rapide()
else:
    afficher_config_google_calendar()
```

---

## Vues Extraites (views/)

Fonctions d'affichage extraites des services pour respecter la séparation UI/logique.

### Authentification (authentification.py)

```python
from src.ui.views import (
    afficher_formulaire_connexion,
    afficher_menu_utilisateur,
    afficher_parametres_profil,
    require_authenticated,
    require_role,
)

# Formulaire de connexion
afficher_formulaire_connexion(rediriger_apres_succes=True)

# Menu utilisateur dans la sidebar
afficher_menu_utilisateur()

# Page paramètres profil
afficher_parametres_profil()

# Décorateurs de protection (backend FastAPI)
@router.get("/protege")
async def page_protegee(user: dict = Depends(require_auth)):
    return {"message": "Contenu protégé"}

@router.get("/admin")
async def page_admin(user: dict = Depends(require_role("admin"))):
    return {"message": "Admin uniquement"}
```

### Historique (historique.py)

```python
from src.ui.views import afficher_timeline_activite, afficher_activite_utilisateur, afficher_statistiques_activite

# Timeline d'activité récente (10 dernières par défaut)
afficher_timeline_activite(limit=10)

# Activité d'un utilisateur spécifique
afficher_activite_utilisateur(user_id="...")

# Statistiques d'activité globales
afficher_statistiques_activite()
```

### Import Recettes (import_recettes.py)

```python
from src.ui.views import afficher_import_recette

# Interface d'import URL/PDF
afficher_import_recette()
```

### Notifications Push (notifications.py)

```python
from src.ui.views import afficher_demande_permission_push, afficher_preferences_notification

# Demander permission push au navigateur
afficher_demande_permission_push()

# Paramètres de notifications
afficher_preferences_notification()
```

### Météo Jardin (meteo.py)

```python
from src.ui.views import afficher_meteo_jardin

# Alertes météo pour le jardin
afficher_meteo_jardin()
```

### Sauvegarde (sauvegarde.py)

```python
from src.ui.views import afficher_sauvegarde

# Interface backup/restauration complète
afficher_sauvegarde()
```

### Synchronisation (synchronisation.py)

```python
from src.ui.views import (
    afficher_indicateur_presence,
    afficher_indicateur_frappe,
    afficher_statut_synchronisation,
    afficher_invite_installation_pwa,
)

# Utilisateurs connectés en temps réel
afficher_indicateur_presence()

# Indicateurs de frappe
afficher_indicateur_frappe()

# Statut sync
afficher_statut_synchronisation()

# Bouton install PWA
afficher_invite_installation_pwa()
```

### Jeux (jeux.py)

```python
from src.ui.views import afficher_badge_notifications_jeux, afficher_notification_jeux, afficher_liste_notifications_jeux

# Badge compteur non-lues
afficher_badge_notifications_jeux(service=None)

# Notification individuelle
afficher_notification_jeux(notification)

# Liste paginée
afficher_liste_notifications_jeux(service=None, limite=10, type_jeu=None)
```

### PWA (pwa.py)

```python
from src.ui.views import injecter_meta_pwa

# Appelé dans app.py après injecter_css()
injecter_meta_pwa()
```

---

## Bonnes Pratiques

### Import Recommandé

```python
# ✅ Import depuis le point d'entrée unifié
from src.ui import badge, carte_metrique_avancee, afficher_succes, etat_vide

# ✅ Import spécifique par sous-package
from src.ui.tablet import ModeTablette, obtenir_mode_tablette
from src.ui.views import afficher_timeline_activite
from src.ui.integrations import verifier_config_google

# ✅ Import dans _common.py des modules métier
from src.ui.components.atoms import etat_vide  # re-exporté via _common.py

# ❌ Éviter les imports profonds dans le code métier
from src.ui.components.atoms import badge  # Préférer from src.ui import badge
```

### Motif état vide

Utiliser le composant `EtatVide` (frontend) pour les états vides :

```tsx
// Composant React unifié
<EtatVide
  titre="Aucune recette trouvée"
  icone="🍽️"
  description="Ajoutez votre première recette"
/>
```

### Cache

Les calculs coûteux utilisent `@avec_cache` (décorateur multi-niveaux) :

- Graphiques: `ttl=300` (5 min)
- Métriques: `ttl=60` (1 min)

### Performance

Pour le chargement différé des modules, les services utilisent `@service_factory` (singleton via registre).
Chaque domaine expose ses routes dans `src/api/routes/` et ses pages dans `frontend/src/app/(app)/`.

### Nommage

- Fonctions d'affichage : `afficher_*()`
- Fonctions d'obtention : `obtenir_*()`
- Fonctions de définition : `definir_*()`
- Classes : `NomEnFrancais` (PascalCase)
- Constantes : `NOM_EN_MAJUSCULES`

---

## Imports Rapides

```python
# Point d'entrée unifié (~90 exports)
from src.ui import badge, carte_metrique_avancee, afficher_succes

# Sous-packages spécifiques
from src.ui.components import graphique_repartition_repas
from src.ui.feedback import spinner_intelligent, SuiviProgression
from src.ui.tablet import ModeTablette, bouton_tablette
from src.ui.views import afficher_sauvegarde, afficher_timeline_activite
from src.ui.integrations import verifier_config_google

# Layout (réservé à app.py)
from src.ui.layout import afficher_header, afficher_sidebar, injecter_css
```
