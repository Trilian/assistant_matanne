/**
 * Composant de recherche globale multi-entités
 * 
 * Recherche dans les recettes, projets, activités, notes et contacts.
 * Accessible via Ctrl+K / Cmd+K ou le bouton de recherche dans le header.
 */

'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import {
  CommandDialog,
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
} from '@/composants/ui/command'
import { utiliserStoreUI } from '@/magasins/store-ui'
import { rechercheGlobale, type ResultatRecherche, type TypeResultatRecherche } from '@/bibliotheque/api/recherche'
import { toast } from 'sonner'
import {
  ChefHat,
  Hammer,
  Users,
  StickyNote,
  UserCircle,
  Loader2,
  Sprout,
  FolderOpen,
  Receipt,
  Wrench,
  Home,
  Map,
  Dices,
  Ticket,
  RotateCw,
  CalendarDays,
  ShoppingCart,
  Sparkles,
  type LucideIcon,
} from 'lucide-react'

/**
 * Map des types d'entités vers leurs icônes Lucide
 */
const ICONES_PAR_TYPE: Record<string, LucideIcon> = {
  recette: ChefHat,
  projet: Hammer,
  activite: Users,
  note: StickyNote,
  contact: UserCircle,
  plante: Sprout,
  document: FolderOpen,
  abonnement: Receipt,
  entretien: Wrench,
  annonce: Home,
  scenario: Map,
  pari: Dices,
  loto: Ticket,
  routine: RotateCw,
}

/**
 * Map des types d'entités vers leurs labels français
 */
const LABELS_PAR_TYPE: Record<string, string> = {
  recette: 'Recettes',
  projet: 'Projets',
  activite: 'Activités',
  note: 'Notes',
  contact: 'Contacts',
  plante: 'Jardin',
  document: 'Documents',
  abonnement: 'Abonnements',
  entretien: 'Entretien',
  annonce: 'Annonces immo',
  scenario: 'Scénarios habitat',
  pari: 'Paris sportifs',
  loto: 'Loto',
  routine: 'Routines',
}

const FILTRES_RECHERCHE: Array<{
  id: string
  label: string
  types?: TypeResultatRecherche[]
}> = [
  { id: 'all', label: 'Tout' },
  { id: 'cuisine', label: 'Cuisine', types: ['recette'] },
  { id: 'famille', label: 'Famille', types: ['activite', 'contact', 'document', 'routine'] },
  { id: 'maison', label: 'Maison', types: ['projet', 'plante', 'abonnement', 'entretien'] },
  { id: 'habitat', label: 'Habitat', types: ['annonce', 'scenario'] },
  { id: 'jeux', label: 'Jeux', types: ['pari', 'loto'] },
  { id: 'outils', label: 'Outils', types: ['note'] },
]

const ACTIONS_RAPIDES = [
  { id: 'planifier', label: 'Planifier ma semaine', icone: CalendarDays, url: '/cuisine/ma-semaine' },
  { id: 'courses', label: 'Ajouter aux courses', icone: ShoppingCart, url: '/cuisine/courses' },
  { id: 'quoi-manger', label: 'Quoi manger ce soir ?', icone: Sparkles, url: '/outils/chat-ia' },
]

export function RechercheGlobale() {
  const router = useRouter()
  const { rechercheOuverte, definirRecherche } = utiliserStoreUI()
  
  const [query, setQuery] = React.useState('')
  const [resultats, setResultats] = React.useState<ResultatRecherche[]>([])
  const [enChargement, setEnChargement] = React.useState(false)
  const [filtreActif, setFiltreActif] = React.useState<string>('all')

  // Debounce pour éviter les requêtes excessives
  const timeoutRef = React.useRef<NodeJS.Timeout | undefined>(undefined)

  /**
   * Effectue la recherche avec debouncing
   */
  const effectuerRecherche = React.useCallback(async (terme: string, filtreId: string = 'all') => {
    // Clear previous timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    // Reset si le terme est trop court
    if (terme.length < 2) {
      setResultats([])
      return
    }

    // Debounce de 300ms
    timeoutRef.current = setTimeout(async () => {
      setEnChargement(true)
      try {
        const filtre = FILTRES_RECHERCHE.find((item) => item.id === filtreId)
        const donnees = await rechercheGlobale(terme, 20, filtre?.types)
        setResultats(donnees)
      } catch {
        toast.error('La recherche a échoué. Veuillez réessayer.')
        setResultats([])
      } finally {
        setEnChargement(false)
      }
    }, 300)
  }, [])

  /**
   * Gère le changement de query
   */
  const handleQueryChange = (value: string) => {
    setQuery(value)
    effectuerRecherche(value, filtreActif)
  }

  /**
   * Gère la sélection d'un résultat
   */
  const handleSelect = (resultat: ResultatRecherche) => {
    definirRecherche(false)
    router.push(resultat.url)
    // Reset après navigation
    setTimeout(() => {
      setQuery('')
      setResultats([])
    }, 100)
  }

  /**
   * Groupe les résultats par type
   */
  const resultatsGroupes = React.useMemo(() => {
    const groupes: Record<string, ResultatRecherche[]> = {}
    
    resultats.forEach((resultat) => {
      if (!groupes[resultat.type]) {
        groupes[resultat.type] = []
      }
      groupes[resultat.type].push(resultat)
    })
    
    return groupes
  }, [resultats])

  /**
   * Keyboard shortcut: Ctrl+K / Cmd+K
   */
  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        definirRecherche(!rechercheOuverte)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [rechercheOuverte, definirRecherche])

  /**
   * Cleanup timeout on unmount
   */
  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  const changerFiltre = (filtreId: string) => {
    setFiltreActif(filtreId)
    if (query.length >= 2) {
      effectuerRecherche(query, filtreId)
    }
  }

  return (
    <CommandDialog 
      open={rechercheOuverte} 
      onOpenChange={definirRecherche}
      title="Recherche globale"
      description="Recherchez à travers la cuisine, la famille, la maison, les documents et les notes"
    >
      <Command shouldFilter={false}>
        <CommandInput
          placeholder="Rechercher... (min 2 caractères)"
          value={query}
          onValueChange={handleQueryChange}
        />
        <div className="flex flex-wrap gap-2 border-b px-3 py-2">
          {FILTRES_RECHERCHE.map((filtre) => (
            <button
              key={filtre.id}
              type="button"
              onClick={() => changerFiltre(filtre.id)}
              className={`rounded-full border px-2.5 py-1 text-xs transition-colors ${
                filtreActif === filtre.id
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border text-muted-foreground hover:bg-muted'
              }`}
            >
              {filtre.label}
            </button>
          ))}
        </div>
        <CommandList>
          <CommandEmpty>
            {enChargement ? (
              <div className="flex items-center justify-center gap-2 py-6">
                <Loader2 className="size-4 animate-spin" />
                <span>Recherche en cours...</span>
              </div>
            ) : query.length < 2 ? (
              <span>Saisissez au moins 2 caractères pour rechercher</span>
            ) : (
              <span>Aucun résultat trouvé</span>
            )}
          </CommandEmpty>

          {query.length < 2 && (
            <CommandGroup heading="Actions rapides">
              {ACTIONS_RAPIDES.map((action) => (
                <CommandItem
                  key={action.id}
                  onSelect={() => {
                    definirRecherche(false)
                    router.push(action.url)
                  }}
                  className="cursor-pointer"
                >
                  <action.icone className="mr-2 size-4" />
                  <span>{action.label}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          )}

          {Object.entries(resultatsGroupes).map(([type, items]) => {
            const Icone = ICONES_PAR_TYPE[type] || StickyNote
            const label = LABELS_PAR_TYPE[type] || type

            return (
              <CommandGroup key={type} heading={label}>
                {items.map((resultat) => (
                  <CommandItem
                    key={`${resultat.type}-${resultat.id}`}
                    onSelect={() => handleSelect(resultat)}
                    className="cursor-pointer"
                  >
                    <Icone className="mr-2 size-4" />
                    <div className="flex min-w-0 flex-1 items-start justify-between gap-2">
                      <div className="flex min-w-0 flex-col gap-0.5">
                        <span className="font-medium truncate">{resultat.titre}</span>
                        {resultat.description && (
                          <span className="text-xs text-muted-foreground line-clamp-2">
                            {resultat.description}
                          </span>
                        )}
                      </div>
                      <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] text-muted-foreground">
                        {LABELS_PAR_TYPE[resultat.type] ?? resultat.type}
                      </span>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )
          })}
        </CommandList>
      </Command>
    </CommandDialog>
  )
}
