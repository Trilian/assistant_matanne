'use client'

import { useState, useRef, useCallback } from 'react'
import { Mic, MicOff, Send, Loader2, Volume2, RotateCcw, Sparkles } from 'lucide-react'
import { Button } from '@/composants/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Badge } from '@/composants/ui/badge'
import { Input } from '@/composants/ui/input'
import { MemoVocal } from '@/composants/ia/memo-vocal'
import { clientApi } from '@/bibliotheque/api/client'
import type { ObjetDonnees } from '@/types/commun'

type ReconnaissanceVocaleCtor = new () => SpeechRecognition

interface ResultatCommande {
  action: string
  message: string
  details?: ObjetDonnees
}

interface EntreeHistorique {
  id: number
  texte: string
  resultat?: ResultatCommande
  erreur?: string
  horodatage: Date
}

const EXEMPLES_COMMANDES = [
  'Ajoute du lait à la liste',
  'Jules pèse 8,5 kg',
  'Rappelle-moi d\'arroser les plantes demain',
  'Planning de demain',
]

export default function AssistantVocalPage() {
  const [enEcoute, setEnEcoute] = useState(false)
  const [texteTranscrit, setTexteTranscrit] = useState('')
  const [chargement, setChargement] = useState(false)
  const [historique, setHistorique] = useState<EntreeHistorique[]>([])
  const [erreurNavigateur, setErreurNavigateur] = useState<string | null>(null)

  const reconnaissanceRef = useRef<SpeechRecognition | null>(null)
  const compteurRef = useRef(0)

  const demarrerEcoute = useCallback(() => {
    const fenetre = window as typeof window & {
      SpeechRecognition?: ReconnaissanceVocaleCtor
      webkitSpeechRecognition?: ReconnaissanceVocaleCtor
    }
    const SpeechRecognitionAPI = fenetre.SpeechRecognition ?? fenetre.webkitSpeechRecognition

    if (!SpeechRecognitionAPI) {
      setErreurNavigateur(
        'Votre navigateur ne supporte pas la reconnaissance vocale. Essayez Chrome ou Edge.'
      )
      return
    }

    const reconnaissance = new SpeechRecognitionAPI()
    reconnaissance.lang = 'fr-FR'
    reconnaissance.continuous = false
    reconnaissance.interimResults = false

    reconnaissance.onresult = (event: SpeechRecognitionEvent) => {
      const transcription = event.results[0][0].transcript
      setTexteTranscrit(transcription)
      setEnEcoute(false)
    }

    reconnaissance.onerror = (event: SpeechRecognitionErrorEvent) => {
      setEnEcoute(false)
      if (event.error !== 'no-speech') {
        setErreurNavigateur(`Erreur reconnaissance vocale : ${event.error}`)
      }
    }

    reconnaissance.onend = () => {
      setEnEcoute(false)
    }

    reconnaissanceRef.current = reconnaissance
    reconnaissance.start()
    setEnEcoute(true)
    setErreurNavigateur(null)
  }, [])

  const arreterEcoute = useCallback(() => {
    reconnaissanceRef.current?.stop()
    setEnEcoute(false)
  }, [])

  const envoyerCommande = useCallback(
    async (texte: string) => {
      if (!texte.trim()) return

      setChargement(true)
      compteurRef.current += 1
      const id = compteurRef.current

      try {
        const { data } = await clientApi.post<ResultatCommande>('/assistant/commande-vocale', { texte })
        setHistorique((prev) => [
          { id, texte, resultat: data, horodatage: new Date() },
          ...prev.slice(0, 19),
        ])
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Erreur lors de l\'envoi de la commande'
        setHistorique((prev) => [
          { id, texte, erreur: message, horodatage: new Date() },
          ...prev.slice(0, 19),
        ])
      } finally {
        setChargement(false)
        setTexteTranscrit('')
      }
    },
    []
  )

  const lireCommande = useCallback((texte: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(texte)
      utterance.lang = 'fr-FR'
      window.speechSynthesis.speak(utterance)
    }
  }, [])

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <Card className="overflow-hidden border-violet-200/70 bg-[linear-gradient(135deg,rgba(245,243,255,0.96),rgba(255,255,255,0.92))] shadow-sm dark:border-violet-900/60 dark:bg-[linear-gradient(135deg,rgba(22,16,36,0.96),rgba(9,14,22,0.94))]">
        <CardContent className="flex flex-col gap-4 p-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">Assistant vocal</Badge>
              <Badge variant="outline">Chrome / Edge</Badge>
              <Badge variant="outline">fr-FR</Badge>
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight lg:text-3xl">🎙️ Assistant vocal</h1>
              <p className="mt-1 max-w-3xl text-sm text-muted-foreground">
                Parlez ou tapez une commande pour piloter les modules famille, cuisine et maison avec une interface cohérente et rapide.
              </p>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/60 bg-white/70 px-4 py-3 dark:border-white/10 dark:bg-white/5">
              <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Saisie</p>
              <p className="mt-1 text-lg font-semibold">Voix + clavier</p>
            </div>
            <div className="rounded-2xl border border-white/60 bg-white/70 px-4 py-3 dark:border-white/10 dark:bg-white/5">
              <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Réactivité</p>
              <p className="mt-1 text-lg font-semibold">Commande rapide</p>
            </div>
            <div className="rounded-2xl border border-white/60 bg-white/70 px-4 py-3 dark:border-white/10 dark:bg-white/5">
              <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">Coût cognitif</p>
              <p className="mt-1 text-lg font-semibold">Minimal</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Sparkles className="h-5 w-5 text-primary" />
                Commande instantanée
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="flex justify-center">
                <button
                  onClick={enEcoute ? arreterEcoute : demarrerEcoute}
                  disabled={chargement}
                  className={`
                    flex h-24 w-24 items-center justify-center rounded-full transition-all
                    focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2
                    ${
                      enEcoute
                        ? 'animate-pulse bg-red-500 shadow-lg shadow-red-200 hover:bg-red-600'
                        : 'bg-primary shadow-md hover:bg-primary/90'
                    }
                    disabled:cursor-not-allowed disabled:opacity-50
                  `}
                  aria-label={enEcoute ? 'Arrêter l\'écoute' : 'Démarrer l\'écoute'}
                >
                  {enEcoute ? <MicOff className="h-10 w-10 text-white" /> : <Mic className="h-10 w-10 text-white" />}
                </button>
              </div>

              <div className="text-center text-sm text-muted-foreground" role="status" aria-live="polite">
                {enEcoute ? 'Écoute en cours… parlez maintenant.' : 'Touchez le micro ou saisissez une commande ci-dessous.'}
              </div>

              <form
                className="flex gap-2"
                onSubmit={(e) => {
                  e.preventDefault()
                  envoyerCommande(texteTranscrit)
                }}
              >
                <Input
                  type="text"
                  value={texteTranscrit}
                  onChange={(e) => setTexteTranscrit(e.target.value)}
                  placeholder="Texte transcrit ou tapez une commande..."
                  disabled={chargement}
                />
                <Button
                  type="submit"
                  disabled={!texteTranscrit.trim() || chargement}
                  size="icon"
                  aria-label="Envoyer"
                >
                  {chargement ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </Button>
              </form>

              <div className="rounded-xl border bg-muted/30 p-3">
                <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Exemples de commandes</p>
                <div className="flex flex-wrap gap-2">
                  {EXEMPLES_COMMANDES.map((exemple) => (
                    <button
                      key={exemple}
                      type="button"
                      onClick={() => setTexteTranscrit(exemple)}
                      className="rounded-full border border-dashed px-3 py-1.5 text-xs transition-colors hover:bg-muted"
                    >
                      {exemple}
                    </button>
                  ))}
                </div>
              </div>

              {erreurNavigateur && <p className="text-center text-sm text-red-500">{erreurNavigateur}</p>}
            </CardContent>
          </Card>

          {historique.length > 0 && (
            <div className="space-y-2">
              <h2 className="text-sm font-medium text-muted-foreground">Historique récent</h2>
              {historique.map((entree) => (
                <Card key={entree.id} className={entree.erreur ? 'border-red-200 dark:border-red-900/50' : ''}>
                  <CardContent className="space-y-3 pt-4 pb-3">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium">« {entree.texte} »</p>
                      <div className="flex shrink-0 items-center gap-1">
                        {entree.resultat && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7"
                            onClick={() => lireCommande(entree.resultat!.message)}
                            title="Lire la réponse"
                          >
                            <Volume2 className="h-3.5 w-3.5" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7"
                          onClick={() => {
                            setTexteTranscrit(entree.texte)
                          }}
                          title="Rejouer"
                        >
                          <RotateCcw className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>

                    {entree.resultat && (
                      <div className="space-y-1">
                        <Badge variant="outline" className="text-xs font-mono">
                          {entree.resultat.action}
                        </Badge>
                        <p className="text-sm text-muted-foreground">{entree.resultat.message}</p>
                      </div>
                    )}

                    {entree.erreur && <p className="text-sm text-red-500">{entree.erreur}</p>}

                    <p className="text-xs text-muted-foreground">
                      {entree.horodatage.toLocaleTimeString('fr-FR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        <MemoVocal />
      </div>
    </div>
  )
}
