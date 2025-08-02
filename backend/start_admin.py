#!/usr/bin/env python3
"""
Script para iniciar o servidor RedATM com interface administrativa
"""

import uvicorn
import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

def main():
    """Inicia o servidor com configurações otimizadas"""
    
    print("🚀 Iniciando RedATM - Painel Administrativo")
    print("=" * 50)
    print("📊 Dashboard: http://127.0.0.1:3000/admin")
    print("🔧 API: http://127.0.0.1:3000/docs")
    print("📋 Health Check: http://127.0.0.1:3000/api/health")
    print("=" * 50)
    
    # Configurações do servidor
    config = {
        "host": "127.0.0.1",
        "port": 3000,
        "reload": True,
        "log_level": "info",
        "access_log": True
    }
    
    # Iniciar servidor
    uvicorn.run(
        "app.main:app",
        **config
    )

if __name__ == "__main__":
    main() 