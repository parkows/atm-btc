#!/usr/bin/env python3
"""
Script para iniciar o servidor com debug completo
"""

import sys
import os
import uvicorn
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

def main():
    print("🔍 Debug completo do servidor")
    print("=" * 40)
    
    # Verificar diretório
    print(f"📁 Diretório atual: {os.getcwd()}")
    
    # Verificar se os arquivos existem
    files = ["app/main.py", "app/static/admin.html", "app/static/admin.js"]
    for file in files:
        if os.path.exists(file):
            print(f"✅ {file} existe")
        else:
            print(f"❌ {file} não existe")
    
    # Tentar importar a aplicação
    try:
        print("\n📦 Importando aplicação...")
        from app.main import app
        print("✅ Aplicação importada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar aplicação: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Tentar iniciar servidor
    try:
        print("\n🚀 Iniciando servidor...")
        print("📊 Dashboard: http://127.0.0.1:3000/admin")
        print("🔧 API Docs: http://127.0.0.1:3000/docs")
        print("📋 Health: http://127.0.0.1:3000/api/health")
        print("=" * 40)
        
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=3000,
            reload=False,
            log_level="debug"
        )
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 