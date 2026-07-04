function safeName(value) {
  return (value || "source2study-capture")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "source2study-capture";
}

chrome.action.onClicked.addListener((tab) => {
  if (!tab.id) return;
  chrome.tabs.sendMessage(tab.id, { type: "SOURCE2STUDY_EXPORT_CURRENT_PAGE" }, (capture) => {
    if (chrome.runtime.lastError || !capture) return;
    const json = JSON.stringify(capture, null, 2);
    const url = "data:application/json;charset=utf-8," + encodeURIComponent(json);
    const filename = `source2study-${safeName(capture.platform)}-${safeName(capture.title)}.browser_capture.json`;
    chrome.downloads.download({ url, filename, saveAs: true });
  });
});
