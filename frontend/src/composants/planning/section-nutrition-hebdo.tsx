'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/composants/ui/card';

interface SectionNutritionHebdoProps {
  nutrition: {
    totaux: {
      calories: number;
      proteines: number;
      glucides: number;
      lipides: number;
    };
    moyenne_calories_par_jour: number;
    nb_repas_sans_donnees: number;
  } | null | undefined;
}

export function SectionNutritionHebdo({ nutrition }: SectionNutritionHebdoProps) {
  if (!nutrition || nutrition.totaux.calories <= 0) return null;

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">🥗 Nutrition de la semaine</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="text-center rounded-md bg-orange-50 dark:bg-orange-950/20 p-2">
            <p className="text-2xl font-bold text-orange-600">{nutrition.totaux.calories}</p>
            <p className="text-xs text-muted-foreground">kcal total</p>
          </div>
          <div className="text-center rounded-md bg-blue-50 dark:bg-blue-950/20 p-2">
            <p className="text-2xl font-bold text-blue-600">{nutrition.totaux.proteines}g</p>
            <p className="text-xs text-muted-foreground">Protéines</p>
          </div>
          <div className="text-center rounded-md bg-yellow-50 dark:bg-yellow-950/20 p-2">
            <p className="text-2xl font-bold text-yellow-600">{nutrition.totaux.glucides}g</p>
            <p className="text-xs text-muted-foreground">Glucides</p>
          </div>
          <div className="text-center rounded-md bg-green-50 dark:bg-green-950/20 p-2">
            <p className="text-2xl font-bold text-green-600">{nutrition.totaux.lipides}g</p>
            <p className="text-xs text-muted-foreground">Lipides</p>
          </div>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Moy. {nutrition.moyenne_calories_par_jour} kcal/jour
          {nutrition.nb_repas_sans_donnees > 0 && (
            <span> · {nutrition.nb_repas_sans_donnees} repas sans données</span>
          )}
        </p>
      </CardContent>
    </Card>
  );
}
