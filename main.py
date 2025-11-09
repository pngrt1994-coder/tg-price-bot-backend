from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()
from typing import Optional
from fastapi import Query
from olx_search import search_olx

@app.get("/debug_olx")
def debug_olx(q: Optional[str] = Query(None, description="Пошуковий запит")):
    if not q:
        return {"hint": "Додайте параметр ?q=ваш_запит, наприклад: /debug_olx?q=Ноутбук Acer i5"}
    items = search_olx(q, limit=10)
    # Повертаємо перші кілька полів, щоб було зручно дивитися
    simplified = [
        {"title": it["title"], "price_uah": it["price_uah"], "url": it["url"]}
        for it in items
    ]
    return {"count": len(simplified), "items": simplified}

# ---- Допоміжні функції для красивого тексту (Markdown) ----
MDV2_SPECIALS = r"_ * [ ] ( ) ~ > # + - = | { } . !".split()

def escape_mdv2(text: str) -> str:
    out = str(text)
    for ch in MDV2_SPECIALS:
        out = out.replace(ch, f"\\{ch}")
    return out

def render_draft(desc: str, price: int | None) -> str:
    desc_e = escape_mdv2(desc)
    price_e = escape_mdv2(str(price) if price is not None else "не вказана")
    return (
        "💡 *Чернетка оцінки*\n"
        f"• Опис: *{desc_e}*\n"
        f"• Ціна користувача: *{price_e}* грн\n\n"
        "Далі навчимо це шукати оголошення на OLX і рахувати медіану."
    )

# ---- Основні налаштування ----
class EstimateReq(BaseModel):
    query: str
    chat_id: int | None = None
    user_id: int | None = None
    lang: str = "uk"

@app.get("/health")
def health():
    return {"status": "ok"}

# ---- Парсимо запит користувача ----
def parse_query(text: str):
    parts = text.split("=")
    if len(parts) == 1:
        desc = parts[0].strip()
        price = None
    else:
        desc = parts[0].strip()
        price_raw = parts[1]
        digits = re.sub(r"[^0-9]", "", price_raw)
        price = int(digits) if digits else None
    return desc, price

# ---- Головна логіка ----
@app.post("/api/estimate")
def estimate(req: EstimateReq):
    desc, price = parse_query(req.query)
    if not desc:
        raise HTTPException(status_code=400, detail="Порожній опис")

    summary = render_draft(desc, price)
    return {"summary": summary}
