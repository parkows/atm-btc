#!/usr/bin/env python3
"""
Script para abrir a interface administrativa no navegador
"""

import subprocess
import time
import webbrowser
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

def main():
    print("🚀 Abrindo Interface Administrativa RedATM")
    print("=" * 50)
    
    # Parar processos antigos
    print("🔄 Parando processos antigos...")
    subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
    
    # Aguardar um momento
    time.sleep(2)
    
    # Iniciar servidor
    print("🚀 Iniciando servidor...")
    
    try:
        # Importar a aplicação
        from app.main import app
        
        # URLs
        admin_url = "http://127.0.0.1:8080/admin"
        health_url = "http://127.0.0.1:8080/api/health"
        
        print(f"📊 Dashboard: {admin_url}")
        print(f"📋 Health: {health_url}")
        print("=" * 50)
        
        # Iniciar servidor em background
        server_process = subprocess.Popen([
            "uvicorn", "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8080",
            "--reload"
        ])
        
        # Aguardar servidor iniciar
        print("⏳ Aguardando servidor iniciar...")
        time.sleep(5)
        
        # Abrir navegador
        print("🌐 Abrindo navegador...")
        webbrowser.open(admin_url)
        
        print("✅ Interface aberta no navegador!")
        print("🔄 Pressione Ctrl+C para parar o servidor")
        
        # Manter servidor rodando
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n👋 Parando servidor...")
            server_process.terminate()
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 