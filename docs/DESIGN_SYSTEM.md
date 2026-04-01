# Design System â€” Assistant Matanne

> **Stack** : Tailwind CSS v4, shadcn/ui, Radix UI, class-variance-authority (CVA)  
> **Theme** : CSS custom properties (variables CSS), support dark/light/system  
> **Composants UI** : `frontend/src/composants/ui/` (29 composants)

---

## Principes visuels

| Principe | Application |
| ---------- | ------------- |
| **Mobile-first** | Grille responsive, bottom navigation sur mobile |
| **Dark mode natif** | Variables CSS `--background`, `--foreground`, etc. |
| **CohÃ©rence typographique** | Seule police systÃ¨me + `text-sm`, `text-base`, `text-2xl` |
| **AccessibilitÃ©** | Radix UI (focus-visible, ARIA, keyboard navigation) |
| **Feedback immÃ©diat** | Toasts (Sonner), skeletons, spinners Loader2 |

---

## Tokens de design (CSS Custom Properties)

### Couleurs

```css
/* Variables Tailwind CSS v4 â€” dÃ©finies dans globals.css ou via @layer base */
--background        /* Fond principal */
--foreground        /* Texte principal */
--card              /* Fond des cartes */
--card-foreground   /* Texte dans les cartes */
--primary           /* Couleur principale (actions) */
--primary-foreground
--secondary         /* Couleur secondaire */
--secondary-foreground
--muted             /* Fond attÃ©nuÃ© (zones secondaires) */
--muted-foreground  /* Texte secondaire/discret */
--accent            /* Accent hover */
--destructive       /* Actions dangereuses */
--border            /* Bordures */
--input             /* Fond inputs */
--ring              /* Focus ring */
```

### Espacement

Tailwind v4 â€” utiliser les classes utilitaires standard :

| Usage | Classe |
| ------- | -------- |
| Espacement entre sections | `space-y-6` |
| Padding interne carte | `p-4` ou via `CardContent` |
| Gap grille | `gap-4` |
| Margin micro | `mb-2`, `mt-1` |

### Typographie

| Ã‰lÃ©ment | Classe | Usage |
| --------- | -------- | ------- |
| Titre de page | `text-2xl font-bold tracking-tight` | `<h1>` |
| Titre de carte | Via `CardTitle` | Auto |
| Sous-titre | `text-sm text-muted-foreground` | Descriptions |
| Label formulaire | Via `Label` | Champs |
| Extra-small | `text-xs text-muted-foreground` | MÃ©tadonnÃ©es |
| Code | `font-mono text-sm` | Exemples techniques |

---

## Composants UI disponibles

### Layout & Navigation

| Composant | Fichier | Usage |
| ----------- | --------- | ------- |
| `Sidebar` | `sidebar.tsx` | Navigation latÃ©rale (desktop) |
| `Sheet` | `sheet.tsx` | Drawer mobile / panels latÃ©raux |
| `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent` | `tabs.tsx` | Navigation par onglets |
| `Separator` | `separator.tsx` | Lignes de sÃ©paration |
| `ScrollArea` | `scroll-area.tsx` | Zone scrollable avec barre stylisÃ©e |
| `Collapsible` | `collapsible.tsx` | Sections dÃ©pliables |

### Contenu & Display

| Composant | Fichier | Usage |
| ----------- | --------- | ------- |
| `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent` | `card.tsx` | Conteneur principal de donnÃ©es |
| `Badge` | `badge.tsx` | Ã‰tiquettes & statuts |
| `Alert` | `alert.tsx` | Messages d'alerte contextuels |
| `Avatar` | `avatar.tsx` | Photos de profil |
| `Progress` | `progress.tsx` | Barres de progression |
| `Skeleton` | `skeleton.tsx` | Loading states |
| `Tooltip` | `tooltip.tsx` | Info-bulles au survol |
| `Table` | `table.tsx` | Tableaux de donnÃ©es |

### Formulaires & Actions

| Composant | Fichier | Usage |
| ----------- | --------- | ------- |
| `Button` | `button.tsx` | Actions (default, outline, ghost, destructive, secondary) |
| `Input` | `input.tsx` | Saisie texte |
| `InputGroup` | `input-group.tsx` | Input avec prÃ©fixe/suffixe |
| `Textarea` | `textarea.tsx` | Saisie multiligne |
| `Label` | `label.tsx` | LibellÃ©s accessibles |
| `Checkbox` | `checkbox.tsx` | Cases Ã  cocher |
| `Switch` | `switch.tsx` | Interrupteurs on/off |
| `Slider` | `slider.tsx` | Curseurs numÃ©riques |
| `Select` | `select.tsx` | Listes dÃ©roulantes (Radix) |
| `Command` | `command.tsx` | Recherche + sÃ©lection (palette de commandes) |

### Overlay

| Composant | Fichier | Usage |
| ----------- | --------- | ------- |
| `Dialog` | `dialog.tsx` | Modales de confirmation / formulaires |
| `Popover` | `popover.tsx` | Info-bulles avec contenu riche |
| `DropdownMenu` | `dropdown-menu.tsx` | Menus contextuels |
| `Sonner` | `sonner.tsx` | Toast notifications (via `toast()`) |

### Custom

| Composant | Fichier | Usage |
| ----------- | --------- | ------- |
| `BoutonVocal` | `bouton-vocal.tsx` | Saisie vocale (Web Speech API) |

---

## Variantes du Button

```tsx
// default â€” action principale
<Button>Enregistrer</Button>

// outline â€” action secondaire
<Button variant="outline">Annuler</Button>

// ghost â€” action tertiaire / navigation
<Button variant="ghost">Voir plus</Button>

// destructive â€” suppression, danger
<Button variant="destructive">Supprimer</Button>

// secondary â€” action alternative
<Button variant="secondary">Dupliquer</Button>

// Tailles
<Button size="sm">Petit</Button>
<Button size="default">Normal</Button>
<Button size="lg">Grand</Button>
<Button size="icon"><Plus /></Button>

// Avec icÃ´ne
<Button>
  <Save className="mr-2 h-4 w-4" />
  Enregistrer
</Button>

// Loading state
<Button disabled={isPending}>
  {isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
  {isPending ? "Chargement..." : "Enregistrer"}
</Button>
```

---

## Pattern â€” Carte de module

```tsx
<Card>
  <CardHeader>
    <CardTitle>Titre du module</CardTitle>
    <CardDescription>Description courte</CardDescription>
  </CardHeader>
  <CardContent className="space-y-4">
    {/* contenu */}
  </CardContent>
</Card>
```

---

## Pattern â€” Page avec onglets

```tsx
<div className="space-y-6">
  <div>
    <h1 className="text-2xl font-bold tracking-tight">Titre</h1>
    <p className="text-muted-foreground">Description</p>
  </div>
  
  <Tabs defaultValue="tab1">
    <TabsList>
      <TabsTrigger value="tab1">Premier onglet</TabsTrigger>
      <TabsTrigger value="tab2">DeuxiÃ¨me onglet</TabsTrigger>
    </TabsList>
    <TabsContent value="tab1">
      {/* contenu */}
    </TabsContent>
  </Tabs>
</div>
```

---

## Pattern â€” Loading State

```tsx
// Skeleton pour liste
if (isLoading) {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <Skeleton key={i} className="h-16 w-full rounded-lg" />
      ))}
    </div>
  );
}

// Spinner inline
{isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
```

---

## Pattern â€” Toast

```tsx
import { toast } from "sonner";

// SuccÃ¨s
toast.success("Recette sauvegardÃ©e");

// Erreur
toast.error("Impossible de sauvegarder");

// Avec description
toast.success("Import terminÃ©", { description: "42 recettes importÃ©es" });

// Promise
toast.promise(saveRecette(), {
  loading: "Sauvegarde...",
  success: "SauvegardÃ© !",
  error: "Erreur lors de la sauvegarde",
});
```

---

## Iconographie

Utiliser [Lucide React](https://lucide.dev/) â€” dÃ©jÃ  installÃ©.

```tsx
import { Plus, Edit, Trash2, ChevronRight, Loader2 } from "lucide-react";

// Convention de taille
<Plus className="h-4 w-4" />          {/* inline, bouton */}
<Plus className="h-5 w-5" />          {/* heading, section */}
<Plus className="size-6" />           {/* grand, tableau de bord */}
```

---

## Ajouter un composant shadcn/ui

```bash
cd frontend
npx shadcn@latest add [nom-composant]
# Ex: npx shadcn@latest add accordion
```

Le composant est ajoutÃ© dans `src/composants/ui/[nom].tsx` avec les styles Tailwind.

---

## Voir aussi

- [FRONTEND_ARCHITECTURE.md](../FRONTEND_ARCHITECTURE.md) â€” Architecture frontend complÃ¨te
- [UI_COMPONENTS.md](../UI_COMPONENTS.md) â€” Guide composants spÃ©cifiques au projet
