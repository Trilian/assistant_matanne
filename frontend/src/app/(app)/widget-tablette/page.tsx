'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { CalendarPlus, Clock3, CloudSun, ListChecks, Loader2, Timer, Utensils } from 'lucide-react'
import { utiliserRequete } from '@/crochets/utiliser-api'
import { obtenirTableauBord } from '@/bibliotheque/api/tableau-bord'
import { obtenirTachesJourMaison } from '@/bibliotheque/api/maison'

function formatDateFr(date: Date): string {
  return new Intl.DateTimeFormat('fr-FR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
  }).format(date)
}

function formatTimeFr(date: Date): string {
  return new Intl.DateTimeFormat('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function formatTimer(secondes: number): string {
  const minutes = Math.floor(secondes / 60)
  const reste = secondes % 60
  return `${minutes}:${reste.toString().padStart(2, '0')}`
}

export default function WidgetTablettePage() {
  const [now, setNow] = useState(() => new Date())
  const [timerActif, setTimerActif] = useState(false)
  const [timerSecondes, setTimerSecondes] = useState(25 * 60)
  const [meteo, setMeteo] = useState<{ temperature: number; condition: string } | null>(null)

  const { data: dashboard, chargement: chargementDashboard, erreur: erreurDashboard } = utiliserRequete(['dashboard', 'widget'], obtenirTableauBord)
  const { data: taches, chargement: chargementTaches } = utiliserRequete(['maison', 'widget', 'taches'], obtenirTachesJourMaison)

  useEffect(() => {
    const horloge = window.setInterval(() => setNow(new Date()), 30_000)
    return () => window.clearInterval(horloge)
  }, [])

  useEffect(() => {
    let annule = false

    async function chargerMeteo() {
      try {
        const response = await fetch('https://wttr.in/Paris?format=j1')
        if (!response.ok) {
          return
        }
        const json = await response.json()
        const actuel = json.current_condition?.[0]
        if (!actuel || annule) {
          return
        }
        setMeteo({
          temperature: Number(actuel.temp_C ?? 0),
          condition: actuel.weatherDesc?.[0]?.value ?? 'Variable',
        })
      } catch {
        if (!annule) {
          setMeteo(null)
        }
      }
    }

    chargerMeteo()
    return () => {
      annule = true
    }
  }, [])

  useEffect(() => {
    if (!timerActif || timerSecondes <= 0) {
      return
    }
    const interval = window.setInterval(() => {
      setTimerSecondes((precedent) => (precedent > 0 ? precedent - 1 : 0))
    }, 1000)
    return () => window.clearInterval(interval)
  }, [timerActif, timerSecondes])

  const repasAujourdhui = dashboard?.repas_aujourd_hui ?? []
  const tachePrioritaire = (Array.isArray(taches) ? taches : []).find(
    (t: { fait?: boolean }) => !t.fait
  ) as { nom?: string; categorie?: string } | undefined

  return (
    <main className="min-h-screen bg-gradient-to-br from-zinc-950 via-zinc-900 to-emerald-950 p-6 text-zinc-100 md:p-10">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <header className="rounded-2xl border border-zinc-700/50 bg-zinc-900/70 p-6 backdrop-blur">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-emerald-300/90">Widget tablette Google</p>
              <h1 className="mt-2 text-3xl font-semibold md:text-5xl">Assistant Matanne</h1>
            </div>
            <div className="text-right">
              <p className="text-5xl font-semibold leading-none md:text-7xl">{formatTimeFr(now)}</p>
              <p className="mt-2 text-sm capitalize text-zinc-300 md:text-base">{formatDateFr(now)}</p>
            </div>
          </div>
        </header>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-300">
                <Utensils className="h-5 w-5" />
                <h2 className="text-lg font-medium">Repas du jour</h2>
              </div>
              {!chargementDashboard && repasAujourdhui.length === 0 && (
                <Link href="/cuisine/planning" className="flex items-center gap-1 rounded-md bg-emerald-500/20 px-3 py-1 text-xs text-emerald-300 hover:bg-emerald-500/30">
                  <CalendarPlus className="h-3.5 w-3.5" />
                  Planifier
                </Link>
              )}
            </div>
            {chargementDashboard ? (
              <div className="flex items-center gap-2 text-zinc-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Chargement...</span>
              </div>
            ) : erreurDashboard ? (
              <p className="text-sm text-red-400">Connexion impossible au serveur</p>
            ) : repasAujourdhui.length === 0 ? (
              <p className="text-sm text-zinc-400">Aucun repas planifie pour aujourd'hui</p>
            ) : (
              <ul className="space-y-2">
                {repasAujourdhui.map((r: { type_repas?: string; recette_nom?: string }, idx: number) => (
                  <li key={idx} className="flex items-baseline gap-2">
                    <span className="w-20 shrink-0 text-xs capitalize text-emerald-300/80">{r.type_repas ?? 'repas'}</span>
                    <span className="text-base font-semibold leading-snug">{r.recette_nom ?? 'A definir'}</span>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-4 flex items-center gap-2 text-amber-300">
              <ListChecks className="h-5 w-5" />
              <h2 className="text-lg font-medium">Tache prioritaire</h2>
            </div>
            {chargementTaches ? (
              <div className="flex items-center gap-2 text-zinc-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Chargement...</span>
              </div>
            ) : (
              <>
                <p className="text-xl font-semibold leading-snug">{tachePrioritaire?.nom ?? 'Rien de prioritaire'}</p>
                <p className="mt-2 text-sm text-zinc-300">{tachePrioritaire?.categorie ?? 'Maison'}</p>
              </>
            )}
          </article>

          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-4 flex items-center gap-2 text-sky-300">
              <CloudSun className="h-5 w-5" />
              <h2 className="text-lg font-medium">Meteo</h2>
            </div>
            <p className="text-xl font-semibold leading-snug">
              {meteo?.temperature != null ? `${meteo.temperature} degres` : 'Donnee indisponible'}
            </p>
            <p className="mt-2 text-sm text-zinc-300">{meteo?.condition ?? 'Actualisation en cours'}</p>
          </article>
        </section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-3 flex items-center gap-2 text-zinc-300">
              <Clock3 className="h-5 w-5" />
              <h2 className="text-lg font-medium">Agenda rapide</h2>
            </div>
            {chargementDashboard ? (
              <div className="flex items-center gap-2 text-zinc-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Chargement...</span>
              </div>
            ) : (
              <ul className="space-y-2 text-base text-zinc-100 md:text-lg">
                {repasAujourdhui
                  .map((repas: { id?: number | string; type_repas?: string; recette_nom?: string }, index: number) => (
                  <li key={`${repas.id}-${index}`}>
                    {(repas.type_repas ?? 'repas').toString()} - {(repas.recette_nom ?? 'Repas').toString()}
                  </li>
                ))}
                {repasAujourdhui.length === 0 && (
                  <li className="text-zinc-400">
                    Aucun repas aujourd'hui —{' '}
                    <Link href="/cuisine/planning" className="text-emerald-400 underline underline-offset-2">
                      planifier
                    </Link>
                  </li>
                )}
              </ul>
            )}
          </article>

          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-3 flex items-center gap-2 text-zinc-300">
              <Timer className="h-5 w-5" />
              <h2 className="text-lg font-medium">Timer cuisine</h2>
            </div>
            <p className="text-4xl font-semibold md:text-5xl">{formatTimer(timerSecondes)}</p>
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={() => setTimerActif((precedent) => !precedent)}
                className="rounded-md bg-emerald-500 px-4 py-3 text-base font-semibold text-zinc-950"
              >
                {timerActif ? 'Pause' : 'Demarrer'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setTimerActif(false)
                  setTimerSecondes(25 * 60)
                }}
                className="rounded-md border border-zinc-500 px-4 py-3 text-base"
              >
                Reinitialiser
              </button>
            </div>
          </article>
        </section>
      </div>
    </main>
  )
}
