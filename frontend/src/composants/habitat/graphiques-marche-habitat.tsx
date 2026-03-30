"use client";

import dynamic from "next/dynamic";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import type { HistoriqueMarcheHabitatPoint, RepartitionTypeMarcheHabitat } from "@/types/habitat";

const ResponsiveContainer = dynamic(() => import("recharts").then((mod) => mod.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import("recharts").then((mod) => mod.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then((mod) => mod.Line), { ssr: false });
const BarChart = dynamic(() => import("recharts").then((mod) => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then((mod) => mod.Bar), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then((mod) => mod.CartesianGrid), { ssr: false });
const XAxis = dynamic(() => import("recharts").then((mod) => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then((mod) => mod.YAxis), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then((mod) => mod.Tooltip), { ssr: false });

interface GraphiquesMarcheHabitatProps {
  historique: HistoriqueMarcheHabitatPoint[];
  repartition: RepartitionTypeMarcheHabitat[];
}

export function GraphiquesMarcheHabitat({ historique, repartition }: GraphiquesMarcheHabitatProps) {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Prix au m2 par mois</CardTitle>
          <CardDescription>Mediane et moyenne observees dans les transactions DVF filtrees.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historique}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="mois" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(value) => `${Math.round(Number(value ?? 0))} €`} />
                <Tooltip formatter={(value) => [`${Math.round(Number(value ?? 0)).toLocaleString("fr-FR")} €`, "Prix / m2"]} />
                <Line type="monotone" dataKey="prix_m2_median" stroke="#047857" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="prix_m2_moyen" stroke="#b45309" strokeWidth={2} dot={false} strokeDasharray="6 4" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Volume par type de bien</CardTitle>
          <CardDescription>Nombre de transactions et niveau de prix median par typologie.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={repartition}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="type_local" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(value, key) => [Number(value ?? 0).toLocaleString("fr-FR"), key === "transactions" ? "Transactions" : "Prix median / m2"]} />
                <Bar dataKey="transactions" fill="#0f766e" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            {repartition.slice(0, 4).map((item) => (
              <div key={item.type_local} className="rounded-xl border px-3 py-2 text-sm">
                <p className="font-medium">{item.type_local}</p>
                <p className="text-muted-foreground">
                  {item.transactions} ventes · {item.prix_m2_median ? `${Math.round(item.prix_m2_median).toLocaleString("fr-FR")} €/m2` : "prix indisponible"}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}