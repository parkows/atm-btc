#!/usr/bin/env python3
"""
Script para construir aplicativo desktop RedATM
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🔨 Construindo Aplicativo Desktop LiquidGold")
    print("=" * 50)
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Verificar se tkinter está disponível
    try:
        import tkinter
        print("✅ Tkinter encontrado")
    except ImportError:
        print("❌ Tkinter não encontrado. Instalando...")
        # No macOS, tkinter geralmente vem com Python
    
    # Criar spec file personalizado
    create_spec_file()
    
    # Construir executável
    print("🔨 Construindo aplicativo desktop...")
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--noconsole",
        "--name=LiquidGold_Desktop",
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "--add-data=app/static:app/static",
        "--add-data=config:config",
        "--add-data=logs:logs",
        "--add-data=reports:reports",
        "--add-data=translations:translations",
        "--hidden-import=uvicorn",
        "--hidden-import=fastapi",
        "--hidden-import=app.main",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "desktop_app.py"
    ]
    
    # Remover argumentos vazios
    cmd = [arg for arg in cmd if arg]
    
    print(f"Executando: {' '.join(cmd)}")
    subprocess.run(cmd)
    
    print("✅ Aplicativo construído!")
    print("📁 Arquivo: dist/LiquidGold_Desktop")
    print("🚀 Execute: ./dist/LiquidGold_Desktop")
    
    # Criar script de instalação
    create_install_script()

def create_spec_file():
    """Criar arquivo spec personalizado"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/static', 'app/static'),
        ('config', 'config'),
        ('logs', 'logs'),
        ('reports', 'reports'),
        ('translations', 'translations'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'app.main',
        'app.api',
        'app.core',
        'app.models',
        'app.schemas',
        'app.deps',
        'tkinter',
        'tkinter.ttk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LiquidGold_Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open("RedATM_Desktop.spec", "w") as f:
        f.write(spec_content)
    
    print("✅ Arquivo spec criado")

def create_install_script():
    """Criar script de instalação"""
    
    install_script = '''#!/bin/bash

echo "🚀 Instalando RedATM Desktop"
echo "=============================="

# Verificar se o executável existe
if [ ! -f "dist/RedATM_Desktop" ]; then
    echo "❌ Executável não encontrado. Execute build_desktop_app.py primeiro."
    exit 1
fi

# Tornar executável
chmod +x dist/RedATM_Desktop

# Criar atalho no Desktop (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 Criando atalho no Desktop..."
    
    # Criar aplicativo .app
    mkdir -p "RedATM_Desktop.app/Contents/MacOS"
    mkdir -p "RedATM_Desktop.app/Contents/Resources"
    
    # Copiar executável
    cp dist/RedATM_Desktop "RedATM_Desktop.app/Contents/MacOS/"
    
    # Criar Info.plist
    cat > "RedATM_Desktop.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>RedATM_Desktop</string>
    <key>CFBundleIdentifier</key>
    <string>com.redatm.desktop</string>
    <key>CFBundleName</key>
    <string>RedATM Desktop</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF
    
    # Mover para Applications
    if [ -d "/Applications" ]; then
        mv "RedATM_Desktop.app" "/Applications/"
        echo "✅ Aplicativo instalado em /Applications/RedATM_Desktop.app"
    else
        echo "✅ Aplicativo criado: RedATM_Desktop.app"
    fi
fi

echo "✅ Instalação concluída!"
echo "🚀 Execute: ./dist/RedATM_Desktop"
'''
    
    with open("install.sh", "w") as f:
        f.write(install_script)
    
    os.chmod("install.sh", 0o755)
    print("✅ Script de instalação criado: install.sh")

if __name__ == "__main__":
    main() 