#!/bin/bash

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
