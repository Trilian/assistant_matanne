# RÃ©fÃ©rence des Composants UI

Guide des composants UI du frontend Next.js (shadcn/ui + composants layout).

Snapshot phase 10:

- 29 composants UI dans `frontend/src/composants/ui/`
- 82 composants metier/layout hors dossier UI

## Architecture

```
frontend/src/
â”œâ”€â”€ composants/ui/           # Composants shadcn/ui (29 fichiers)
â”‚   â”œâ”€â”€ avatar.tsx           # Avatar utilisateur
â”‚   â”œâ”€â”€ badge.tsx            # Badge statut/tag
â”‚   â”œâ”€â”€ button.tsx           # Bouton (variants: default, outline, ghost, destructive)
â”‚   â”œâ”€â”€ card.tsx             # Card, CardHeader, CardContent, CardFooter, CardTitle
â”‚   â”œâ”€â”€ command.tsx          # Command palette (recherche)
â”‚   â”œâ”€â”€ dialog.tsx           # Dialog modal (Dialog, DialogTrigger, DialogContent)
â”‚   â”œâ”€â”€ dropdown-menu.tsx    # Menu dÃ©roulant contextuel
â”‚   â”œâ”€â”€ input-group.tsx      # Groupe d'inputs avec icÃ´ne
â”‚   â”œâ”€â”€ input.tsx            # Champ texte
â”‚   â”œâ”€â”€ label.tsx            # Label formulaire
â”‚   â”œâ”€â”€ scroll-area.tsx      # Zone scrollable
â”‚   â”œâ”€â”€ select.tsx           # Select dropdown
â”‚   â”œâ”€â”€ separator.tsx        # SÃ©parateur horizontal
â”‚   â”œâ”€â”€ sheet.tsx            # Panneau latÃ©ral (Sheet/Drawer)
â”‚   â”œâ”€â”€ sidebar.tsx          # Sidebar navigation complÃ¨te
â”‚   â”œâ”€â”€ skeleton.tsx         # Skeleton loader
â”‚   â”œâ”€â”€ sonner.tsx           # Toasts (notifications via Sonner)
â”‚   â”œâ”€â”€ table.tsx            # Table, TableHeader, TableBody, TableRow, TableCell
â”‚   â”œâ”€â”€ tabs.tsx             # Onglets (Tabs, TabsList, TabsTrigger, TabsContent)
â”‚   â”œâ”€â”€ textarea.tsx         # Zone de texte multilignes
â”‚   â””â”€â”€ tooltip.tsx          # Tooltip au survol
â”œâ”€â”€ composants/disposition/  # Composants layout app (5 fichiers)
â”‚   â”œâ”€â”€ coquille-app.tsx     # Shell principal (sidebar + content)
â”‚   â”œâ”€â”€ barre-laterale.tsx   # Sidebar avec navigation modules
â”‚   â”œâ”€â”€ en-tete.tsx          # Header avec breadcrumbs + actions
â”‚   â”œâ”€â”€ fil-ariane.tsx       # Breadcrumbs
â”‚   â””â”€â”€ nav-mobile.tsx       # Bottom navigation bar mobile
â”œâ”€â”€ fournisseurs/            # Providers React
â”‚   â”œâ”€â”€ fournisseur-query.tsx   # TanStack Query provider
â”‚   â”œâ”€â”€ fournisseur-auth.tsx    # Protection routes authentifiÃ©es
â”‚   â””â”€â”€ fournisseur-theme.tsx   # ThÃ¨me clair/sombre (next-themes)
â”œâ”€â”€ crochets/                # Hooks React personnalisÃ©s
â”‚   â”œâ”€â”€ utiliser-api.ts      # utiliserRequete, utiliserMutation, utiliserInvalidation
â”‚   â”œâ”€â”€ utiliser-auth.ts     # utiliserAuth (user, login, logout)
â”‚   â”œâ”€â”€ utiliser-delai.ts    # Debounce de valeurs
â”‚   â””â”€â”€ use-mobile.ts        # DÃ©tection mobile
â””â”€â”€ magasins/                # Zustand stores
    â”œâ”€â”€ store-auth.ts        # Ã‰tat auth (utilisateur, estConnecte)
    â”œâ”€â”€ store-ui.ts          # Ã‰tat UI (sidebar, recherche)
    â””â”€â”€ store-notifications.ts # File de notifications
```

---

## Composants shadcn/ui

Tous les composants UI de base proviennent de [shadcn/ui](https://ui.shadcn.com/) et sont dans `frontend/src/composants/ui/`. Ils utilisent Tailwind CSS v4 avec les tokens CSS du thÃ¨me.

### Button

```tsx
import { Button } from "@/components/ui/button"

<Button>DÃ©faut</Button>
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
| ----------- | ------- |
| `Badge` | Tags statut (couleur via `variant`) |
| `Input` | Champ texte avec `placeholder` |
| `Textarea` | Zone texte multiligne |
| `Select` | Dropdown sÃ©lection |
| `Label` | Label pour formulaire |
| `Separator` | Ligne sÃ©paratrice |
| `Avatar` | Photo/initiales utilisateur |
| `Tooltip` | Info-bulle au survol |
| `Sheet` | Panneau latÃ©ral (mobile) |
| `ScrollArea` | Zone scrollable personnalisÃ©e |
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

Navigation principale : modules Cuisine, Famille, Maison, Jeux, Outils, ParamÃ¨tres. Repliable sur desktop, sheet sur mobile.

### EnTete (en-tete.tsx)

Header avec fil d'ariane et actions (recherche, notifications).

### NavMobile (nav-mobile.tsx)

Bottom bar mobile avec 5 icÃ´nes de navigation rapide.

---

## Hooks personnalisÃ©s

### utiliserRequete / utiliserMutation / utiliserInvalidation

```tsx
import { utiliserRequete, utiliserMutation, utiliserInvalidation } from "@/crochets/utiliser-api"

// RequÃªte
const { data, isLoading, error } = utiliserRequete(["recettes"], listerRecettes)

// Mutation
const mutation = utiliserMutation(creerRecette, {
  onSuccess: () => invalider(["recettes"])
})

// Invalidation
const invalider = utiliserInvalidation()
invalider(["recettes"])  // RafraÃ®chit les requÃªtes recettes
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
            <CardContent>{/* DÃ©tails */}</CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={dialogOuvert} onOpenChange={setDialogOuvert}>
        <DialogContent>
          <DialogHeader><DialogTitle>Nouvel item</DialogTitle></DialogHeader>
          {/* Formulaire */}
          <DialogFooter>
            <Button onClick={() => mutationCreer.mutate(formData)}>
              CrÃ©er
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
```

---

## IcÃ´nes

L'application utilise [lucide-react](https://lucide.dev/) pour les icÃ´nes :

```tsx
import { Plus, Pencil, Trash2, Search, Star, Calendar, Home } from "lucide-react"

<Plus className="h-4 w-4" />
<Button><Pencil className="mr-2 h-4 w-4" /> Modifier</Button>
```

---

## IntÃ©grations (integrations/)

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

# VÃ©rifier la configuration
if verifier_config_google():
    afficher_statut_sync_google()
    afficher_bouton_sync_rapide()
else:
    afficher_config_google_calendar()
```

---

## Vues Extraites (views/)

Fonctions d'affichage extraites des services pour respecter la sÃ©paration UI/logique.

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

# Page paramÃ¨tres profil
afficher_parametres_profil()

# DÃ©corateurs de protection (backend FastAPI)
@router.get("/protege")
async def page_protegee(user: dict = Depends(require_auth)):
    return {"message": "Contenu protÃ©gÃ©"}

@router.get("/admin")
async def page_admin(user: dict = Depends(require_role("admin"))):
    return {"message": "Admin uniquement"}
```

### Historique (historique.py)

```python
from src.ui.views import afficher_timeline_activite, afficher_activite_utilisateur, afficher_statistiques_activite

# Timeline d'activitÃ© rÃ©cente (10 derniÃ¨res par dÃ©faut)
afficher_timeline_activite(limit=10)

# ActivitÃ© d'un utilisateur spÃ©cifique
afficher_activite_utilisateur(user_id="...")

# Statistiques d'activitÃ© globales
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

# ParamÃ¨tres de notifications
afficher_preferences_notification()
```

### MÃ©tÃ©o Jardin (meteo.py)

```python
from src.ui.views import afficher_meteo_jardin

# Alertes mÃ©tÃ©o pour le jardin
afficher_meteo_jardin()
```

### Sauvegarde (sauvegarde.py)

```python
from src.ui.views import afficher_sauvegarde

# Interface backup/restauration complÃ¨te
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

# Utilisateurs connectÃ©s en temps rÃ©el
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

# Liste paginÃ©e
afficher_liste_notifications_jeux(service=None, limite=10, type_jeu=None)
```

### PWA (pwa.py)

```python
from src.ui.views import injecter_meta_pwa

# AppelÃ© dans app.py aprÃ¨s injecter_css()
injecter_meta_pwa()
```

---

## Bonnes Pratiques

### Import RecommandÃ©

```python
# âœ… Import depuis le point d'entrÃ©e unifiÃ©
from src.ui import badge, carte_metrique_avancee, afficher_succes, etat_vide

# âœ… Import spÃ©cifique par sous-package
from src.ui.tablet import ModeTablette, obtenir_mode_tablette
from src.ui.views import afficher_timeline_activite
from src.ui.integrations import verifier_config_google

# âœ… Import dans _common.py des modules mÃ©tier
from src.ui.components.atoms import etat_vide  # re-exportÃ© via _common.py

# âŒ Ã‰viter les imports profonds dans le code mÃ©tier
from src.ui.components.atoms import badge  # PrÃ©fÃ©rer from src.ui import badge
```

### Motif Ã©tat vide

Utiliser le composant `EtatVide` (frontend) pour les Ã©tats vides :

```tsx
// Composant React unifiÃ©
<EtatVide
  titre="Aucune recette trouvÃ©e"
  icone="ðŸ½ï¸"
  description="Ajoutez votre premiÃ¨re recette"
/>
```

### Cache

Les calculs coÃ»teux utilisent `@avec_cache` (dÃ©corateur multi-niveaux) :

- Graphiques: `ttl=300` (5 min)
- MÃ©triques: `ttl=60` (1 min)

### Performance

Pour le chargement diffÃ©rÃ© des modules, les services utilisent `@service_factory` (singleton via registre).
Chaque domaine expose ses routes dans `src/api/routes/` et ses pages dans `frontend/src/app/(app)/`.

### Nommage

- Fonctions d'affichage : `afficher_*()`
- Fonctions d'obtention : `obtenir_*()`
- Fonctions de dÃ©finition : `definir_*()`
- Classes : `NomEnFrancais` (PascalCase)
- Constantes : `NOM_EN_MAJUSCULES`

---

## Imports Rapides

```python
# Point d'entrÃ©e unifiÃ© (~90 exports)
from src.ui import badge, carte_metrique_avancee, afficher_succes

# Sous-packages spÃ©cifiques
from src.ui.components import graphique_repartition_repas
from src.ui.feedback import spinner_intelligent, SuiviProgression
from src.ui.tablet import ModeTablette, bouton_tablette
from src.ui.views import afficher_sauvegarde, afficher_timeline_activite
from src.ui.integrations import verifier_config_google

# Layout (rÃ©servÃ© Ã  app.py)
from src.ui.layout import afficher_header, afficher_sidebar, injecter_css
```
