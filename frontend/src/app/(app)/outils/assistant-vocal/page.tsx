'use client'

import { useState, useRef, useCallback } from 'react'
import { Mic, MicOff, Send, Loader2, Volume2, RotateCcw } from 'lucide-react'
import { Button } from '@/composants/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card'
import { Badge } from '@/composants/ui/badge'
import { clientApi } from '@/bibliotheque/api/client'

type RecognitionResultEvent = {
  results: ArrayLike<ArrayLike<{ transcript: string }>>
}

type RecognitionErrorEvent = {
  error: string
}

type ReconnaissanceVocale = {
  lang: string
  continuous: boolean
  interimResults: boolean
  onresult: ((event: RecognitionResultEvent) => void) | null
  onerror: ((event: RecognitionErrorEvent) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

type ReconnaissanceVocaleCtor = new () => ReconnaissanceVocale

interface ResultatCommande {
  action: string
  message: string
  details?: Record<string, unknown>
}

interface EntreeHistorique {
  id: number
  texte: string
  resultat?: ResultatCommande
  erreur?: string
  horodatage: Date
}

// Exemples de commandes vocales pour l'aide
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

  const reconnaissanceRef = useRef<ReconnaissanceVocale | null>(null)
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

    reconnaissance.onresult = (event: RecognitionResultEvent) => {
      const transcription = event.results[0][0].transcript
      setTexteTranscrit(transcription)
      setEnEcoute(false)
    }

    reconnaissance.onerror = (event: RecognitionErrorEvent) => {
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
        const { data } = await clientApi.post<ResultatCommande>(
          '/assistant/commande-vocale',
          { texte }
        )
        setHistorique((prev) => [
          { id, texte, resultat: data, horodatage: new Date() },
          ...prev.slice(0, 19),
        ])
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : 'Erreur lors de l\'envoi de la commande'
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
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold">Assistant vocal</h1>
        <p className="text-muted-foreground mt-1">
          Parlez ou tapez une commande — ajout courses, mesure Jules, rappels...
        </p>
      </div>

      {/* Zone principale */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          {/* Bouton microphone */}
          <div className="flex justify-center">
            <button
              onClick={enEcoute ? arreterEcoute : demarrerEcoute}
              disabled={chargement}
              className={`
                w-24 h-24 rounded-full flex items-center justify-center transition-all
                focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2
                ${enEcoute
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-200'
                  : 'bg-primary hover:bg-primary/90 shadow-md'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
              aria-label={enEcoute ? 'Arrêter l\'écoute' : 'Démarrer l\'écoute'}
            >
              {enEcoute ? (
                <MicOff className="w-10 h-10 text-white" />
              ) : (
                <Mic className="w-10 h-10 text-white" />
              )}
            </button>
          </div>

          {enEcoute && (
            <p className="text-center text-sm text-muted-foreground animate-pulse">
              Écoute en cours... Parlez maintenant
            </p>
          )}

          {/* Zone de texte */}
          <div className="flex gap-2">
            <input
              type="text"
              value={texteTranscrit}
              onChange={(e) => setTexteTranscrit(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  envoyerCommande(texteTranscrit)
                }
              }}
              placeholder="Texte transcrit ou tapez une commande..."
              className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              disabled={chargement}
            />
            <Button
              onClick={() => envoyerCommande(texteTranscrit)}
              disabled={!texteTranscrit.trim() || chargement}
              size="icon"
            >
              {chargement ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>

          {erreurNavigateur && (
            <p className="text-sm text-red-500 text-center">{erreurNavigateur}</p>
          )}
        </CardContent>
      </Card>

      {/* Exemples */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Exemples de commandes
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {EXEMPLES_COMMANDES.map((exemple) => (
            <button
              key={exemple}
              onClick={() => setTexteTranscrit(exemple)}
              className="text-xs px-3 py-1.5 rounded-full border border-dashed hover:bg-muted transition-colors"
            >
              {exemple}
            </button>
          ))}
        </CardContent>
      </Card>

      {/* Historique */}
      {historique.length > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-medium text-muted-foreground">Historique</h2>
          {historique.map((entree) => (
            <Card key={entree.id} className={entree.erreur ? 'border-red-200' : ''}>
              <CardContent className="pt-4 pb-3 space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium">«&nbsp;{entree.texte}&nbsp;»</p>
                  <div className="flex items-center gap-1 shrink-0">
                    {entree.resultat && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6"
                        onClick={() => lireCommande(entree.resultat!.message)}
                        title="Lire la réponse"
                      >
                        <Volume2 className="w-3 h-3" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => {
                        setTexteTranscrit(entree.texte)
                      }}
                      title="Rejouer"
                    >
                      <RotateCcw className="w-3 h-3" />
                    </Button>
                  </div>
                </div>

                {entree.resultat && (
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs font-mono">
                        {entree.resultat.action}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {entree.resultat.message}
                    </p>
                  </div>
                )}

                {entree.erreur && (
                  <p className="text-sm text-red-500">{entree.erreur}</p>
                )}

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
  )
}
