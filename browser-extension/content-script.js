function metaContent(selectors) {
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    const value = element && (element.getAttribute("content") || element.textContent || "").trim();
    if (value) return value;
  }
  return "";
}

const MAX_TEXT_CHARS = 50000;
const MAX_HTML_CHARS = 100000;
const MAX_IMAGES = 20;

function detectPlatform() {
  const host = location.hostname.toLowerCase();
  if (host.includes("mp.weixin.qq.com")) return "wechat";
  if (host.includes("xiaohongshu.com")) return "xiaohongshu";
  if (host.includes("zhihu.com")) return "zhihu";
  if (host.includes("bilibili.com")) return "bilibili";
  if (host.includes("youtube.com") || host.includes("youtu.be")) return "youtube";
  return "web";
}

function redactSensitive(value) {
  return String(value || "")
    .replace(/authorization\s*:\s*bearer\s+[a-z0-9._-]+/gi, "Authorization: [REDACTED]")
    .replace(/cookie\s*:\s*[^\n\r<]+/gi, "Cookie: [REDACTED]")
    .replace(/(api[_-]?key|access[_-]?token|refresh[_-]?token|sessionid)\s*[:=]\s*[^\s<]+/gi, "$1=[REDACTED]")
    .replace(/sk-[a-z0-9_-]{16,}/gi, "sk-[REDACTED]")
    .replace(/-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/g, "[REDACTED PRIVATE KEY]");
}

function riskWarnings(value) {
  const text = String(value || "").toLowerCase();
  const warnings = [];
  if (text.includes("authorization: bearer")) warnings.push("authorization header pattern redacted");
  if (text.includes("cookie:")) warnings.push("cookie header pattern redacted");
  if (/(api[_-]?key|access[_-]?token|refresh[_-]?token|sessionid)\s*[:=]/i.test(value || "")) warnings.push("token-like pattern redacted");
  if (/-----BEGIN [A-Z ]*PRIVATE KEY-----/.test(value || "")) warnings.push("private-key pattern redacted");
  return warnings;
}

function sanitizeHtml() {
  const root = document.querySelector("article, main, [role='main']") || document.body;
  if (!root) return "";
  const clone = root.cloneNode(true);
  clone.querySelectorAll("script, style, noscript, iframe, canvas, svg, form, input, textarea, select, button").forEach((node) => node.remove());
  clone.querySelectorAll("[hidden], [aria-hidden='true']").forEach((node) => node.remove());
  return redactSensitive(clone.innerHTML || "").slice(0, MAX_HTML_CHARS);
}

function buildCapture() {
  const rawText = (document.body && document.body.innerText ? document.body.innerText : "").trim();
  const warnings = riskWarnings(rawText);
  const text = redactSensitive(rawText).slice(0, MAX_TEXT_CHARS);
  const contentHtml = sanitizeHtml();
  const images = Array.from(document.images || [])
    .slice(0, MAX_IMAGES)
    .map((image) => ({ src: image.currentSrc || image.src, alt: image.alt || "" }))
    .filter((image) => image.src);
  return {
    schema_version: "1.3.0",
    source_type: "browser_capture",
    platform: detectPlatform(),
    title: document.title || metaContent(["meta[property='og:title']", "h1"]),
    author: metaContent(["meta[name='author']", "meta[property='article:author']", "#profileBt", ".author"]),
    published_at: metaContent(["meta[property='article:published_time']", "meta[name='pubdate']", "#publish_time"]),
    url: location.href,
    content_html: contentHtml,
    text,
    images,
    capture_method: "current_page_dom",
    user_initiated_capture: true,
    captured_at: new Date().toISOString(),
    sanitizer: "studyloom_current_page_v1",
    content_truncated: rawText.length > MAX_TEXT_CHARS || contentHtml.length >= MAX_HTML_CHARS,
    risk_warnings: Array.from(new Set(warnings))
  };
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === "SOURCE2STUDY_EXPORT_CURRENT_PAGE") {
    sendResponse(buildCapture());
  }
});
