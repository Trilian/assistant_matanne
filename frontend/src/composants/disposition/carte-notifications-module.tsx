"use client";

import { Bell } from "lucide-react";
import { Card, CardContent } from "@/composants/ui/card";
import { Switch } from "@/composants/ui/switch";
import { utiliserMutation, utiliserRequete } from "@/crochets/utiliser-api";
import {
  obtenirPreferencesNotifications,
  sauvegarderPreferencesNotifications,
} from "@/bibliotheque/api/preferences";
import { toast } from "sonner";

interface CarteNotificationsModuleProps {
  moduleKey: string;
  moduleLabel: string;
}

export function CarteNotificationsModule({
  moduleKey,
  moduleLabel,
}: CarteNotificationsModuleProps) {
  const { data: prefs } = utiliserRequete(
    ["preferences", "notifications", "module", moduleKey],
    obtenirPreferencesNotifications,
    { staleTime: 5 * 60 * 1000 }
  );

  const { mutate: sauvegarder, isPending } = utiliserMutation(
    sauvegarderPreferencesNotifications,
    {
      onSuccess: () => {
        toast.success(`Notifications ${moduleLabel} mises a jour`);
      },
      onError: () => {
        toast.error("Impossible de sauvegarder les notifications du module");
      },
    }
  );

  const notificationsParModule = prefs?.notifications_par_module ?? {};
  const actif = notificationsParModule[moduleKey] ?? true;

  const onToggle = (checked: boolean) => {
    const prochain = {
      ...notificationsParModule,
      [moduleKey]: checked,
    };
    sauvegarder({ notifications_par_module: prochain });
  };

  return (
    <Card>
      <CardContent className="pt-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-start gap-2">
            <Bell className="h-4 w-4 mt-0.5 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">Me notifier pour {moduleLabel}</p>
              <p className="text-xs text-muted-foreground">
                Active ou coupe les notifications de ce module sans passer par les
                parametres globaux.
              </p>
            </div>
          </div>
          <Switch
            checked={actif}
            disabled={isPending}
            onCheckedChange={onToggle}
            aria-label={`Notifications ${moduleLabel}`}
          />
        </div>
      </CardContent>
    </Card>
  );
}
