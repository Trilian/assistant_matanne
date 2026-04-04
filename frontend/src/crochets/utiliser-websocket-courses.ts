import { useEffect, useRef, useCallback, useState } from "react";
import type { ObjetDonnees } from "@/types/commun";

interface WSMessage {
  type: string;
  [key: string]: unknown;
}

interface UseWebSocketCoursesOptions {
  listeId: number | null;
  userId?: string;
  username?: string;
  onMessage?: (message: WSMessage) => void;
  onUsersChange?: (users: { user_id: string; username: string }[]) => void;
}

interface UseWebSocketCoursesReturn {
  connected: boolean;
  users: { user_id: string; username: string }[];
  send: (action: string, data?: ObjetDonnees) => void;
  cocherArticle: (itemId: number, checked: boolean) => void;
  ajouterArticle: (nom: string, quantite?: number) => void;
  supprimerArticle: (itemId: number) => void;
}

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
const RECONNECT_DELAY = 3000;
const MAX_RECONNECT = 5;

export function useWebSocketCourses({
  listeId,
  userId = "user-1",
  username = "Utilisateur",
  onMessage,
  onUsersChange,
}: UseWebSocketCoursesOptions): UseWebSocketCoursesReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCount = useRef(0);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [connected, setConnected] = useState(false);
  const [users, setUsers] = useState<{ user_id: string; username: string }[]>([]);

  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;
  const onUsersChangeRef = useRef(onUsersChange);
  onUsersChangeRef.current = onUsersChange;

  const send = useCallback((action: string, data: ObjetDonnees = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action, ...data }));
    }
  }, []);

  const cocherArticle = useCallback(
    (itemId: number, checked: boolean) => send("item_checked", { item_id: itemId, checked }),
    [send]
  );

  const ajouterArticle = useCallback(
    (nom: string, quantite?: number) => send("item_added", { nom, quantite }),
    [send]
  );

  const supprimerArticle = useCallback(
    (itemId: number) => send("item_removed", { item_id: itemId }),
    [send]
  );

  useEffect(() => {
    if (listeId == null) return;

    function connect() {
      const url = `${WS_BASE}/api/v1/ws/courses/${listeId}?user_id=${encodeURIComponent(userId)}&username=${encodeURIComponent(username)}`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        reconnectCount.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data);

          if (msg.type === "users_list" && Array.isArray(msg.users)) {
            const ulist = msg.users as { user_id: string; username: string }[];
            setUsers(ulist);
            onUsersChangeRef.current?.(ulist);
          } else if (msg.type === "user_joined") {
            setUsers((prev) => {
              if (prev.some((u) => u.user_id === msg.user_id)) return prev;
              const next = [...prev, { user_id: msg.user_id as string, username: msg.username as string }];
              onUsersChangeRef.current?.(next);
              return next;
            });
          } else if (msg.type === "user_left") {
            setUsers((prev) => {
              const next = prev.filter((u) => u.user_id !== msg.user_id);
              onUsersChangeRef.current?.(next);
              return next;
            });
          } else if (msg.type === "pong") {
            // heartbeat ack, ignore
          } else {
            onMessageRef.current?.(msg);
          }
        } catch {
          // ignore invalid JSON
        }
      };

      ws.onclose = () => {
        setConnected(false);
        wsRef.current = null;
        if (reconnectCount.current < MAX_RECONNECT) {
          reconnectCount.current++;
          reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    // Heartbeat
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "ping" }));
      }
    }, 30_000);

    return () => {
      clearInterval(pingInterval);
      clearTimeout(reconnectTimer.current);
      reconnectCount.current = MAX_RECONNECT; // prevent reconnect on unmount
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [listeId, userId, username]);

  return { connected, users, send, cocherArticle, ajouterArticle, supprimerArticle };
}
