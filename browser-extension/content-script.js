function metaContent(selectors) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    const value = element && (element.getAttribute("content") || element.textContent || "").trim();
    if (value) return value;
  }
  return "";
}

function detectPlatform() {
  const host = location.hostname.toLowerCase();
  if (host.includes("mp.weixin.qq.com")) return "wechat";
  if (host.includes("xiaohongshu.com")) return "xiaohongshu";
  if (host.includes("zhihu.com")) return "zhihu";
  if (host.includes("bilibili.com")) return "bilibili";
  if (host.includes("youtube.com") || host.includes("youtu.be")) return "youtube";
  return "web";
}

function buildCapture() {
  const text = (document.body && document.body.innerText ? document.body.innerText : "").trim();
  const images = Array.from(document.images || [])
    .slice(0, 20)
    .map((image) => ({ src: image.currentSrc || image.src, alt: image.alt || "" }))
    .filter((image) => image.src);
  return {
    source_type: "browser_capture",
    platform: detectPlatform(),
    title: document.title || metaContent(["meta[property='og:title']", "h1"]),
    author: metaContent(["meta[name='author']", "meta[property='article:author']", "#profileBt", ".author"]),
    published_at: metaContent(["meta[property='article:published_time']", "meta[name='pubdate']", "#publish_time"]),
    url: location.href,
    content_html: document.body ? document.body.innerHTML : "",
    text,
    images,
    capture_method: "current_page_dom",
    user_initiated_capture: true
  };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === "SOURCE2STUDY_EXPORT_CURRENT_PAGE") {
    sendResponse(buildCapture());
  }
});
