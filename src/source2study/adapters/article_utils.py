from __future__ import annotations

from html.parser import HTMLParser


class HTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self._skip = False
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self._skip = True
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self._skip = False
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._skip:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        self.parts.append(text)

    def text(self) -> str:
        return "\n\n".join(self.parts)

    def title(self, fallback: str) -> str:
        title = " ".join(self.title_parts).strip()
        return title or fallback


def html_to_text_and_title(html: str, fallback_title: str) -> tuple[str, str]:
    parser = HTMLTextParser()
    parser.feed(html)
    return parser.text(), parser.title(fallback_title)
