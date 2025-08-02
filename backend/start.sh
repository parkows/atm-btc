#!/bin/bash

# Script para iniciar o RedATM com interface administrativa

echo "🚀 Iniciando RedATM - Painel Administrativo"
echo "=============================================="

# Verificar se estamos no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Erro: Execute este script do diretório backend/"
    exit 1
fi

# Verificar se Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Erro: Python não encontrado"
    exit 1
fi

# Verificar se as dependências estão instaladas
echo "📦 Verificando dependências..."
python -c "import fastapi, uvicorn, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs config reports translations app/static

# Verificar se os arquivos estáticos existem
if [ ! -f "app/static/admin.html" ]; then
    echo "❌ Erro: Arquivo admin.html não encontrado"
    exit 1
fi

if [ ! -f "app/static/admin.js" ]; then
    echo "❌ Erro: Arquivo admin.js não encontrado"
    exit 1
fi

echo "✅ Tudo pronto!"
echo ""
echo "🌐 URLs disponíveis:"
echo "   📊 Dashboard: http://127.0.0.1:3000/admin"
echo "   🔧 API Docs: http://127.0.0.1:3000/docs"
echo "   📋 Health: http://127.0.0.1:3000/api/health"
echo ""
echo "🔄 Pressione Ctrl+C para parar o servidor"
echo ""

# Iniciar o servidor
python start_admin.py 