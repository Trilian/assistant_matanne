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
import { rechercheGlobale, type ResultatRecherche } from '@/bibliotheque/api/recherche'
import { toast } from 'sonner'
import {
  ChefHat,
  Hammer,
  Users,
  StickyNote,
  UserCircle,
  Loader2,
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
}

export function RechercheGlobale() {
  const router = useRouter()
  const { rechercheOuverte, definirRecherche } = utiliserStoreUI()
  
  const [query, setQuery] = React.useState('')
  const [resultats, setResultats] = React.useState<ResultatRecherche[]>([])
  const [enChargement, setEnChargement] = React.useState(false)

  // Debounce pour éviter les requêtes excessives
  const timeoutRef = React.useRef<NodeJS.Timeout | undefined>(undefined)

  /**
   * Effectue la recherche avec debouncing
   */
  const effectuerRecherche = React.useCallback(async (terme: string) => {
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
        const donnees = await rechercheGlobale(terme, 20)
        setResultats(donnees)
      } catch (error) {
        console.error('Erreur de recherche:', error)
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
    effectuerRecherche(value)
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

  return (
    <CommandDialog 
      open={rechercheOuverte} 
      onOpenChange={definirRecherche}
      title="Recherche globale"
      description="Recherchez des recettes, projets, activités, notes et contacts"
    >
      <Command shouldFilter={false}>
        <CommandInput
          placeholder="Rechercher... (min 2 caractères)"
          value={query}
          onValueChange={handleQueryChange}
        />
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
                    <div className="flex flex-col gap-0.5">
                      <span className="font-medium">{resultat.titre}</span>
                      {resultat.description && (
                        <span className="text-xs text-muted-foreground">
                          {resultat.description}
                        </span>
                      )}
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
