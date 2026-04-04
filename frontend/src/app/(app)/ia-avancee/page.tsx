'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Button } from '@/composants/ui/button'
import { AlertTriangle, Sparkles, TrendingUp, Zap } from 'lucide-react'
import {
  obtenirPrevisionDepenses,
  obtenirPredictionPannes,
  obtenirRecommandationsEnergie,
  obtenirSuggestionsProactives,
} from '@/bibliotheque/api/ia-avancee'
import { ItemAnime, SectionReveal } from '@/composants/ui/motion-utils'

const OUTILS = [
  { titre: 'Suggestions achats', description: 'Historique de consommation et réapprovisionnement.', chemin: '/ia-avancee/suggestions-achats', icone: '🛒' },
  { titre: 'Préférences apprises', description: 'Voir ce que l’IA retient des goûts et habitudes.', chemin: '/outils/preferences-apprises', icone: '🧠' },
  { titre: 'Planning adaptatif', description: 'Repas et activités adaptés à la météo et au budget.', chemin: '/ia-avancee/planning-adaptatif', icone: '📅' },
  { titre: 'Diagnostic plante', description: 'Analyse photo et recommandations de soin.', chemin: '/ia-avancee/diagnostic-plante', icone: '🌱' },
  { titre: 'Prévision dépenses', description: 'Projection des dépenses de fin de mois.', chemin: '/ia-avancee/prevision-depenses', icone: '💶' },
  { titre: 'Idées cadeaux', description: 'Suggestions personnalisées selon le profil.', chemin: '/ia-avancee/idees-cadeaux', icone: '🎁' },
  { titre: 'Analyse photo', description: 'Détection automatique du contexte et actions.', chemin: '/ia-avancee/analyse-photo', icone: '📸' },
  { titre: 'Optimisation routines', description: 'Gains de temps pour les routines du foyer.', chemin: '/ia-avancee/optimisation-routines', icone: '⚙️' },
  { titre: 'Analyse document', description: 'Analyse et classement des documents photo.', chemin: '/ia-avancee/analyse-document', icone: '📄' },
  { titre: 'Estimation travaux', description: 'Budget et difficulté à partir d’une photo.', chemin: '/ia-avancee/estimation-travaux', icone: '🔨' },
  { titre: 'Planning voyage', description: 'Itinéraire, checklist et adaptation enfant.', chemin: '/ia-avancee/planning-voyage', icone: '✈️' },
  { titre: 'Recommandations énergie', description: 'Plan d’économie d’énergie ciblé.', chemin: '/ia-avancee/recommandations-energie', icone: '⚡' },
  { titre: 'Prédiction pannes', description: 'Risque de panne et maintenance préventive.', chemin: '/ia-avancee/prediction-pannes', icone: '🔧' },
  { titre: 'Suggestions proactives', description: 'Actions suggérées automatiquement par l’app.', chemin: '/ia-avancee/suggestions-proactives', icone: '✨' },
  { titre: 'Adaptations météo', description: 'Transforme les prévisions en arbitrages concrets.', chemin: '/ia-avancee/adaptations-meteo', icone: '🌤️' },
  { titre: 'Comparateur recettes', description: 'Comparer 2 recettes sur calories et macros.', chemin: '/ia-avancee/comparateur-recettes', icone: '🥗' },
]

export default function IAAvanceePage() {
  const { data: depenses } = useQuery({ queryKey: ['ia-avancee', 'prevision-depenses'], queryFn: () => obtenirPrevisionDepenses(), staleTime: 1000 * 60 * 60 })
  const { data: energie } = useQuery({ queryKey: ['ia-avancee', 'energie'], queryFn: () => obtenirRecommandationsEnergie(), staleTime: 1000 * 60 * 60 })
  const { data: pannes } = useQuery({ queryKey: ['ia-avancee', 'pannes'], queryFn: () => obtenirPredictionPannes(), staleTime: 1000 * 60 * 60 })
  const { data: suggestions } = useQuery({ queryKey: ['ia-avancee', 'proactives'], queryFn: () => obtenirSuggestionsProactives(), staleTime: 1000 * 60 * 10 })

  return (
    <div className="space-y-6 pb-8">
      <SectionReveal>
        <div className="space-y-3 rounded-lg border border-amber-200 bg-gradient-to-r from-orange-50 via-amber-50 to-yellow-50 p-6">
          <div className="flex items-center gap-3">
            <Sparkles className="h-8 w-8 text-amber-600" />
            <div>
              <h1 className="text-3xl font-bold">IA Avancée</h1>
              <p className="text-muted-foreground">Un hub de 14 outils IA contextuels réellement actionnables.</p>
            </div>
          </div>
        </div>
      </SectionReveal>

      {suggestions && suggestions.suggestions.length > 0 && (
        <SectionReveal delay={0.04}>
          <Card className="border-amber-200 bg-amber-50/70">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-900"><AlertTriangle className="h-5 w-5" /> Suggestions proactives</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {suggestions.suggestions.slice(0, 3).map((item, index) => (
                <li key={`${item.titre}-${index}`} className="text-sm text-amber-950">• {item.titre} — {item.message}</li>
              ))}
            </ul>
          </CardContent>
          </Card>
        </SectionReveal>
      )}

      <SectionReveal delay={0.08} className="grid gap-4 md:grid-cols-3">
        <ItemAnime>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <TrendingUp className="h-4 w-4" /> Dépenses prévues
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{depenses ? `${depenses.prevision_fin_mois.toFixed(0)} €` : '—'}</div>
              <p className="text-xs text-muted-foreground">Projection de fin de mois</p>
            </CardContent>
          </Card>
        </ItemAnime>
        <ItemAnime index={1}>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <Zap className="h-4 w-4" /> Recos énergie
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{energie?.recommandations.length ?? 0}</div>
              <p className="text-xs text-muted-foreground">Actions priorisées</p>
            </CardContent>
          </Card>
        </ItemAnime>
        <ItemAnime index={2}>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <AlertTriangle className="h-4 w-4" /> Risques pannes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{pannes?.predictions.length ?? 0}</div>
              <p className="text-xs text-muted-foreground">Equipements surveillés</p>
            </CardContent>
          </Card>
        </ItemAnime>
      </SectionReveal>

      <SectionReveal delay={0.12} className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {OUTILS.map((outil, index) => (
          <ItemAnime key={outil.chemin} index={index}>
            <Card className="transition-all hover:-translate-y-0.5 hover:shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg"><span className="text-2xl">{outil.icone}</span>{outil.titre}</CardTitle>
                <CardDescription>{outil.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full">
                  <Link href={outil.chemin}>Ouvrir l’outil</Link>
                </Button>
              </CardContent>
            </Card>
          </ItemAnime>
        ))}
      </SectionReveal>
    </div>
  )
}
