#!/bin/bash

echo "🚀 Iniciando Simulação ATM para Apresentação"
echo "=============================================="

# Verificar se o Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não está instalado. Por favor, instale o Node.js primeiro."
    exit 1
fi

# Verificar se o npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm não está instalado. Por favor, instale o npm primeiro."
    exit 1
fi

echo "✅ Node.js e npm encontrados"

# Instalar dependências se necessário
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

echo "🎯 Iniciando aplicação..."
echo "🌐 Acesse: http://localhost:3000"
echo "📱 Pressione Ctrl+C para parar"
echo ""

# Iniciar a aplicação
npm start 