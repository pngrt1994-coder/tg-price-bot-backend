from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/estimate")
def estimate():
    return {"summary": "✅ Тест працює! Ваш бот зможе отримувати відповіді."}
