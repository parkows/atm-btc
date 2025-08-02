#!/usr/bin/env python3
"""
Script simples para construir executável RedATM
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
    
    # Limpar diretório dist se existir
    if os.path.exists("dist"):
        print("🗑️ Limpando diretório dist...")
        shutil.rmtree("dist")
    
    # Construir executável simples
    print("🔨 Construindo executável...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=RedATM_Desktop",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "redatm_desktop.py"
    ]
    
    print(f"Executando: {' '.join(cmd)}")
    subprocess.run(cmd)
    
    print("✅ Executável construído!")
    print("📁 Arquivo: dist/RedATM_Desktop")
    print("🚀 Execute: ./dist/RedATM_Desktop")

if __name__ == "__main__":
    main() 