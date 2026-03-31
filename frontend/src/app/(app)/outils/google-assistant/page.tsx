'use client'

import { useEffect, useMemo, useState } from 'react'
import { Bot, Play, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import { Badge } from '@/composants/ui/badge'
import { Button } from '@/composants/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/composants/ui/card'
import {
  executerIntentGoogleAssistant,
  listerIntentsGoogleAssistant,
  type AssistantIntent,
} from '@/bibliotheque/api/assistant'

export default function GoogleAssistantPage() {
  const [chargement, setChargement] = useState(false)
  const [execution, setExecution] = useState(false)
  const [intents, setIntents] = useState<AssistantIntent[]>([])
  const [intentActif, setIntentActif] = useState<string>('')
  const [slotsTexte, setSlotsTexte] = useState<string>('{}')
  const [reponse, setReponse] = useState<string>('')

  async function chargerIntents() {
    setChargement(true)
    try {
      const data = await listerIntentsGoogleAssistant()
      setIntents(data.intents)
      if (data.intents.length > 0 && !intentActif) {
        setIntentActif(data.intents[0].intent)
      }
    } catch {
      toast.error('Impossible de charger les intents Google Assistant')
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => {
    void chargerIntents()
  }, [])

  const slotsRequis = useMemo(
    () => intents.find((i) => i.intent === intentActif)?.slots ?? [],
    [intents, intentActif]
  )

  async function executer() {
    if (!intentActif) return

    let slots: Record<string, string> = {}
    try {
      const parsed = JSON.parse(slotsTexte)
      if (parsed && typeof parsed === 'object') {
        slots = parsed as Record<string, string>
      }
    } catch {
      toast.error('Le JSON des slots est invalide')
      return
    }

    setExecution(true)
    setReponse('')
    try {
      const data = await executerIntentGoogleAssistant({ intent: intentActif, slots })
      setReponse(`${data.resultat.action}: ${data.resultat.message}`)
      toast.success('Intent exécuté')
    } catch {
      toast.error('Échec exécution intent')
    } finally {
      setExecution(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Google Assistant</h1>
          <p className="text-muted-foreground">Tester les intents/actions et le mapping API.</p>
        </div>
        <Button variant="outline" onClick={chargerIntents} disabled={chargement}>
          <RefreshCw className="mr-2 h-4 w-4" />
          {chargement ? 'Chargement...' : 'Rafraîchir'}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5" />
            Exécution d'un intent
          </CardTitle>
          <CardDescription>Choisir un intent, renseigner les slots JSON puis exécuter.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Intent</label>
            <select
              title="Choisir un intent Google Assistant"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
              value={intentActif}
              onChange={(e) => setIntentActif(e.target.value)}
            >
              {intents.map((intent) => (
                <option key={intent.intent} value={intent.intent}>
                  {intent.intent}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-wrap gap-2">
            {slotsRequis.length === 0 ? (
              <Badge variant="secondary">Aucun slot requis</Badge>
            ) : (
              slotsRequis.map((slot) => (
                <Badge key={slot} variant="outline">
                  slot: {slot}
                </Badge>
              ))
            )}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Slots (JSON)</label>
            <textarea
              className="min-h-28 w-full rounded-md border bg-background px-3 py-2 text-sm"
              value={slotsTexte}
              onChange={(e) => setSlotsTexte(e.target.value)}
              placeholder='{"article":"lait"}'
            />
          </div>

          <Button onClick={executer} disabled={execution || !intentActif}>
            <Play className="mr-2 h-4 w-4" />
            {execution ? 'Exécution...' : 'Exécuter intent'}
          </Button>

          {reponse && (
            <div className="rounded-md border bg-muted/30 p-3 text-sm">
              <p className="font-medium">Réponse backend</p>
              <p className="text-muted-foreground">{reponse}</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Intents disponibles</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {intents.map((intent) => (
            <div key={intent.intent} className="rounded-md border p-3">
              <p className="font-medium">{intent.intent}</p>
              <p className="text-sm text-muted-foreground">{intent.description}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Action attendue: {intent.action_attendue}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
