from fastapi import FastAPI
from .db import init_db
from .routers import auth, pedidos, produtos

app = FastAPI(title="PDV Delivery API")


app.include_router(auth.router, prefix="/auth")
app.include_router(pedidos.router)  # sem prefixo extra aqui
app.include_router(produtos.router)  # sem prefixo extra aqui

@app.get("/health")
async def health():
    return {"ok": True}

@app.on_event("startup")
async def startup():
    await init_db()