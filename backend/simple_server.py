#!/usr/bin/env python3
"""
Servidor simples para teste
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Criar app simples
app = FastAPI(title="RedATM Test")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "RedATM Test Server"}

@app.get("/admin")
async def admin():
    return FileResponse("app/static/admin.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("🚀 Iniciando servidor de teste simples...")
    print("📊 Acesse: http://localhost:8080/admin")
    print("🔧 Health: http://localhost:8080/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8080) 