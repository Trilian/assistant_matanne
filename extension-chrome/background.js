chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "START_DRIVE_SYNC") {
    lancerSync(message.articles || [])
      .then(() => sendResponse({ ok: true }))
      .catch((error) => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  if (message?.type === "OPEN_MISSING_SEARCHES") {
    ouvrirRecherches(message.articles || [])
      .then(() => sendResponse({ ok: true }))
      .catch((error) => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  return false;
});

async function lancerSync(articles) {
  await chrome.storage.local.set({ driveSyncQueue: articles, driveSyncResults: {} });

  for (const article of articles) {
    const url = article.correspondance?.produit_drive_url;
    if (!url) continue;
    await chrome.tabs.create({ url, active: false });
  }
}

async function ouvrirRecherches(articles) {
  for (const article of articles) {
    const query = encodeURIComponent(article.nom);
    const url = `https://www.carrefour.fr/s?q=${query}`;
    await chrome.tabs.create({ url, active: false });
  }
}
