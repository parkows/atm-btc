#!/usr/bin/env python3
"""
Servidor final na porta 5000
"""

import uvicorn
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

def main():
    print("🚀 RedATM - Interface Administrativa")
    print("=" * 50)
    print("📊 Dashboard: http://127.0.0.1:5000/admin")
    print("🔧 API Docs: http://127.0.0.1:5000/docs")
    print("📋 Health: http://127.0.0.1:5000/api/health")
    print("=" * 50)
    print("🔄 Pressione Ctrl+C para parar")
    print("")
    
    try:
        # Importar a aplicação
        from app.main import app
        
        # Iniciar servidor na porta 5000
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=5000,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 