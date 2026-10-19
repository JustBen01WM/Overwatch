import json
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def find_author(soup):
    # 1. Standard meta tags
    tag = soup.find("meta", attrs={"name": "author"}) or soup.find(
        "meta", attrs={"property": "article:author"}
    )
    if tag and tag.get("content"):
        author = tag["content"]
        if author.startswith("http"):
            author = author.rstrip("/").split("/")[-1]
        return author

    # 2. Hidden JSON-LD data
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            a = item.get("author") if isinstance(item, dict) else None
            if isinstance(a, list) and a:
                a = a[0]
            if isinstance(a, dict) and a.get("name"):
                return a["name"]
    return None


def scrape_article(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the author before removing page clutter
    author = find_author(soup)

    for tag in soup(["script", "style", "nav", "footer", "aside", "form", "header"]):
        tag.decompose()

    container = soup.find("article") or soup.find("main") or soup.body

    paragraphs = [p.get_text(" ", strip=True) for p in container.find_all("p")]
    text = "\n".join(p for p in paragraphs if len(p) > 40)

    if len(text) < 500:
        raise ValueError(
            "Not enough article text found. This may be a section page, a "
            "paywalled article, or a site that blocks scrapers. Try a link to "
            "a single article, or use the 'Paste the text' tab."
        )

    # Collect up to 4 real image links
    images = []
    for img in container.find_all("img", src=True):
        src = urljoin(url, img["src"])
        if src.startswith("http") and src not in images:
            images.append(src)
    images = images[:4]

    return {
        "url": url,
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "author": author or "not found",
        "images": images,
        "text": text[:15000],
    }