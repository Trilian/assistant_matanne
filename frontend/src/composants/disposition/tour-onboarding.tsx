/**
 * Tour d'onboarding pour les nouveaux utilisateurs
 * 
 * Présente les fonctionnalités principales de l'application lors de la première connexion.
 */

'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/composants/ui/dialog'
import { Button } from '@/composants/ui/button'
import { Badge } from '@/composants/ui/badge'
import { Card, CardContent } from '@/composants/ui/card'
import { Progress } from '@/composants/ui/progress'
import {
  ChefHat,
  ShoppingCart,
  Calendar,
  Users,
  Home,
  Gamepad2,
  Wrench,
  ArrowRight,
  ArrowLeft,
  X,
  MessageCircle,
  Rocket,
  CheckCircle2,
} from 'lucide-react'

const STORAGE_KEY = 'matanne-onboarding-complete'

type EtatOnboardingStocke = {
  completed: boolean
  lastStep: number
  completedAt?: string | null
}

function lireEtatOnboarding(): EtatOnboardingStocke | null {
  if (typeof window === 'undefined') {
    return null
  }

  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) {
    return null
  }

  if (raw === 'true') {
    return { completed: true, lastStep: 0 }
  }

  try {
    const parsed = JSON.parse(raw) as Partial<EtatOnboardingStocke>
    return {
      completed: Boolean(parsed.completed),
      lastStep: Math.max(0, Number(parsed.lastStep ?? 0)),
      completedAt: parsed.completedAt ?? null,
    }
  } catch {
    return null
  }
}

function sauvegarderEtatOnboarding(etat: EtatOnboardingStocke) {
  if (typeof window === 'undefined') {
    return
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(etat))
}

/**
 * Étapes du tour d'onboarding
 */
const ETAPES_TOUR = [
  {
    titre: 'Bienvenue dans Assistant Matanne ! 🏠',
    description: 'Votre hub de gestion familiale tout-en-un',
    icone: Home,
    lien: undefined,
    ctaLabel: undefined,
    contenu: (
      <div className="space-y-3">
        <p className="text-sm">
          Assistant Matanne vous aide à gérer votre quotidien familial avec des outils
          pour la cuisine, les activités, la maison et bien plus.
        </p>
        <p className="text-sm font-medium">Découvrons les principales fonctionnalités :</p>
      </div>
    ),
  },
  {
    titre: 'Cuisine & Repas 🍽️',
    description: 'Recettes, planning des repas et courses',
    icone: ChefHat,
    lien: '/cuisine',
    ctaLabel: 'Ouvrir la cuisine',
    contenu: (
      <div className="space-y-2">
        <div className="flex items-start gap-3">
          <ChefHat className="size-5 text-orange-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Recettes</p>
            <p className="text-xs text-muted-foreground">
              Créez, importez et organisez vos recettes préférées. Import depuis URL ou PDF.
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Calendar className="size-5 text-blue-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Planning des repas</p>
            <p className="text-xs text-muted-foreground">
              Planifiez vos repas de la semaine avec suggestions IA personnalisées.
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <ShoppingCart className="size-5 text-green-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Liste de courses</p>
            <p className="text-xs text-muted-foreground">
              Générez automatiquement vos courses depuis votre planning.
            </p>
          </div>
        </div>
      </div>
    ),
  },
  {
    titre: 'Famille & Activités 👨‍👩‍👦',
    description: 'Suivi enfant, budget et activités',
    icone: Users,
    lien: '/famille',
    ctaLabel: 'Ouvrir la famille',
    contenu: (
      <div className="space-y-2">
        <div className="flex items-start gap-3">
          <Users className="size-5 text-purple-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Suivi de développement</p>
            <p className="text-xs text-muted-foreground">
              Jalons, activités et journal pour suivre l'évolution de Jules.
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Calendar className="size-5 text-pink-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Activités & Weekend</p>
            <p className="text-xs text-muted-foreground">
              Planifiez vos activités familiales et weekends avec suggestions IA.
            </p>
          </div>
        </div>
      </div>
    ),
  },
  {
    titre: 'Maison & Projets 🏡',
    description: 'Projets, entretien et énergie',
    icone: Home,
    lien: '/maison',
    ctaLabel: 'Ouvrir la maison',
    contenu: (
      <div className="space-y-2">
        <div className="flex items-start gap-3">
          <Wrench className="size-5 text-yellow-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Projets & Entretien</p>
            <p className="text-xs text-muted-foreground">
              Gérez vos projets de rénovation et l'entretien régulier de votre maison.
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Home className="size-5 text-teal-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Jardin & Stocks</p>
            <p className="text-xs text-muted-foreground">
              Suivez votre potager et gérez vos stocks de produits ménagers.
            </p>
          </div>
        </div>
      </div>
    ),
  },
  {
    titre: 'Jeux & Outils 🎮',
    description: 'Paris sportifs, loto et utilitaires',
    icone: Gamepad2,
    lien: '/jeux',
    ctaLabel: 'Ouvrir les jeux',
    contenu: (
      <div className="space-y-2">
        <div className="flex items-start gap-3">
          <Gamepad2 className="size-5 text-red-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Jeux</p>
            <p className="text-xs text-muted-foreground">
              Gérez vos paris sportifs et tirages Loto/EuroMillions.
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Wrench className="size-5 text-gray-500 mt-0.5" />
          <div>
            <p className="text-sm font-medium">Outils</p>
            <p className="text-xs text-muted-foreground">
              Chat IA, convertisseur, météo, notes et minuteur.
            </p>
          </div>
        </div>
      </div>
    ),
  },
  {
    titre: 'Démarrage recommandé 🚀',
    description: 'Les 3 actions qui donnent le plus de valeur dès le départ',
    icone: Rocket,
    lien: '/parametres/preferences-notifications',
    ctaLabel: 'Configurer maintenant',
    contenu: (
      <div className="space-y-3">
        {[
          'Configurer Telegram pour recevoir les résumés utiles et les actions rapides.',
          'Créer ou importer 2 à 3 recettes, puis générer un premier planning.',
          'Ajouter vos abonnements/contrats maison pour comparer les coûts annuels.',
        ].map((item) => (
          <div key={item} className="flex items-start gap-3 rounded-lg bg-muted/60 p-3">
            <CheckCircle2 className="mt-0.5 size-4 text-emerald-600" />
            <p className="text-sm">{item}</p>
          </div>
        ))}
        <div className="flex items-start gap-3 rounded-lg border border-dashed p-3">
          <MessageCircle className="mt-0.5 size-4 text-sky-600" />
          <p className="text-xs text-muted-foreground">
            Astuce : activez d&apos;abord Telegram si vous voulez des rappels simples et gratuits depuis l&apos;app.
          </p>
        </div>
      </div>
    ),
  },
  {
    titre: 'Astuces & Raccourcis ⌨️',
    description: 'Gagnez du temps avec ces raccourcis',
    icone: ArrowRight,
    lien: undefined,
    ctaLabel: undefined,
    contenu: (
      <div className="space-y-3">
        <div className="rounded-lg bg-muted p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm">Recherche globale</span>
            <kbd className="px-2 py-1 text-xs font-mono bg-background border rounded">
              Ctrl+K
            </kbd>
          </div>
          <p className="text-xs text-muted-foreground">
            Recherchez n'importe quoi dans l'application (recettes, projets, notes, etc.)
          </p>
        </div>
        <div className="rounded-lg bg-muted p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm">Guide utilisateur</span>
            <span className="text-xs text-muted-foreground">Icône 📖 dans le header</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Documentation complète avec FAQ et guides détaillés
          </p>
        </div>
        <div className="rounded-lg bg-muted p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm">Thème clair/sombre</span>
            <span className="text-xs text-muted-foreground">Bouton ☀️/🌙 dans le header</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Personnalisez l'apparence depuis le header ou les paramètres
          </p>
        </div>
      </div>
    ),
  },
] as const

interface TourOnboardingProps {
  /**
   * Forcer l'affichage du tour (pour le bouton "Rejouer" dans les paramètres)
   */
  forcer?: boolean
  /**
   * Callback appelé quand le tour est terminé ou fermé
   */
  onTerminer?: () => void
}

export function TourOnboarding({ forcer = false, onTerminer }: TourOnboardingProps) {
  const router = useRouter()
  const [ouvert, setOuvert] = React.useState(false)
  const [etapeActuelle, setEtapeActuelle] = React.useState(0)

  const etape = ETAPES_TOUR[etapeActuelle]
  const estDerniereEtape = etapeActuelle === ETAPES_TOUR.length - 1
  const Icone = etape.icone
  const progression = ((etapeActuelle + 1) / ETAPES_TOUR.length) * 100

  /**
   * Initialise le tour au premier chargement
   */
  React.useEffect(() => {
    const etat = lireEtatOnboarding()

    if (forcer) {
      setEtapeActuelle(Math.min(etat?.lastStep ?? 0, ETAPES_TOUR.length - 1))
      setOuvert(true)
      return
    }

    if (!etat?.completed) {
      setEtapeActuelle(Math.min(etat?.lastStep ?? 0, ETAPES_TOUR.length - 1))
      setOuvert(true)
    }
  }, [forcer])

  React.useEffect(() => {
    if (!ouvert) {
      return
    }

    sauvegarderEtatOnboarding({
      completed: false,
      lastStep: etapeActuelle,
      completedAt: null,
    })
  }, [etapeActuelle, ouvert])

  /**
   * Passe à l'étape suivante
   */
  const etapeSuivante = () => {
    if (estDerniereEtape) {
      terminer()
    } else {
      setEtapeActuelle((prev) => Math.min(prev + 1, ETAPES_TOUR.length - 1))
    }
  }

  /**
   * Retour à l'étape précédente
   */
  const etapePrecedente = () => {
    setEtapeActuelle((prev) => Math.max(prev - 1, 0))
  }

  /**
   * Termine le tour
   */
  const terminer = () => {
    sauvegarderEtatOnboarding({
      completed: true,
      lastStep: 0,
      completedAt: new Date().toISOString(),
    })
    setOuvert(false)
    setEtapeActuelle(0)
    onTerminer?.()
  }

  /**
   * Ferme et marque comme complété
   */
  const fermer = () => {
    terminer()
  }

  /**
   * Visite un module
   */
  const visiterModule = () => {
    if (etape.lien) {
      terminer()
      router.push(etape.lien)
    } else {
      etapeSuivante()
    }
  }

  return (
    <Dialog open={ouvert} onOpenChange={(open) => !open && fermer()}>
      <DialogContent className="max-w-xl w-full overflow-y-auto max-h-[90vh]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-2">
              <Icone className="size-6 text-primary" />
            </div>
            <div>
              <DialogTitle className="text-xl">{etape.titre}</DialogTitle>
              <DialogDescription>{etape.description}</DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Étape {etapeActuelle + 1} / {ETAPES_TOUR.length}</span>
              <span>{Math.round(progression)}% du tour parcouru</span>
            </div>
            <Progress value={progression} className="h-2" />
            <div className="flex flex-wrap gap-1.5">
              {ETAPES_TOUR.map((item, index) => (
                <button
                  key={item.titre}
                  type="button"
                  onClick={() => setEtapeActuelle(index)}
                  title={item.description}
                  className={`rounded-full border w-7 h-7 text-xs font-medium transition-colors ${
                    index === etapeActuelle
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border text-muted-foreground hover:bg-muted'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>
          </div>

          <Card className="border-none bg-muted/20 shadow-none">
            <CardContent className="space-y-4 pt-4">
              {etape.lien ? (
                <div className="flex items-center gap-2 rounded-lg border border-dashed bg-background/80 px-3 py-2 text-xs text-muted-foreground">
                  <Badge variant="secondary">Action rapide</Badge>
                  <span>Ouvrez ce module pour tester immédiatement cette partie de l&apos;app.</span>
                </div>
              ) : null}
              {etape.contenu}
            </CardContent>
          </Card>
        </div>

        <DialogFooter className="flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-muted-foreground">
            Le tour peut être rejoué depuis les paramètres d&apos;affichage ou la recherche globale.
          </p>

          <div className="flex gap-2 justify-end">
            <Button variant="ghost" size="sm" onClick={fermer}>
              <X className="size-4 mr-1" />
              Plus tard
            </Button>
            {etapeActuelle > 0 && (
              <Button variant="outline" size="sm" onClick={etapePrecedente}>
                <ArrowLeft className="size-4 mr-1" />
                Précédent
              </Button>
            )}
            {etape.lien ? (
              <Button size="sm" onClick={visiterModule}>
                {etape.ctaLabel ?? 'Ouvrir le module'}
                <ArrowRight className="size-4 ml-1" />
              </Button>
            ) : (
              <Button size="sm" onClick={etapeSuivante}>
                {estDerniereEtape ? 'Terminer' : 'Suivant'}
                <ArrowRight className="size-4 ml-1" />
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

/**
 * Hook pour vérifier si l'onboarding a été complété
 */
export function useOnboardingComplete() {
  const [complete, setComplete] = React.useState(false)

  React.useEffect(() => {
    const etat = lireEtatOnboarding()
    setComplete(Boolean(etat?.completed))
  }, [])

  return complete
}

/**
 * Fonction pour réinitialiser l'onboarding (utile pour le bouton "Rejouer")
 */
export function resetOnboarding() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(STORAGE_KEY)
  }
}
