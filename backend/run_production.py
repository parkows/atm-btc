#!/usr/bin/env python3
"""
Script para executar a aplicação em modo de produção
Utiliza Gunicorn com workers Uvicorn para melhor desempenho
"""

import multiprocessing
import os
import argparse
import subprocess
import signal
import sys

# Configurações padrão
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_WORKERS = min(multiprocessing.cpu_count() * 2 + 1, 8)  # Fórmula recomendada, máximo 8

def parse_arguments():
    """
    Processa argumentos da linha de comando
    """
    parser = argparse.ArgumentParser(description="Executa a aplicação LiquidGold ATM em modo de produção")
    
    parser.add_argument(
        "--host", 
        type=str, 
        default=DEFAULT_HOST,
        help=f"Endereço IP para escutar (padrão: {DEFAULT_HOST})"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=DEFAULT_PORT,
        help=f"Porta para escutar (padrão: {DEFAULT_PORT})"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=DEFAULT_WORKERS,
        help=f"Número de workers (padrão: {DEFAULT_WORKERS})"
    )
    
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="Ativar modo de recarga automática (apenas para desenvolvimento)"
    )
    
    return parser.parse_args()

def run_server(args):
    """
    Executa o servidor usando Gunicorn com workers Uvicorn
    """
    # Construir comando
    cmd = [
        "gunicorn",
        "app.main:app",
        f"--bind={args.host}:{args.port}",
        f"--workers={args.workers}",
        "--worker-class=uvicorn.workers.UvicornWorker",
        "--timeout=120",
        "--graceful-timeout=30",
        "--keep-alive=5",
        "--log-level=info",
        "--access-logfile=-",
        "--error-logfile=-"
    ]
    
    # Adicionar opção de reload se solicitado
    if args.reload:
        cmd.append("--reload")
        print("AVISO: Modo de recarga ativado. Não use em produção!")
    
    # Imprimir informações
    print(f"Iniciando servidor em {args.host}:{args.port} com {args.workers} workers")
    
    try:
        # Executar comando
        process = subprocess.Popen(cmd)
        
        # Configurar manipulador de sinal para encaminhar sinais ao processo
        def signal_handler(sig, frame):
            if process.poll() is None:  # Se o processo ainda estiver em execução
                process.send_signal(sig)
            else:
                sys.exit(0)
        
        # Registrar manipuladores de sinal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Aguardar processo
        process.wait()
        
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
        if process.poll() is None:  # Se o processo ainda estiver em execução
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        sys.exit(0)
    except Exception as e:
        print(f"Erro ao executar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar se estamos no diretório correto
    if not os.path.exists("app/main.py"):
        print("Erro: Este script deve ser executado do diretório 'backend'")
        sys.exit(1)
    
    # Verificar se Gunicorn está instalado
    try:
        subprocess.run(["gunicorn", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Erro: Gunicorn não está instalado. Execute 'pip install gunicorn'")
        sys.exit(1)
    
    # Executar servidor
    args = parse_arguments()
    run_server(args)