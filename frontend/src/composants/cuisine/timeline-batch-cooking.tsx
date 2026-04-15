"use client";

import Link from "next/link";
import { motion } from "framer-motion";

import type { SessionBatchCooking } from "@/types/batch-cooking";

const COULEURS_STATUT = {
  planifiee: "from-slate-200 to-slate-100 text-slate-900",
  en_cours: "from-amber-200 to-orange-100 text-orange-950",
  terminee: "from-emerald-200 to-emerald-100 text-emerald-950",
  annulee: "from-rose-200 to-rose-100 text-rose-950",
  pause: "from-sky-200 to-sky-100 text-sky-950",
} as const;

export function TimelineBatchCooking({
  sessions,
}: {
  sessions: SessionBatchCooking[];
}) {
  const sessionsTriees = [...sessions]
    .filter((session) => session.date_session)
    .sort((a, b) => a.date_session.localeCompare(b.date_session))
    .slice(0, 6);

  if (!sessionsTriees.length) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="relative ml-4 border-l border-dashed border-border pl-8">
        {sessionsTriees.map((session, index) => {
          const progression = Math.round((session.progression ?? 0) * 100);

          return (
            <motion.div
              key={session.id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.35, delay: index * 0.08 }}
              className="relative mb-5"
            >
              <span className="absolute -left-[2.4rem] top-5 h-4 w-4 rounded-full border-2 border-background bg-primary shadow-sm" />
              <Link href={`/cuisine/batch-cooking/${session.id}`} className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-2xl">
              <div className={`rounded-2xl border bg-gradient-to-r p-4 cursor-pointer hover:opacity-90 transition-opacity ${COULEURS_STATUT[session.statut] ?? COULEURS_STATUT.planifiee}`}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold">{session.nom}</p>
                    <p className="text-xs opacity-80">
                      {new Date(session.date_session).toLocaleDateString("fr-FR", {
                        weekday: "short",
                        day: "numeric",
                        month: "short",
                      })}
                      {session.duree_estimee ? ` · ${session.duree_estimee} min` : ""}
                    </p>
                  </div>
                  <div className="text-right text-xs opacity-90">
                    <p>{session.etapes_count} étapes</p>
                    <p>{session.recettes_selectionnees.length} recettes</p>
                  </div>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-background/50">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.max(10, progression || (session.statut === "terminee" ? 100 : 18))}%` }}
                    transition={{ duration: 0.7, delay: index * 0.1 }}
                    className="h-full rounded-full bg-foreground/80"
                  />
                </div>
              </div>
              </Link>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
