'use client'

import { useEffect, useMemo, useState } from 'react'
import { CalendarDays, Clock3, CloudSun, ListChecks, Utensils } from 'lucide-react'

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

export default function WidgetTablettePage() {
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 60_000)
    return () => window.clearInterval(timer)
  }, [])

  const blocRepas = useMemo(
    () => ({
      titre: 'Repas du jour',
      valeur: 'Poulet roti, legumes au four',
      sousTexte: 'Prep 30 min - cuisson 45 min',
    }),
    [],
  )

  const blocTache = useMemo(
    () => ({
      titre: 'Tache prioritaire',
      valeur: 'Verifier entretien filtre VMC',
      sousTexte: 'A faire avant 18:00',
    }),
    [],
  )

  const blocMeteo = useMemo(
    () => ({
      titre: 'Meteo',
      valeur: '17 degres - eclaircies',
      sousTexte: 'Risque pluie faible en soiree',
    }),
    [],
  )

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

        <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-4 flex items-center gap-2 text-emerald-300">
              <Utensils className="h-5 w-5" />
              <h2 className="text-lg font-medium">{blocRepas.titre}</h2>
            </div>
            <p className="text-xl font-semibold leading-snug">{blocRepas.valeur}</p>
            <p className="mt-2 text-sm text-zinc-300">{blocRepas.sousTexte}</p>
          </article>

          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-4 flex items-center gap-2 text-amber-300">
              <ListChecks className="h-5 w-5" />
              <h2 className="text-lg font-medium">{blocTache.titre}</h2>
            </div>
            <p className="text-xl font-semibold leading-snug">{blocTache.valeur}</p>
            <p className="mt-2 text-sm text-zinc-300">{blocTache.sousTexte}</p>
          </article>

          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-4 flex items-center gap-2 text-sky-300">
              <CloudSun className="h-5 w-5" />
              <h2 className="text-lg font-medium">{blocMeteo.titre}</h2>
            </div>
            <p className="text-xl font-semibold leading-snug">{blocMeteo.valeur}</p>
            <p className="mt-2 text-sm text-zinc-300">{blocMeteo.sousTexte}</p>
          </article>
        </section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-3 flex items-center gap-2 text-zinc-300">
              <CalendarDays className="h-5 w-5" />
              <h2 className="text-lg font-medium">Agenda rapide</h2>
            </div>
            <ul className="space-y-2 text-base text-zinc-100">
              <li>09:00 - Activite exterieure Jules</li>
              <li>12:30 - Dejeuner famille</li>
              <li>18:15 - Courses d'appoint</li>
            </ul>
          </article>

          <article className="rounded-2xl border border-zinc-700/60 bg-zinc-900/70 p-5">
            <div className="mb-3 flex items-center gap-2 text-zinc-300">
              <Clock3 className="h-5 w-5" />
              <h2 className="text-lg font-medium">Timer cuisine</h2>
            </div>
            <p className="text-3xl font-semibold">00:25:00</p>
            <p className="mt-2 text-sm text-zinc-300">Mode affiche tablette: vue lisible a distance.</p>
          </article>
        </section>
      </div>
    </main>
  )
}
