#!/usr/bin/env python3
"""
Servidor simples que funciona
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="RedATM Admin")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "RedATM Admin Server"}

@app.get("/admin")
async def admin():
    return FileResponse("app/static/admin.html")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Server is running"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "message": "API is working"}

if __name__ == "__main__":
    print("🚀 Iniciando RedATM - Interface Administrativa")
    print("=" * 50)
    print("📊 Dashboard: http://127.0.0.1:8080/admin")
    print("🔧 Health: http://127.0.0.1:8080/health")
    print("📋 API Health: http://127.0.0.1:8080/api/health")
    print("=" * 50)
    print("🔄 Pressione Ctrl+C para parar")
    print("")
    
    uvicorn.run(app, host="127.0.0.1", port=8080) 