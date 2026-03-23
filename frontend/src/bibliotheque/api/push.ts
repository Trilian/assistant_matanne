// ═══════════════════════════════════════════════════════════
// API Push — Notifications Web Push
// ═══════════════════════════════════════════════════════════

import { clientApi } from "./client";

export interface PushSubscriptionPayload {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
}

export interface PushStatus {
  has_subscriptions: boolean;
  subscription_count: number;
  notifications_enabled: boolean;
}

/** Souscrire aux notifications push */
export async function souscrirePush(
  subscription: PushSubscriptionPayload
): Promise<{ success: boolean; message: string }> {
  const { data } = await clientApi.post("/push/subscribe", subscription);
  return data;
}

/** Se désabonner des notifications push */
export async function desabonnerPush(
  endpoint: string
): Promise<{ success: boolean; message: string }> {
  const { data } = await clientApi.delete("/push/unsubscribe", {
    data: { endpoint },
  });
  return data;
}

/** Statut des notifications push */
export async function statutPush(): Promise<PushStatus> {
  const { data } = await clientApi.get<PushStatus>("/push/status");
  return data;
}
