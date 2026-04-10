/**
 * Données statiques du calendrier saisonnier — fallback offline.
 *
 * Miroir des constantes Python `INGREDIENTS_SAISON_ENRICHI` et `PAIRES_SAISON`
 * dans src/services/cuisine/suggestions/saisons_enrichi.py.
 *
 * Utilisé comme `initialData` / fallback quand le backend est inaccessible.
 */

import type { ReponseCalendrierSaisonnier } from "./api/recettes";

// ─── Types internes ───────────────────────────────────────

interface IngredientStat {
  nom: string;
  categorie: string;
  picMois: number[];
  bioLocal: boolean;
}

interface PaireStat {
  ingredients: string[];
  description: string;
  saison: string;
}

// ─── Catalogue (~120 ingrédients de saison) ──────────────

const INGREDIENTS: Record<string, IngredientStat[]> = {
  printemps: [
    { nom: "asperge", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "radis", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "épinard", categorie: "legume", picMois: [3, 4, 5], bioLocal: true },
    { nom: "petit pois", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "fève", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "carotte nouvelle", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "artichaut", categorie: "legume", picMois: [3, 4, 5], bioLocal: false },
    { nom: "chou-fleur", categorie: "legume", picMois: [3, 4], bioLocal: false },
    { nom: "laitue", categorie: "legume", picMois: [3, 4, 5], bioLocal: true },
    { nom: "cresson", categorie: "legume", picMois: [3, 4], bioLocal: true },
    { nom: "navet nouveau", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "blette", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "oignon nouveau", categorie: "legume", picMois: [4, 5], bioLocal: true },
    { nom: "roquette", categorie: "legume", picMois: [3, 4, 5], bioLocal: true },
    { nom: "fenouil", categorie: "legume", picMois: [4, 5], bioLocal: false },
    { nom: "fraise", categorie: "fruit", picMois: [4, 5], bioLocal: true },
    { nom: "rhubarbe", categorie: "fruit", picMois: [4, 5], bioLocal: true },
    { nom: "cerise", categorie: "fruit", picMois: [5], bioLocal: false },
    { nom: "ciboulette", categorie: "aromate", picMois: [3, 4, 5], bioLocal: true },
    { nom: "menthe", categorie: "aromate", picMois: [4, 5], bioLocal: true },
    { nom: "estragon", categorie: "aromate", picMois: [4, 5], bioLocal: true },
    { nom: "oseille", categorie: "aromate", picMois: [3, 4, 5], bioLocal: true },
    { nom: "maquereau", categorie: "produit_mer", picMois: [3, 4, 5], bioLocal: false },
    { nom: "bar", categorie: "produit_mer", picMois: [3, 4], bioLocal: false },
    { nom: "sardine", categorie: "produit_mer", picMois: [5], bioLocal: false },
  ],
  été: [
    { nom: "tomate", categorie: "legume", picMois: [7, 8], bioLocal: true },
    { nom: "courgette", categorie: "legume", picMois: [6, 7, 8], bioLocal: true },
    { nom: "aubergine", categorie: "legume", picMois: [7, 8], bioLocal: true },
    { nom: "poivron", categorie: "legume", picMois: [7, 8], bioLocal: true },
    { nom: "concombre", categorie: "legume", picMois: [6, 7, 8], bioLocal: true },
    { nom: "haricot vert", categorie: "legume", picMois: [6, 7, 8], bioLocal: true },
    { nom: "maïs", categorie: "legume", picMois: [7, 8], bioLocal: false },
    { nom: "fenouil", categorie: "legume", picMois: [6, 7], bioLocal: false },
    { nom: "betterave", categorie: "legume", picMois: [6, 7, 8], bioLocal: true },
    { nom: "céleri branche", categorie: "legume", picMois: [7, 8], bioLocal: false },
    { nom: "brocoli", categorie: "legume", picMois: [6, 7], bioLocal: false },
    { nom: "artichaut violet", categorie: "legume", picMois: [6, 7], bioLocal: false },
    { nom: "melon", categorie: "fruit", picMois: [7, 8], bioLocal: false },
    { nom: "pastèque", categorie: "fruit", picMois: [7, 8], bioLocal: false },
    { nom: "pêche", categorie: "fruit", picMois: [7, 8], bioLocal: true },
    { nom: "nectarine", categorie: "fruit", picMois: [7, 8], bioLocal: false },
    { nom: "abricot", categorie: "fruit", picMois: [6, 7], bioLocal: true },
    { nom: "cerise", categorie: "fruit", picMois: [6], bioLocal: false },
    { nom: "framboise", categorie: "fruit", picMois: [6, 7, 8], bioLocal: true },
    { nom: "myrtille", categorie: "fruit", picMois: [7, 8], bioLocal: true },
    { nom: "groseille", categorie: "fruit", picMois: [6, 7], bioLocal: true },
    { nom: "cassis", categorie: "fruit", picMois: [7], bioLocal: true },
    { nom: "figue", categorie: "fruit", picMois: [8], bioLocal: false },
    { nom: "prune", categorie: "fruit", picMois: [7, 8], bioLocal: false },
    { nom: "basilic", categorie: "aromate", picMois: [6, 7, 8], bioLocal: true },
    { nom: "coriandre", categorie: "aromate", picMois: [6, 7, 8], bioLocal: true },
    { nom: "aneth", categorie: "aromate", picMois: [6, 7], bioLocal: false },
    { nom: "persil", categorie: "aromate", picMois: [6, 7, 8], bioLocal: true },
    { nom: "sardine", categorie: "produit_mer", picMois: [6, 7, 8], bioLocal: false },
    { nom: "thon rouge", categorie: "produit_mer", picMois: [6, 7], bioLocal: false },
    { nom: "dorade", categorie: "produit_mer", picMois: [7, 8], bioLocal: false },
  ],
  automne: [
    { nom: "champignon", categorie: "champignon", picMois: [9, 10, 11], bioLocal: true },
    { nom: "cèpe", categorie: "champignon", picMois: [9, 10], bioLocal: true },
    { nom: "girolle", categorie: "champignon", picMois: [9, 10], bioLocal: false },
    { nom: "potiron", categorie: "legume", picMois: [9, 10, 11], bioLocal: true },
    { nom: "courge", categorie: "legume", picMois: [9, 10, 11], bioLocal: true },
    { nom: "butternut", categorie: "legume", picMois: [10, 11], bioLocal: true },
    { nom: "potimarron", categorie: "legume", picMois: [9, 10, 11], bioLocal: true },
    { nom: "chou", categorie: "legume", picMois: [9, 10, 11], bioLocal: true },
    { nom: "chou-fleur", categorie: "legume", picMois: [9, 10], bioLocal: false },
    { nom: "brocoli", categorie: "legume", picMois: [9, 10], bioLocal: false },
    { nom: "poireau", categorie: "legume", picMois: [9, 10, 11], bioLocal: true },
    { nom: "céleri", categorie: "legume", picMois: [9, 10, 11], bioLocal: false },
    { nom: "blette", categorie: "legume", picMois: [9, 10], bioLocal: false },
    { nom: "endive", categorie: "legume", picMois: [10, 11], bioLocal: false },
    { nom: "panais", categorie: "legume", picMois: [10, 11], bioLocal: true },
    { nom: "betterave", categorie: "legume", picMois: [9, 10], bioLocal: false },
    { nom: "épinard", categorie: "legume", picMois: [9, 10, 11], bioLocal: false },
    { nom: "pomme", categorie: "fruit", picMois: [9, 10, 11], bioLocal: true },
    { nom: "poire", categorie: "fruit", picMois: [9, 10, 11], bioLocal: true },
    { nom: "raisin", categorie: "fruit", picMois: [9, 10], bioLocal: false },
    { nom: "figue", categorie: "fruit", picMois: [9], bioLocal: false },
    { nom: "coing", categorie: "fruit", picMois: [10, 11], bioLocal: true },
    { nom: "châtaigne", categorie: "fruit", picMois: [10, 11], bioLocal: true },
    { nom: "noix", categorie: "fruit", picMois: [9, 10, 11], bioLocal: true },
    { nom: "noisette", categorie: "fruit", picMois: [9, 10], bioLocal: true },
    { nom: "mirabelle", categorie: "fruit", picMois: [9], bioLocal: false },
    { nom: "thym", categorie: "aromate", picMois: [9, 10, 11], bioLocal: false },
    { nom: "romarin", categorie: "aromate", picMois: [9, 10, 11], bioLocal: false },
    { nom: "sauge", categorie: "aromate", picMois: [9, 10], bioLocal: false },
    { nom: "moule", categorie: "produit_mer", picMois: [9, 10, 11], bioLocal: false },
    { nom: "huître", categorie: "produit_mer", picMois: [10, 11], bioLocal: false },
    { nom: "coquille saint-jacques", categorie: "produit_mer", picMois: [10, 11], bioLocal: false },
  ],
  hiver: [
    { nom: "endive", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "mâche", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "chou de bruxelles", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "navet", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "panais", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "topinambour", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "chou rouge", categorie: "legume", picMois: [12, 1], bioLocal: false },
    { nom: "chou frisé", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "pomme de terre", categorie: "legume", picMois: [12, 1, 2], bioLocal: false },
    { nom: "oignon", categorie: "legume", picMois: [12, 1, 2], bioLocal: false },
    { nom: "carotte", categorie: "legume", picMois: [12, 1, 2], bioLocal: false },
    { nom: "céleri-rave", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "rutabaga", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "salsifis", categorie: "legume", picMois: [12, 1], bioLocal: false },
    { nom: "poireau", categorie: "legume", picMois: [12, 1, 2], bioLocal: true },
    { nom: "épinard", categorie: "legume", picMois: [12, 1], bioLocal: false },
    { nom: "orange", categorie: "fruit", picMois: [12, 1, 2], bioLocal: false },
    { nom: "clémentine", categorie: "fruit", picMois: [12, 1], bioLocal: false },
    { nom: "mandarine", categorie: "fruit", picMois: [12, 1, 2], bioLocal: false },
    { nom: "kiwi", categorie: "fruit", picMois: [12, 1, 2], bioLocal: true },
    { nom: "pamplemousse", categorie: "fruit", picMois: [1, 2], bioLocal: false },
    { nom: "pomme", categorie: "fruit", picMois: [12, 1, 2], bioLocal: true },
    { nom: "poire", categorie: "fruit", picMois: [12, 1], bioLocal: false },
    { nom: "citron", categorie: "fruit", picMois: [12, 1, 2], bioLocal: false },
    { nom: "persil", categorie: "aromate", picMois: [12, 1, 2], bioLocal: false },
    { nom: "cerfeuil", categorie: "aromate", picMois: [12, 1], bioLocal: false },
    { nom: "huître", categorie: "produit_mer", picMois: [12, 1, 2], bioLocal: false },
    { nom: "coquille saint-jacques", categorie: "produit_mer", picMois: [12, 1], bioLocal: false },
    { nom: "moule", categorie: "produit_mer", picMois: [12], bioLocal: false },
    { nom: "lieu noir", categorie: "produit_mer", picMois: [1, 2], bioLocal: false },
  ],
};

const PAIRES: PaireStat[] = [
  { ingredients: ["fraise", "rhubarbe"], description: "Tarte fraise-rhubarbe", saison: "printemps" },
  { ingredients: ["asperge", "œuf", "parmesan"], description: "Asperges gratinées", saison: "printemps" },
  { ingredients: ["petit pois", "menthe"], description: "Petits pois à la menthe", saison: "printemps" },
  { ingredients: ["fève", "pecorino"], description: "Salade de fèves", saison: "printemps" },
  { ingredients: ["radis", "beurre"], description: "Radis beurre sel", saison: "printemps" },
  { ingredients: ["tomate", "mozzarella", "basilic"], description: "Caprese", saison: "été" },
  { ingredients: ["courgette", "chèvre", "menthe"], description: "Tarte courgette-chèvre", saison: "été" },
  { ingredients: ["aubergine", "tomate", "poivron"], description: "Ratatouille", saison: "été" },
  { ingredients: ["melon", "jambon cru"], description: "Melon-jambon", saison: "été" },
  { ingredients: ["pêche", "thym"], description: "Pêches rôties au thym", saison: "été" },
  { ingredients: ["pastèque", "feta", "menthe"], description: "Salade pastèque-feta", saison: "été" },
  { ingredients: ["concombre", "yaourt", "aneth"], description: "Tzatziki", saison: "été" },
  { ingredients: ["potiron", "châtaigne"], description: "Velouté potiron-châtaigne", saison: "automne" },
  { ingredients: ["cèpe", "persil", "ail"], description: "Cèpes persillés", saison: "automne" },
  { ingredients: ["pomme", "cannelle"], description: "Tarte aux pommes", saison: "automne" },
  { ingredients: ["butternut", "noisette"], description: "Butternut rôti aux noisettes", saison: "automne" },
  { ingredients: ["poire", "roquefort", "noix"], description: "Salade poire-roquefort", saison: "automne" },
  { ingredients: ["endive", "noix", "roquefort"], description: "Salade d'endives", saison: "automne" },
  { ingredients: ["endive", "jambon", "béchamel"], description: "Endives au jambon", saison: "hiver" },
  { ingredients: ["chou", "saucisse", "pomme de terre"], description: "Potée hivernale", saison: "hiver" },
  { ingredients: ["orange", "chocolat"], description: "Orangettes", saison: "hiver" },
  { ingredients: ["topinambour", "noisette"], description: "Velouté topinambour", saison: "hiver" },
  { ingredients: ["panais", "miel"], description: "Panais rôtis au miel", saison: "hiver" },
  { ingredients: ["céleri-rave", "pomme", "noix"], description: "Rémoulade de céleri", saison: "hiver" },
];

const MOIS_NOMS = [
  "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
];

const SAISONS: Record<string, number[]> = {
  printemps: [3, 4, 5],
  été: [6, 7, 8],
  automne: [9, 10, 11],
  hiver: [12, 1, 2],
};

function obtenirSaison(mois: number): string {
  for (const [saison, moisList] of Object.entries(SAISONS)) {
    if (moisList.includes(mois)) return saison;
  }
  return "hiver";
}

/** Construit la réponse calendrier à partir des données statiques. */
export function construireCalendrierStatique(): ReponseCalendrierSaisonnier {
  const moisCourant = new Date().getMonth() + 1;
  const saisonCourante = obtenirSaison(moisCourant);

  const calendrier = Array.from({ length: 12 }, (_, i) => {
    const mois = i + 1;
    const ingredients: { nom: string; categorie: string; bio_local: boolean }[] = [];
    for (const items of Object.values(INGREDIENTS)) {
      for (const ing of items) {
        if (ing.picMois.includes(mois)) {
          ingredients.push({ nom: ing.nom, categorie: ing.categorie, bio_local: ing.bioLocal });
        }
      }
    }
    return { mois, nom: MOIS_NOMS[mois], ingredients };
  });

  const paires_saison = PAIRES.map((p) => ({
    ingredients: p.ingredients,
    description: p.description,
    saison: p.saison,
  }));

  return { mois_courant: moisCourant, saison_courante: saisonCourante, calendrier, paires_saison };
}
