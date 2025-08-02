#!/usr/bin/env python3
"""
Script para abrir o navegador com a interface administrativa
"""

import webbrowser
import time

def main():
    print("🌐 Abrindo Interface Administrativa RedATM")
    print("=" * 50)
    
    # URLs para tentar
    urls = [
        "http://127.0.0.1:8080/admin",
        "http://localhost:8080/admin",
        "http://127.0.0.1:5000/admin",
        "http://localhost:5000/admin",
        "http://127.0.0.1:3000/admin",
        "http://localhost:3000/admin"
    ]
    
    print("📊 Tentando abrir as seguintes URLs:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    print("=" * 50)
    print("🌐 Abrindo navegador...")
    
    # Abrir todas as URLs
    for url in urls:
        try:
            print(f"🔗 Tentando: {url}")
            webbrowser.open(url)
            time.sleep(1)
        except Exception as e:
            print(f"❌ Erro ao abrir {url}: {e}")
    
    print("✅ Navegador aberto!")
    print("📋 Se nenhuma página carregar, inicie o servidor manualmente:")
    print("   cd /Users/ravrok/atm-btc/backend")
    print("   uvicorn app.main:app --host 127.0.0.1 --port 8080")

if __name__ == "__main__":
    main() 