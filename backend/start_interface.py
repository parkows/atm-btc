#!/usr/bin/env python3
"""
Script final para iniciar a interface administrativa do RedATM
"""

import uvicorn
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

def main():
    """Inicia o servidor RedATM com interface administrativa"""
    
    print("🚀 RedATM - Interface Administrativa")
    print("=" * 50)
    print("📊 Dashboard: http://127.0.0.1:3000/admin")
    print("🔧 API Docs: http://127.0.0.1:3000/docs")
    print("📋 Health Check: http://127.0.0.1:3000/api/health")
    print("=" * 50)
    print("🔄 Pressione Ctrl+C para parar o servidor")
    print("")
    
    try:
        # Importar a aplicação
        from app.main import app
        
        # Configurações do servidor
        config = {
            "host": "127.0.0.1",
            "port": 3000,
            "reload": False,
            "log_level": "info",
            "access_log": True
        }
        
        # Iniciar servidor
        uvicorn.run(
            "app.main:app",
            **config
        )
        
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 