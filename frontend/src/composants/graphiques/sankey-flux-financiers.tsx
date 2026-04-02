"use client";

import { useMemo } from "react";

export interface NoeudFluxFinancier {
  nom: string;
  montant: number;
  details?: Array<{ nom: string; montant: number }>;
}

function repartirSegments(valeurs: number[], hauteurTotale: number, debutY: number) {
  const somme = valeurs.reduce((acc, valeur) => acc + valeur, 0) || 1;
  let curseur = debutY;

  return valeurs.map((valeur) => {
    const hauteur = (valeur / somme) * hauteurTotale;
    const segment = { y: curseur, h: hauteur };
    curseur += hauteur;
    return segment;
  });
}

export function SankeyFluxFinanciers({
  donnees,
  hauteur = 360,
}: {
  donnees: NoeudFluxFinancier[];
  hauteur?: number;
}) {
  const categories = useMemo(
    () => donnees.filter((item) => item.montant > 0).sort((a, b) => b.montant - a.montant),
    [donnees]
  );

  const total = categories.reduce((acc, item) => acc + item.montant, 0);

  const categoriesLayout = useMemo(
    () => repartirSegments(categories.map((item) => item.montant), hauteur - 80, 40),
    [categories, hauteur]
  );

  const details = useMemo(
    () => categories.flatMap((categorie) => (categorie.details ?? []).slice(0, 3)),
    [categories]
  );

  const detailsLayout = useMemo(
    () => repartirSegments(details.map((item) => item.montant), hauteur - 80, 40),
    [details, hauteur]
  );

  if (!categories.length || total <= 0) {
    return (
      <div className="flex h-[280px] items-center justify-center text-sm text-muted-foreground">
        Pas assez de flux financiers pour afficher le Sankey.
      </div>
    );
  }

  let detailIndex = 0;

  return (
    <svg viewBox={`0 0 760 ${hauteur}`} className="h-auto w-full">
      <text x="60" y="24" className="fill-muted-foreground text-[12px]">Budget mensuel</text>
      <text x="300" y="24" className="fill-muted-foreground text-[12px]">Catégories</text>
      <text x="560" y="24" className="fill-muted-foreground text-[12px]">Sous-catégories</text>

      <rect x="40" y="40" width="110" height={hauteur - 80} rx="18" fill="rgba(37, 99, 235, 0.14)" stroke="rgba(37, 99, 235, 0.35)" />
      <text x="58" y="76" className="fill-foreground text-[14px] font-semibold">Total</text>
      <text x="58" y="100" className="fill-muted-foreground text-[12px]">{total.toFixed(0)} €</text>

      {categories.map((categorie, index) => {
        const bloc = categoriesLayout[index];
        const y = bloc.y;
        const h = Math.max(28, bloc.h);

        const detailsCategorie = (categorie.details ?? []).slice(0, 3);
        const valeurSourceY = y + h / 2;

        return (
          <g key={categorie.nom}>
            <path
              d={`M 150 ${valeurSourceY} C 210 ${valeurSourceY}, 240 ${y + h / 2}, 280 ${y + h / 2}`}
              fill="none"
              stroke="rgba(14, 116, 144, 0.18)"
              strokeWidth={Math.max(14, (categorie.montant / total) * 96)}
              strokeLinecap="round"
            />
            <rect x="280" y={y} width="160" height={h} rx="16" fill="rgba(16, 185, 129, 0.16)" stroke="rgba(5, 150, 105, 0.35)" />
            <text x="296" y={y + 24} className="fill-foreground text-[13px] font-medium">{categorie.nom}</text>
            <text x="296" y={y + 42} className="fill-muted-foreground text-[12px]">{categorie.montant.toFixed(0)} €</text>

            {detailsCategorie.map((detail) => {
              const segment = detailsLayout[detailIndex];
              detailIndex += 1;
              const detailY = segment?.y ?? y;
              const detailH = Math.max(24, segment?.h ?? 24);
              const sourceY = y + h / 2;
              const cibleY = detailY + detailH / 2;

              return (
                <g key={`${categorie.nom}-${detail.nom}`}>
                  <path
                    d={`M 440 ${sourceY} C 490 ${sourceY}, 520 ${cibleY}, 560 ${cibleY}`}
                    fill="none"
                    stroke="rgba(245, 158, 11, 0.22)"
                    strokeWidth={Math.max(8, (detail.montant / total) * 80)}
                    strokeLinecap="round"
                  />
                  <rect x="560" y={detailY} width="150" height={detailH} rx="14" fill="rgba(245, 158, 11, 0.14)" stroke="rgba(217, 119, 6, 0.35)" />
                  <text x="574" y={detailY + 22} className="fill-foreground text-[12px] font-medium">{detail.nom}</text>
                  <text x="574" y={detailY + 38} className="fill-muted-foreground text-[11px]">{detail.montant.toFixed(0)} €</text>
                </g>
              );
            })}
          </g>
        );
      })}
    </svg>
  );
}
