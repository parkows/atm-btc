#!/usr/bin/env python3
"""
Script para construir executável da interface administrativa RedATM
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🔨 Construindo Executável RedATM")
    print("=" * 50)
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Criar arquivo principal do executável
    create_main_file()
    
    # Construir executável
    print("🔨 Construindo executável...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=RedATM_Admin",
        "--add-data=app/static:app/static",
        "--add-data=config:config",
        "--add-data=logs:logs",
        "--add-data=reports:reports",
        "--add-data=translations:translations",
        "executable_main.py"
    ]
    
    subprocess.run(cmd)
    
    print("✅ Executável construído!")
    print("📁 Arquivo: dist/RedATM_Admin")
    print("🚀 Execute: ./dist/RedATM_Admin")

def create_main_file():
    """Criar arquivo principal do executável"""
    
    main_code = '''#!/usr/bin/env python3
"""
RedATM - Interface Administrativa (Executável)
"""

import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

# Adicionar diretórios ao path
if getattr(sys, 'frozen', False):
    # Executável
    base_path = Path(sys._MEIPASS)
else:
    # Desenvolvimento
    base_path = Path(__file__).parent

# Configurar paths
os.chdir(base_path)
sys.path.insert(0, str(base_path))

def start_server():
    """Iniciar servidor FastAPI"""
    try:
        import uvicorn
        from app.main import app
        
        print("🚀 Iniciando servidor RedATM...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8080,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def open_browser():
    """Abrir navegador"""
    time.sleep(3)
    try:
        print("🌐 Abrindo navegador...")
        webbrowser.open("http://127.0.0.1:8080/admin")
        print("✅ Interface aberta no navegador!")
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")

def main():
    print("🎛️ RedATM - Interface Administrativa")
    print("=" * 50)
    print("📊 Dashboard: http://127.0.0.1:8080/admin")
    print("🔧 API Docs: http://127.0.0.1:8080/docs")
    print("📋 Health: http://127.0.0.1:8080/api/health")
    print("=" * 50)
    
    # Iniciar servidor em thread separada
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Abrir navegador
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    print("🔄 Servidor iniciado! Pressione Ctrl+C para parar")
    
    try:
        # Manter aplicação rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n👋 Parando RedATM...")

if __name__ == "__main__":
    main()
'''
    
    with open("executable_main.py", "w") as f:
        f.write(main_code)
    
    print("✅ Arquivo principal criado")

if __name__ == "__main__":
    main() 