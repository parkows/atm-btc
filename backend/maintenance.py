#!/usr/bin/env python3
"""
Script de Manutenção - LiquidGold ATM
Fornece comandos para tarefas de manutenção do sistema
"""

import argparse
import asyncio
import os
import sys
import json
from datetime import datetime

# Adicionar diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar após ajustar o path
from app.core.logger import atm_logger
from app.deps import get_db_session
from app.db.init_db import init_db

async def run_db_init():
    """
    Inicializa o banco de dados
    """
    try:
        print("Inicializando banco de dados...")
        async with get_db_session() as db:
            await init_db(db)
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        sys.exit(1)

async def run_backup(backup_type="manual"):
    """
    Executa um backup do sistema
    """
    try:
        from app.core.backup_manager import backup_manager
        
        print(f"Executando backup do tipo '{backup_type}'...")
        result = backup_manager.create_backup(backup_type)
        
        if result["success"]:
            print(f"Backup criado com sucesso: {result['backup_path']}")
        else:
            print(f"Erro ao criar backup: {result.get('error', 'Erro desconhecido')}")
            sys.exit(1)
    except Exception as e:
        print(f"Erro ao executar backup: {e}")
        sys.exit(1)

async def run_restore(backup_path):
    """
    Restaura um backup do sistema
    """
    try:
        from app.core.backup_manager import backup_manager
        
        # Verificar se o arquivo existe
        if not os.path.exists(backup_path):
            print(f"Erro: Arquivo de backup não encontrado: {backup_path}")
            sys.exit(1)
        
        print(f"Restaurando backup de {backup_path}...")
        print("ATENÇÃO: Esta operação substituirá dados existentes!")
        confirmation = input("Digite 'CONFIRMAR' para continuar: ")
        
        if confirmation != "CONFIRMAR":
            print("Operação cancelada.")
            sys.exit(0)
        
        result = backup_manager.restore_backup(backup_path)
        
        if result["success"]:
            print("Backup restaurado com sucesso!")
        else:
            print(f"Erro ao restaurar backup: {result.get('error', 'Erro desconhecido')}")
            sys.exit(1)
    except Exception as e:
        print(f"Erro ao restaurar backup: {e}")
        sys.exit(1)

async def run_cleanup():
    """
    Remove backups antigos conforme política de retenção
    """
    try:
        from app.core.backup_manager import backup_manager
        
        print("Removendo backups antigos...")
        result = backup_manager.cleanup_old_backups()
        
        if result["success"]:
            print(f"Limpeza concluída. Backups removidos: {result['removed_count']}")
        else:
            print(f"Erro na limpeza: {result.get('error', 'Erro desconhecido')}")
            sys.exit(1)
    except Exception as e:
        print(f"Erro ao limpar backups: {e}")
        sys.exit(1)

async def run_report(report_type="daily", date=None):
    """
    Gera um relatório do sistema
    """
    try:
        from app.core.reports import ReportGenerator
        
        # Usar data atual se não especificada
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"Gerando relatório {report_type} para {date}...")
        
        # Criar gerador de relatórios
        report_generator = ReportGenerator()
        
        # Gerar relatório conforme tipo
        if report_type == "daily":
            report = await report_generator.generate_daily_report(date)
        elif report_type == "weekly":
            report = await report_generator.generate_weekly_report(date)
        elif report_type == "performance":
            report = await report_generator.generate_performance_report(date)
        else:
            print(f"Tipo de relatório inválido: {report_type}")
            sys.exit(1)
        
        # Salvar relatório em arquivo
        output_file = f"{report_type}_report_{date}.json"
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"Relatório gerado com sucesso: {output_file}")
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        sys.exit(1)

async def run_maintenance_mode(enable=True):
    """
    Ativa ou desativa o modo de manutenção
    """
    try:
        from app.core.config import atm_config
        
        action = "ativando" if enable else "desativando"
        print(f"{action} modo de manutenção...")
        
        # Atualizar configuração
        config = atm_config.get_all()
        config["maintenance_mode"] = enable
        atm_config.update(config)
        
        status = "ativado" if enable else "desativado"
        print(f"Modo de manutenção {status} com sucesso!")
    except Exception as e:
        print(f"Erro ao alterar modo de manutenção: {e}")
        sys.exit(1)

def main():
    """
    Função principal que processa argumentos e executa comandos
    """
    parser = argparse.ArgumentParser(description="Ferramenta de manutenção do LiquidGold ATM")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    
    # Comando: init-db
    subparsers.add_parser("init-db", help="Inicializa o banco de dados")
    
    # Comando: backup
    backup_parser = subparsers.add_parser("backup", help="Cria um backup do sistema")
    backup_parser.add_argument(
        "--type", 
        choices=["daily", "weekly", "monthly", "manual"],
        default="manual",
        help="Tipo de backup a criar"
    )
    
    # Comando: restore
    restore_parser = subparsers.add_parser("restore", help="Restaura um backup do sistema")
    restore_parser.add_argument(
        "backup_path", 
        help="Caminho para o arquivo de backup a restaurar"
    )
    
    # Comando: cleanup
    subparsers.add_parser("cleanup", help="Remove backups antigos conforme política de retenção")
    
    # Comando: report
    report_parser = subparsers.add_parser("report", help="Gera um relatório do sistema")
    report_parser.add_argument(
        "--type", 
        choices=["daily", "weekly", "performance"],
        default="daily",
        help="Tipo de relatório a gerar"
    )
    report_parser.add_argument(
        "--date", 
        help="Data para o relatório (formato YYYY-MM-DD)"
    )
    
    # Comando: maintenance
    maintenance_parser = subparsers.add_parser("maintenance", help="Controla o modo de manutenção")
    maintenance_parser.add_argument(
        "action", 
        choices=["on", "off"],
        help="Ativar ou desativar modo de manutenção"
    )
    
    # Processar argumentos
    args = parser.parse_args()
    
    # Verificar se um comando foi especificado
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Executar comando apropriado
    if args.command == "init-db":
        asyncio.run(run_db_init())
    elif args.command == "backup":
        asyncio.run(run_backup(args.type))
    elif args.command == "restore":
        asyncio.run(run_restore(args.backup_path))
    elif args.command == "cleanup":
        asyncio.run(run_cleanup())
    elif args.command == "report":
        asyncio.run(run_report(args.type, args.date))
    elif args.command == "maintenance":
        asyncio.run(run_maintenance_mode(args.action == "on"))

if __name__ == "__main__":
    main()