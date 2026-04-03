import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { utiliserWebSocket } from "@/crochets/utiliser-websocket";

class MockWebSocket {
  static OPEN = 1;
  static CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readyState = MockWebSocket.OPEN;
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  send = vi.fn();
  close = vi.fn(() => {
    this.readyState = MockWebSocket.CLOSED;
  });

  constructor(public url: string) {
    MockWebSocket.instances.push(this);
  }

  open() {
    this.onopen?.();
  }

  closeWithEvent() {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  }

  error() {
    this.onerror?.();
  }

  message(data: unknown) {
    this.onmessage?.({ data: JSON.stringify(data) });
  }
}

async function flushPromises() {
  await Promise.resolve();
}

describe("utiliserWebSocket", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.useFakeTimers();
    MockWebSocket.instances = [];
    fetchMock.mockReset();
    vi.stubGlobal("WebSocket", MockWebSocket as unknown as typeof WebSocket);
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("reste déconnecté sans URL", () => {
    const { result } = renderHook(() => utiliserWebSocket({ url: null }));
    expect(result.current.connecte).toBe(false);
    expect(result.current.erreur).toBeNull();
    expect(result.current.mode).toBe("deconnecte");
  });

  it("établit la connexion avec URL", () => {
    const { result } = renderHook(() => utiliserWebSocket({ url: "ws://localhost:8000/ws" }));
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.open();
    });

    expect(result.current.connecte).toBe(true);
    expect(result.current.mode).toBe("websocket");
    expect(typeof result.current.envoyer).toBe("function");
    expect(result.current.dernierMessage).toBeNull();

    act(() => {
      result.current.envoyer({ action: "ping" });
    });

    expect(ws.send).toHaveBeenCalledWith(JSON.stringify({ action: "ping" }));
  });

  it("expose la liste des utilisateurs à vide par défaut", () => {
    const { result } = renderHook(() => utiliserWebSocket({ url: "ws://localhost:8000/ws" }));
    expect(Array.isArray(result.current.utilisateurs)).toBe(true);
    expect(result.current.utilisateurs).toHaveLength(0);
  });

  it("met à jour les utilisateurs et appelle les gestionnaires de messages", () => {
    const gestionnaireSync = vi.fn();
    const { result } = renderHook(() =>
      utiliserWebSocket({
        url: "ws://localhost:8000/ws",
        gestionnaires: { sync: gestionnaireSync },
      })
    );
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.open();
      ws.message({
        type: "users_list",
        users: [{ user_id: "u1", username: "Anne", connected_at: "2026-04-03T10:00:00Z" }],
      });
      ws.message({
        type: "user_joined",
        user_id: "u2",
        username: "Marc",
        timestamp: "2026-04-03T10:00:01Z",
      });
      ws.message({
        type: "user_left",
        user_id: "u1",
      });
      ws.message({
        type: "sync",
        action: "item_added",
      });
    });

    expect(result.current.utilisateurs).toEqual([
      { user_id: "u2", username: "Marc", connected_at: "2026-04-03T10:00:01Z" },
    ]);
    expect(result.current.dernierMessage).toEqual({ type: "sync", action: "item_added" });
    expect(gestionnaireSync).toHaveBeenCalledWith({ type: "sync", action: "item_added" });
  });

  it("met les messages en file d'attente hors connexion puis les flush au prochain envoi", () => {
    const { result } = renderHook(() => utiliserWebSocket({ url: "ws://localhost:8000/ws" }));
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.readyState = MockWebSocket.CLOSED;
      result.current.envoyer({ action: "queued" });
      ws.readyState = MockWebSocket.OPEN;
      ws.open();
      result.current.envoyer({ action: "live" });
    });

    expect(ws.send).toHaveBeenNthCalledWith(1, JSON.stringify({ action: "live" }));
    expect(ws.send).toHaveBeenNthCalledWith(2, JSON.stringify({ action: "queued" }));
  });

  it("bascule en mode polling après épuisement des tentatives et poste les actions via HTTP", async () => {
    const gestionnaireSync = vi.fn();
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        current_seq: 2,
        users: [{ user_id: "poll-1", username: "Poll", connected_at: "2026-04-03T10:00:00Z" }],
        changes: [{ type: "sync", action: "item_checked", item_id: 9, checked: true }],
      }),
    });

    const { result } = renderHook(() =>
      utiliserWebSocket({
        url: "ws://localhost:8000/ws",
        maxTentatives: 0,
        intervallePolling: 1000,
        urlPollingFallback: "/api/v1/ws/courses/1/poll",
        urlActionFallback: "/api/v1/ws/courses/1/action",
        gestionnaires: { sync: gestionnaireSync },
      })
    );
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.closeWithEvent();
    });
    await act(async () => {
      await flushPromises();
    });

    expect(result.current.mode).toBe("polling");
    expect(result.current.connecte).toBe(true);
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/ws/courses/1/poll?since_seq=0");
    expect(result.current.utilisateurs).toEqual([
      { user_id: "poll-1", username: "Poll", connected_at: "2026-04-03T10:00:00Z" },
    ]);
    expect(gestionnaireSync).toHaveBeenCalledWith({
      type: "sync",
      action: "item_checked",
      item_id: 9,
      checked: true,
    });

    act(() => {
      result.current.envoyer({ action: "item_checked", item_id: 9, checked: true });
    });
    await act(async () => {
      await flushPromises();
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/ws/courses/1/action",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "item_checked", item_id: 9, checked: true }),
      })
    );
  });

  it("déclenche une reconnexion avec backoff et expose les erreurs WebSocket", () => {
    const { result } = renderHook(() =>
      utiliserWebSocket({
        url: "ws://localhost:8000/ws",
        delaiReconnexion: 500,
        maxTentatives: 2,
      })
    );
    const ws = MockWebSocket.instances[0];

    act(() => {
      ws.error();
    });
    expect(result.current.erreur).toBe("Erreur de connexion WebSocket");

    act(() => {
      ws.closeWithEvent();
      vi.advanceTimersByTime(500);
    });

    expect(MockWebSocket.instances).toHaveLength(2);
    expect(result.current.connecte).toBe(false);
  });
});
