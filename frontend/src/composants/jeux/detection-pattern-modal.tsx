'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from '@/composants/ui/dialog'
import { Alert, AlertDescription, AlertTitle } from '@/composants/ui/alert'
import { Button } from '@/composants/ui/button'
import { Badge } from '@/composants/ui/badge'
import { Checkbox } from '@/composants/ui/checkbox'
import { Label } from '@/composants/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/composants/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import { Flame, Dice1, TrendingDown, AlertTriangle, Info, X, BookOpen } from 'lucide-react'

interface ResultatTest {
  alerte: boolean
  severite: 'faible' | 'moyenne' | 'forte'
  message: string
  details: Record<string, any>
  type_pattern: string
}

interface DetectionPatternModalProps {
  open: boolean
  onClose: () => void
  /** Résultats des tests statistiques */
  alerts: {
    regression_moyenne?: ResultatTest
    hot_hand?: ResultatTest
    gamblers_fallacy?: ResultatTest
  }
  /** User ID pour localStorage */
  userId?: number
}

const STORAGE_KEY_PREFIX = 'paris_alerts_disabled_'

export function DetectionPatternModal({
  open,
  onClose,
  alerts,
  userId
}: DetectionPatternModalProps) {
  const [nePlusAfficher, setNePlusAfficher] = useState(false)
  const [activeTab, setActiveTab] = useState<'all' | 'hot_hand' | 'gamblers' | 'regression'>('all')

  // Compter nombre d'alertes actives
  const nbAlertes = Object.values(alerts).filter(a => a?.alerte).length

  // Vérifier localStorage au chargement
  useEffect(() => {
    if (userId) {
      const disabled = localStorage.getItem(`${STORAGE_KEY_PREFIX}${userId}`)
      if (disabled === 'true') {
        setNePlusAfficher(true)
      }
    }
  }, [userId])

  // Sauvegarder préférence
  const handleSavePreference = () => {
    if (userId && nePlusAfficher) {
      localStorage.setItem(`${STORAGE_KEY_PREFIX}${userId}`, 'true')
    } else if (userId) {
      localStorage.removeItem(`${STORAGE_KEY_PREFIX}${userId}`)
    }
    onClose()
  }

  // Ne pas afficher si utilisateur a désactivé
  const shouldShow = userId
    ? localStorage.getItem(`${STORAGE_KEY_PREFIX}${userId}`) !== 'true'
    : true

  if (!shouldShow || nbAlertes === 0) {
    return null
  }

  // Helpers couleurs
  const couleurSeverite = (severite: string) => {
    switch (severite) {
      case 'forte':
        return 'destructive'
      case 'moyenne':
        return 'default'
      case 'faible':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  const couleurBordure = (severite: string) => {
    switch (severite) {
      case 'forte':
        return 'border-red-300 bg-red-50/50'
      case 'moyenne':
        return 'border-orange-300 bg-orange-50/50'
      case 'faible':
        return 'border-yellow-300 bg-yellow-50/50'
      default:
        return 'border-gray-300 bg-gray-50/50'
    }
  }

  // Icônes par type
  const getIcone = (type: string) => {
    switch (type) {
      case 'hot_hand':
        return <Flame className="h-5 w-5 text-orange-600" />
      case 'gamblers_fallacy':
        return <Dice1 className="h-5 w-5 text-purple-600" />
      case 'regression_moyenne':
        return <TrendingDown className="h-5 w-5 text-blue-600" />
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />
    }
  }

  // Titres éducatifs
  const getTitre = (type: string) => {
    switch (type) {
      case 'hot_hand':
        return '🔥 Illusion de la "main chaude"'
      case 'gamblers_fallacy':
        return '🎲 Erreur du parieur'
      case 'regression_moyenne':
        return '📉 Régression vers la moyenne'
      default:
        return '⚠️ Pattern détecté'
    }
  }

  // Explications pédagogiques
  const getExplication = (type: string) => {
    switch (type) {
      case 'hot_hand':
        return {
          titre: "Qu'est-ce que l'illusion de la main chaude ?",
          texte: `La "main chaude" est la croyance erronée qu'après une série de succès, on a plus de chances de continuer à gagner. En réalité, chaque pari est indépendant. Une série de victoires n'influence pas les résultats futurs.`,
          conseil: 'Ne pas augmenter vos mises après une série de gains. Suivez votre stratégie initiale.'
        }
      case 'gamblers_fallacy':
        return {
          titre: "Qu'est-ce que l'erreur du parieur ?",
          texte: `L'erreur du parieur consiste à croire qu'après une série de pertes, on "doit" bientôt gagner pour "se refaire". Chaque pari reste indépendant avec les mêmes probabilités, quelle que soit l'historique.`,
          conseil: 'Ne jamais augmenter ses mises après une perte pour "se refaire". C\'est le chemin vers des pertes importantes.'
        }
      case 'regression_moyenne':
        return {
          titre: "Qu'est-ce que la régression vers la moyenne ?",
          texte: `Après une période de résultats exceptionnels (très bons ou très mauvais), les résultats tendent naturellement à revenir vers la moyenne à long terme. Cela ne prédit pas le résultat immédiat du prochain pari.`,
          conseil: 'Ne vous attendez pas à ce que la prochaine série soit forcément différente. Gardez vos attentes réalistes.'
        }
      default:
        return {
          titre: 'Biais cognitif détecté',
          texte: 'Un pattern inhabituel a été détecté dans votre comportement de paris.',
          conseil: 'Prenez du recul et analysez objectivement votre stratégie.'
        }
    }
  }

  return (
    <Dialog open={open && shouldShow} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="flex items-center gap-2 text-xl">
                <AlertTriangle className="h-6 w-6 text-orange-600" />
                {nbAlertes} alerte{nbAlertes > 1 ? 's' : ''} statistique{nbAlertes > 1 ? 's' : ''}
              </DialogTitle>
              <DialogDescription className="mt-2">
                Notre analyse a détecté des patterns inhabituels dans votre historique de paris. 
                Ces alertes visent à vous protéger contre les biais cognitifs courants.
              </DialogDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8 flex-shrink-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="mt-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">
              Toutes ({nbAlertes})
            </TabsTrigger>
            {alerts.hot_hand?.alerte && (
              <TabsTrigger value="hot_hand" className="text-xs">
                🔥 Main chaude
              </TabsTrigger>
            )}
            {alerts.gamblers_fallacy?.alerte && (
              <TabsTrigger value="gamblers" className="text-xs">
                🎲 Erreur parieur
              </TabsTrigger>
            )}
            {alerts.regression_moyenne?.alerte && (
              <TabsTrigger value="regression" className="text-xs">
                📉 Régression
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="all" className="space-y-4 mt-4">
            {alerts.hot_hand?.alerte && (
              <AlertCard alert={alerts.hot_hand} type="hot_hand" />
            )}
            {alerts.gamblers_fallacy?.alerte && (
              <AlertCard alert={alerts.gamblers_fallacy} type="gamblers_fallacy" />
            )}
            {alerts.regression_moyenne?.alerte && (
              <AlertCard alert={alerts.regression_moyenne} type="regression_moyenne" />
            )}
          </TabsContent>

          {alerts.hot_hand?.alerte && (
            <TabsContent value="hot_hand">
              <AlertCardDetailed alert={alerts.hot_hand} type="hot_hand" />
            </TabsContent>
          )}

          {alerts.gamblers_fallacy?.alerte && (
            <TabsContent value="gamblers">
              <AlertCardDetailed alert={alerts.gamblers_fallacy} type="gamblers_fallacy" />
            </TabsContent>
          )}

          {alerts.regression_moyenne?.alerte && (
            <TabsContent value="regression">
              <AlertCardDetailed alert={alerts.regression_moyenne} type="regression_moyenne" />
            </TabsContent>
          )}
        </Tabs>

        {/* Ressources jeu responsable */}
        <Card className="mt-4 border-blue-200 bg-blue-50/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Besoin d'aide ?
            </CardTitle>
          </CardHeader>
          <CardContent className="text-xs text-gray-700 space-y-2">
            <p>
              <strong>Joueurs Info Service :</strong> 09 74 75 13 13 (appel non surtaxé)
            </p>
            <p>
              Si vous ressentez une perte de contrôle sur vos paris, n'hésitez pas à contacter 
              un professionnel ou à utiliser nos outils d'auto-exclusion.
            </p>
            <Button variant="link" size="sm" className="h-auto p-0 text-xs">
              → Activer l'auto-exclusion temporaire
            </Button>
          </CardContent>
        </Card>

        {/* Options */}
        <div className="flex items-center justify-between pt-4 border-t">
          <div className="flex items-center gap-2">
            <Checkbox
              id="ne-plus-afficher"
              checked={nePlusAfficher}
              onCheckedChange={(checked) => setNePlusAfficher(checked as boolean)}
            />
            <Label htmlFor="ne-plus-afficher" className="text-sm cursor-pointer">
              Ne plus afficher ces alertes
            </Label>
          </div>

          <Button onClick={handleSavePreference}>
            J'ai compris
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// Composant carte alerte résumée
function AlertCard({ alert, type }: { alert: ResultatTest; type: string }) {
  const getIcone = (type: string) => {
    switch (type) {
      case 'hot_hand':
        return <Flame className="h-5 w-5 text-orange-600" />
      case 'gamblers_fallacy':
        return <Dice1 className="h-5 w-5 text-purple-600" />
      case 'regression_moyenne':
        return <TrendingDown className="h-5 w-5 text-blue-600" />
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />
    }
  }

  const getTitre = (type: string) => {
    switch (type) {
      case 'hot_hand':
        return 'Illusion de la "main chaude"'
      case 'gamblers_fallacy':
        return 'Erreur du parieur'
      case 'regression_moyenne':
        return 'Régression vers la moyenne'
      default:
        return 'Pattern détecté'
    }
  }

  const couleurSeverite = (severite: string) => {
    switch (severite) {
      case 'forte':
        return 'destructive'
      case 'moyenne':
        return 'default'
      case 'faible':
        return 'secondary'
      default:
        return 'outline'
    }
  }

  return (
    <Alert>
      <div className="flex items-start gap-3">
        {getIcone(type)}
        <div className="flex-1">
          <AlertTitle className="flex items-center gap-2">
            {getTitre(type)}
            <Badge variant={couleurSeverite(alert.severite)}>
              {alert.severite}
            </Badge>
          </AlertTitle>
          <AlertDescription className="mt-2 text-sm">
            {alert.message}
          </AlertDescription>
        </div>
      </div>
    </Alert>
  )
}

// Composant carte alerte détaillée
function AlertCardDetailed({ alert, type }: { alert: ResultatTest; type: string }) {
  const explication = {
    hot_hand: {
      titre: "Qu'est-ce que l'illusion de la main chaude ?",
      texte: `La "main chaude" est la croyance erronée qu'après une série de succès, on a plus de chances de continuer à gagner. En réalité, chaque pari est indépendant. Une série de victoires n'influence pas les résultats futurs.`,
      conseil: 'Ne pas augmenter vos mises après une série de gains. Suivez votre stratégie initiale.'
    },
    gamblers_fallacy: {
      titre: "Qu'est-ce que l'erreur du parieur ?",
      texte: `L'erreur du parieur consiste à croire qu'après une série de pertes, on "doit" bientôt gagner pour "se refaire". Chaque pari reste indépendant avec les mêmes probabilités, quelle que soit l'historique.`,
      conseil: 'Ne jamais augmenter ses mises après une perte pour "se refaire". C\'est le chemin vers des pertes importantes.'
    },
    regression_moyenne: {
      titre: "Qu'est-ce que la régression vers la moyenne ?",
      texte: `Après une période de résultats exceptionnels (très bons ou très mauvais), les résultats tendent naturellement à revenir vers la moyenne à long terme. Cela ne prédit pas le résultat immédiat du prochain pari.`,
      conseil: 'Ne vous attendez pas à ce que la prochaine série soit forcément différente. Gardez vos attentes réalistes.'
    }
  }[type] || {
    titre: 'Biais cognitif détecté',
    texte: 'Un pattern inhabituel a été détecté.',
    conseil: 'Analysez votre stratégie.'
  }

  return (
    <div className="space-y-4">
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Alerte détectée</AlertTitle>
        <AlertDescription>{alert.message}</AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Info className="h-4 w-4" />
            {explication.titre}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-gray-700">{explication.texte}</p>
          
          <div className="rounded-lg bg-blue-50 border border-blue-200 p-3">
            <p className="text-sm font-semibold text-blue-900 mb-1">💡 Conseil</p>
            <p className="text-sm text-blue-800">{explication.conseil}</p>
          </div>

          {/* Détails statistiques */}
          {Object.keys(alert.details).length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold mb-2">Détails statistiques</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(alert.details).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 rounded p-2">
                    <div className="text-gray-500">{key.replace(/_/g, ' ')}</div>
                    <div className="font-semibold">
                      {typeof value === 'number' ? value.toFixed(2) : String(value)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
