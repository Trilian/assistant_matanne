document.documentElement.dataset.assistantMatanneDriveBridge = "ready";
window.dispatchEvent(new CustomEvent("assistant-matanne-drive-bridge-ready"));

window.addEventListener("message", (event) => {
  if (event.source !== window) {
    return;
  }

  const data = event.data;
  if (!data || data.source !== "assistant-matanne") {
    return;
  }

  const typeMessage = data.type === "REMAP_CARREFOUR_DRIVE" ? "REMAP_FROM_APP" : data.type === "SYNC_CARREFOUR_DRIVE" ? "SYNC_FROM_APP" : null;
  if (!typeMessage) {
    return;
  }

  chrome.runtime.sendMessage(
    {
      type: typeMessage,
      payload: data.payload || {},
    },
    (response) => {
      const detail = chrome.runtime.lastError
        ? { ok: false, error: chrome.runtime.lastError.message }
        : response || { ok: false, error: "Aucune réponse de l'extension." };

      window.dispatchEvent(
        new CustomEvent("assistant-matanne-drive-sync-result", {
          detail,
        })
      );
    }
  );
});
