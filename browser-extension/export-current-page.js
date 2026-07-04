function safeName(value) {
  return (value || "studyloom-capture")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "studyloom-capture";
}

chrome.action.onClicked.addListener((tab) => {
  if (!tab.id) return;
  chrome.tabs.sendMessage(tab.id, { type: "SOURCE2STUDY_EXPORT_CURRENT_PAGE" }, (capture) => {
    if (chrome.runtime.lastError || !capture) return;
    const json = JSON.stringify(capture, null, 2);
    const url = "data:application/json;charset=utf-8," + encodeURIComponent(json);
    const filename = `studyloom-${safeName(capture.platform)}-${safeName(capture.title)}.browser_capture.json`;
    chrome.downloads.download({ url, filename, saveAs: true });
  });
});
