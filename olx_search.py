import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Простий User-Agent, щоб сторінка віддавалася як звичайному браузеру
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

def search_olx(query: str, limit: int = 20):
    """
    Повертає список словників: {title, price_uah, url}
    Беремо першу сторінку результатів OLX.
    """
    q = urllib.parse.quote_plus(query)
    url = f"https://www.olx.ua/d/uk/list/q/{q}/"
    headers = {"User-Agent": UA, "Accept-Language": "uk,en;q=0.9"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    items = []

    # Карточки оголошень (селектори можуть змінюватись з часом — це MVP)
    cards = soup.select('[data-testid="l-card"]')
    for card in cards:
        a = card.select_one('a[data-cy="listing-ad-title"]') or card.find("a", href=True)
        title = (a.get_text(strip=True) if a else "").strip()
        href = a["href"] if a and a.has_attr("href") else None
        if href and href.startswith("/"):
            href = "https://www.olx.ua" + href

        price_el = card.select_one('[data-testid="ad-price"]') or card.find(class_="price")
        price_text = price_el.get_text(" ", strip=True) if price_el else ""

        digits = re.sub(r"[^0-9]", "", price_text)
        if not digits:
            continue
        price_uah = int(digits)

        if title and href:
            items.append({
                "title": title,
                "price_uah": price_uah,
                "url": href
            })

        if len(items) >= limit:
            break

    return items
