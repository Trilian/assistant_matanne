"use client";

import dynamic from "next/dynamic";
import { TrendingDown, TrendingUp, Minus, MapPin } from "lucide-react";
import { Badge } from "@/composants/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/composants/ui/card";
import type { BarometreHabitat, BarometreVilleHabitat } from "@/types/habitat";

// Recharts chargé côté client uniquement
const ResponsiveContainer = dynamic(() => import("recharts").then((m) => m.ResponsiveContainer), { ssr: false });
const BarChart = dynamic(() => import("recharts").then((m) => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then((m) => m.Bar), { ssr: false });
const Cell = dynamic(() => import("recharts").then((m) => m.Cell), { ssr: false });
const LineChart = dynamic(() => import("recharts").then((m) => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then((m) => m.Line), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then((m) => m.CartesianGrid), { ssr: false });
const XAxis = dynamic(() => import("recharts").then((m) => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then((m) => m.YAxis), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then((m) => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then((m) => m.Legend), { ssr: false });

// Palette de couleurs pour les lignes de tendance
const COULEURS_VILLES = [
  "#0f766e", "#7c3aed", "#b45309", "#0369a1",
  "#be185d", "#15803d", "#9a3412", "#1d4ed8",
  "#a21caf", "#047857",
];

function BadgeEvolution({ pct }: { pct?: number | null }) {
  if (pct == null) return <span className="text-xs text-muted-foreground">—</span>;
  if (pct > 0.5)
    return (
      <Badge variant="destructive" className="text-xs gap-1">
        <TrendingUp className="h-3 w-3" />
        +{pct.toFixed(1)} %
      </Badge>
    );
  if (pct < -0.5)
    return (
      <Badge variant="secondary" className="bg-emerald-100 text-emerald-800 text-xs gap-1">
        <TrendingDown className="h-3 w-3" />
        {pct.toFixed(1)} %
      </Badge>
    );
  return (
    <Badge variant="secondary" className="text-xs gap-1">
      <Minus className="h-3 w-3" />
      {pct.toFixed(1)} %
    </Badge>
  );
}

interface GraphiquesBarometreProps {
  barometre: BarometreHabitat;
}

export function GraphiquesBarometre({ barometre }: GraphiquesBarometreProps) {
  const { villes, rang_local } = barometre;

  if (villes.length === 0) {
    return (
      <Card className="p-8 text-center text-muted-foreground">
        Aucune donnée disponible pour ce baromètre. Réessayez dans quelques instants.
      </Card>
    );
  }

  // Données pour le bar chart horizontal (prix médian par ville)
  const dataBarChart = [...villes]
    .sort((a, b) => b.prix_m2_median - a.prix_m2_median)
    .map((v) => ({
      name: v.est_locale ? `★ ${v.ville}` : v.ville,
      prix: v.prix_m2_median,
      est_locale: v.est_locale,
    }));

  // Données pour les courbes de tendance (12 derniers mois)
  // On construit un tableau unifié de mois
  const tousLesMois = Array.from(
    new Set(villes.flatMap((v) => v.historique.map((h) => h.mois)))
  ).sort();

  const dataTendance = tousLesMois.map((mois) => {
    const point: Record<string, string | number | null> = { mois };
    villes.forEach((v) => {
      const h = v.historique.find((x) => x.mois === mois);
      point[v.est_locale ? `★ ${v.ville}` : v.ville] = h?.prix_m2_median ?? null;
    });
    return point;
  });

  // Ville la moins chère et la plus chère
  const villeMax = villes[0];
  const villeMin = villes[villes.length - 1];
  const villeLocale = villes.find((v) => v.est_locale);

  return (
    <div className="space-y-6">
      {/* ── Encarts synthèse ─────────────────────────────────────────── */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardContent className="pt-5">
            <p className="text-xs uppercase tracking-widest text-muted-foreground">Plus cher</p>
            <p className="mt-1 text-xl font-bold text-destructive">
              {villeMax.prix_m2_median.toLocaleString("fr-FR")} €/m²
            </p>
            <p className="mt-0.5 text-sm font-medium">{villeMax.ville}</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-5">
            <p className="text-xs uppercase tracking-widest text-muted-foreground">Moins cher</p>
            <p className="mt-1 text-xl font-bold text-emerald-600">
              {villeMin.prix_m2_median.toLocaleString("fr-FR")} €/m²
            </p>
            <p className="mt-0.5 text-sm font-medium">{villeMin.ville}</p>
          </CardContent>
        </Card>

        {villeLocale ? (
          <Card className="border-primary/50 bg-primary/5">
            <CardContent className="pt-5">
              <p className="text-xs uppercase tracking-widest text-muted-foreground flex items-center gap-1">
                <MapPin className="h-3 w-3" /> Ma zone
              </p>
              <p className="mt-1 text-xl font-bold">
                {villeLocale.prix_m2_median.toLocaleString("fr-FR")} €/m²
              </p>
              <p className="mt-0.5 text-sm font-medium">{villeLocale.ville}</p>
            </CardContent>
          </Card>
        ) : null}

        {rang_local != null ? (
          <Card>
            <CardContent className="pt-5">
              <p className="text-xs uppercase tracking-widest text-muted-foreground">Rang local</p>
              <p className="mt-1 text-xl font-bold">
                {rang_local}<span className="text-base font-normal text-muted-foreground">/{villes.length}</span>
              </p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {rang_local <= 3 ? "Parmi les plus chers" : rang_local > villes.length - 3 ? "Parmi les moins chers" : "Zone intermédiaire"}
              </p>
            </CardContent>
          </Card>
        ) : null}
      </div>

      {/* ── Bar chart : prix médian par ville ────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Prix médian au m² par ville</CardTitle>
          <CardDescription>
            Classé par prix décroissant · {barometre.type_local} · Source DVF data.gouv
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dataBarChart} layout="vertical" margin={{ left: 16, right: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => `${Math.round(Number(v ?? 0)).toLocaleString("fr-FR")} €`}
                />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={110} />
                <Tooltip
                  formatter={(value) => [
                    `${Math.round(Number(value ?? 0)).toLocaleString("fr-FR")} €/m²`,
                    "Prix médian",
                  ]}
                />
                <Bar dataKey="prix" radius={[0, 6, 6, 0]} maxBarSize={28}>
                  {dataBarChart.map((entry, index) => (
                    <Cell
                      key={`cell-${entry.name}`}
                      fill={entry.est_locale ? "#0f766e" : COULEURS_VILLES[index % COULEURS_VILLES.length]}
                      opacity={entry.est_locale ? 1 : 0.72}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* ── Line chart : évolution comparative ───────────────────────── */}
      {dataTendance.length > 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Évolution comparative sur 12 mois</CardTitle>
            <CardDescription>Prix médian au m² mensuel — toutes les villes du baromètre.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dataTendance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="mois" tick={{ fontSize: 10 }} />
                  <YAxis
                    tick={{ fontSize: 11 }}
                    tickFormatter={(v) => `${Math.round(Number(v ?? 0)).toLocaleString("fr-FR")} €`}
                  />
                  <Tooltip
                    formatter={(value, name) => [
                      value != null ? `${Math.round(Number(value)).toLocaleString("fr-FR")} €/m²` : "—",
                      String(name),
                    ]}
                  />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  {villes.map((v, idx) => {
                    const nomCle = v.est_locale ? `★ ${v.ville}` : v.ville;
                    return (
                      <Line
                        key={nomCle}
                        type="monotone"
                        dataKey={nomCle}
                        stroke={COULEURS_VILLES[idx % COULEURS_VILLES.length]}
                        strokeWidth={v.est_locale ? 3 : 1.5}
                        dot={false}
                        strokeDasharray={v.est_locale ? undefined : "6 3"}
                        connectNulls
                      />
                    );
                  })}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Tableau récapitulatif ─────────────────────────────────────── */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Tableau comparatif</CardTitle>
          <CardDescription>Classement des villes avec indicateurs d'évolution (3 derniers mois).</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-xs uppercase tracking-wide text-muted-foreground">
                  <th className="pb-2 text-left">Rang</th>
                  <th className="pb-2 text-left">Ville</th>
                  <th className="pb-2 text-right">Prix médian</th>
                  <th className="pb-2 text-right">Évolution 3 mois</th>
                  <th className="pb-2 text-right">Transactions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {villes.map((ville: BarometreVilleHabitat, idx) => (
                  <tr
                    key={ville.code_postal}
                    className={ville.est_locale ? "bg-primary/5 font-semibold" : ""}
                  >
                    <td className="py-2 text-muted-foreground">{idx + 1}</td>
                    <td className="py-2">
                      {ville.est_locale ? (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3.5 w-3.5 text-primary" />
                          {ville.ville}
                        </span>
                      ) : (
                        ville.ville
                      )}
                    </td>
                    <td className="py-2 text-right tabular-nums">
                      {ville.prix_m2_median.toLocaleString("fr-FR")} €/m²
                    </td>
                    <td className="py-2 text-right">
                      <BadgeEvolution pct={ville.evolution_3m_pct} />
                    </td>
                    <td className="py-2 text-right tabular-nums text-muted-foreground">
                      {ville.nb_transactions}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
