"""DuckDuckGo news search with compatibility fallback."""

from html.parser import HTMLParser
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


class _DuckDuckGoResultParser(HTMLParser):
    """Extract result links and snippets from DuckDuckGo HTML results."""

    def __init__(self):
        super().__init__()
        self.results = []
        self._current = None
        self._capture = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if tag == "a" and "result__a" in classes:
            self._current = {"title": "", "url": attributes.get("href", "")}
            self._capture = "title"
        elif tag in {"a", "div"} and "result__snippet" in classes and self._current:
            self._capture = "snippet"

    def handle_data(self, data):
        if self._current and self._capture:
            self._current[self._capture] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._current and self._capture == "title":
            self.results.append(self._current)
            self._current = None
            self._capture = None
        elif self._current and self._capture == "snippet" and tag in {"a", "div"}:
            self._capture = None


def search_recent_news(company_name, max_results=5):
    """Return recent DuckDuckGo results without relying on its broken timer formatting."""
    query = quote_plus(f"{company_name} news")
    request = Request(
        f"https://html.duckduckgo.com/html/?q={query}",
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urlopen(request, timeout=20) as response:
        parser = _DuckDuckGoResultParser()
        parser.feed(response.read().decode("utf-8", errors="replace"))

    results = []
    for item in parser.results[:max_results]:
        results.append({
            "title": " ".join(item["title"].split()),
            "url": item["url"],
            "snippet": " ".join(item.get("snippet", "").split()),
        })
    return results
