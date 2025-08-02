#!/usr/bin/env python3
"""
Script final para iniciar a interface administrativa
"""

import uvicorn
import webbrowser
import time
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

def main():
    print("🚀 RedATM - Interface Administrativa")
    print("=" * 50)
    
    try:
        # Importar a aplicação
        from app.main import app
        
        # URL da interface
        admin_url = "http://127.0.0.1:8080/admin"
        
        print(f"📊 Dashboard: {admin_url}")
        print("🔧 API Docs: http://127.0.0.1:8080/docs")
        print("📋 Health: http://127.0.0.1:8080/api/health")
        print("=" * 50)
        print("⏳ Iniciando servidor...")
        print("🌐 Abrindo navegador em 5 segundos...")
        
        # Abrir navegador após 5 segundos
        def open_browser():
            time.sleep(5)
            print("🌐 Abrindo navegador...")
            webbrowser.open(admin_url)
            print("✅ Interface aberta no navegador!")
        
        # Iniciar thread para abrir navegador
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Iniciar servidor
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8080,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 