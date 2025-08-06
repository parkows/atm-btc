#!/usr/bin/env python3
"""
Sistema de Backup - LiquidGold ATM
Implementação de backup automático para segurança e recuperação de dados
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import shutil
import json
import threading
import time
import sqlite3
import subprocess
import gzip

from app.core.logger import atm_logger
from app.core.config import atm_config

class BackupManager:
    """
    Gerenciador de backup automático para segurança e recuperação de dados
    """
    
    def __init__(self):
        self.logger = atm_logger
        self.config = atm_config
        
        # Configurações padrão
        self.backup_dir = os.path.abspath("backups")
        self.db_path = os.path.abspath("liquidgold_atm.db")
        self.config_dir = os.path.abspath("config")
        self.logs_dir = os.path.abspath("logs")
        
        # Configurações de retenção
        self.daily_retention = 7    # Manter backups diários por 7 dias
        self.weekly_retention = 4    # Manter backups semanais por 4 semanas
        self.monthly_retention = 3   # Manter backups mensais por 3 meses
        
        # Carregar configurações
        self._load_config()
        
        # Criar diretório de backup se não existir
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "daily"), exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "weekly"), exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "monthly"), exist_ok=True)
        
        # Iniciar thread de backup
        self._start_backup_thread()
    
    def _load_config(self):
        """
        Carrega configurações de backup do arquivo de configuração
        """
        try:
            backup_config = self.config.get("backup")
            if backup_config:
                if "backup_dir" in backup_config:
                    self.backup_dir = os.path.abspath(backup_config["backup_dir"])
                if "db_path" in backup_config:
                    self.db_path = os.path.abspath(backup_config["db_path"])
                if "config_dir" in backup_config:
                    self.config_dir = os.path.abspath(backup_config["config_dir"])
                if "logs_dir" in backup_config:
                    self.logs_dir = os.path.abspath(backup_config["logs_dir"])
                
                # Configurações de retenção
                if "daily_retention" in backup_config:
                    self.daily_retention = backup_config["daily_retention"]
                if "weekly_retention" in backup_config:
                    self.weekly_retention = backup_config["weekly_retention"]
                if "monthly_retention" in backup_config:
                    self.monthly_retention = backup_config["monthly_retention"]
        except Exception as e:
            self.logger.log_error('backup', 'config_load_error', {'error': str(e)})
    
    def _start_backup_thread(self):
        """
        Inicia thread para execução de backups automáticos
        """
        def backup_task():
            while True:
                try:
                    # Verificar se é hora de fazer backup
                    now = datetime.now()
                    
                    # Backup diário às 3:00 da manhã
                    if now.hour == 3 and now.minute < 15:
                        self.create_backup("daily")
                        
                        # Backup semanal aos domingos
                        if now.weekday() == 6:  # 0 = Segunda, 6 = Domingo
                            self.create_backup("weekly")
                            
                            # Backup mensal no primeiro domingo do mês
                            if now.day <= 7:
                                self.create_backup("monthly")
                        
                        # Limpar backups antigos
                        self.cleanup_old_backups()
                        
                        # Aguardar 20 minutos para evitar execução duplicada
                        time.sleep(1200)
                    else:
                        # Verificar a cada 5 minutos
                        time.sleep(300)
                        
                except Exception as e:
                    self.logger.log_error('backup', 'backup_thread_error', {'error': str(e)})
                    time.sleep(600)  # Aguardar 10 minutos em caso de erro
        
        # Iniciar thread
        backup_thread = threading.Thread(target=backup_task, daemon=True)
        backup_thread.start()
    
    def create_backup(self, backup_type: str = "daily") -> Dict[str, Any]:
        """
        Cria um backup do sistema
        """
        try:
            # Verificar tipo de backup
            if backup_type not in ["daily", "weekly", "monthly", "manual"]:
                backup_type = "manual"
            
            # Criar nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"liquidgold_atm_{backup_type}_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_type, backup_filename)
            
            # Criar diretório para este backup
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup do banco de dados
            db_backup_result = self._backup_database(backup_path)
            
            # Backup das configurações
            config_backup_result = self._backup_configs(backup_path)
            
            # Backup dos logs
            logs_backup_result = self._backup_logs(backup_path)
            
            # Criar arquivo de metadados
            metadata = {
                "timestamp": timestamp,
                "type": backup_type,
                "database": db_backup_result,
                "configs": config_backup_result,
                "logs": logs_backup_result,
                "version": "1.0.0"
            }
            
            with open(os.path.join(backup_path, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Comprimir o backup
            backup_zip = f"{backup_path}.zip"
            shutil.make_archive(backup_path, 'zip', backup_path)
            
            # Remover diretório temporário
            shutil.rmtree(backup_path)
            
            # Registrar sucesso
            self.logger.log_system('backup', 'backup_created', {
                'type': backup_type,
                'filename': backup_zip,
                'size_bytes': os.path.getsize(backup_zip)
            })
            
            return {
                "success": True,
                "type": backup_type,
                "filename": backup_zip,
                "timestamp": timestamp,
                "size_bytes": os.path.getsize(backup_zip)
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.log_error('backup', 'backup_creation_error', {'error': error_msg})
            
            return {
                "success": False,
                "type": backup_type,
                "error": error_msg
            }
    
    def _backup_database(self, backup_path: str) -> Dict[str, Any]:
        """
        Cria backup do banco de dados
        """
        try:
            # Verificar se o banco de dados existe
            if not os.path.exists(self.db_path):
                return {"success": False, "error": "Database file not found"}
            
            # Nome do arquivo de backup
            db_backup_file = os.path.join(backup_path, "database.sql.gz")
            
            # Para SQLite, usar dump para SQL
            if self.db_path.endswith(".db"):
                # Conectar ao banco de dados
                conn = sqlite3.connect(self.db_path)
                
                # Abrir arquivo de backup comprimido
                with gzip.open(db_backup_file, 'wt') as f:
                    # Dump do esquema
                    for line in conn.iterdump():
                        f.write(f"{line}\n")
                
                conn.close()
            # Para PostgreSQL, usar pg_dump
            elif os.environ.get("DATABASE_URL", "").startswith("postgresql"):
                # Extrair informações de conexão da URL
                db_url = os.environ.get("DATABASE_URL", "")
                
                # Executar pg_dump e comprimir
                with open(db_backup_file, 'wb') as f:
                    pg_dump_process = subprocess.Popen(
                        ["pg_dump", db_url, "--format=c"],
                        stdout=subprocess.PIPE
                    )
                    
                    # Comprimir a saída
                    with gzip.GzipFile(fileobj=f, mode='wb') as gzf:
                        shutil.copyfileobj(pg_dump_process.stdout, gzf)
                    
                    pg_dump_process.stdout.close()
                    return_code = pg_dump_process.wait()
                    
                    if return_code != 0:
                        return {"success": False, "error": f"pg_dump failed with code {return_code}"}
            else:
                return {"success": False, "error": "Unsupported database type"}
            
            return {
                "success": True,
                "file": db_backup_file,
                "size_bytes": os.path.getsize(db_backup_file)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _backup_configs(self, backup_path: str) -> Dict[str, Any]:
        """
        Cria backup dos arquivos de configuração
        """
        try:
            # Verificar se o diretório de configuração existe
            if not os.path.exists(self.config_dir):
                return {"success": False, "error": "Config directory not found"}
            
            # Criar diretório para configurações
            config_backup_dir = os.path.join(backup_path, "config")
            os.makedirs(config_backup_dir, exist_ok=True)
            
            # Copiar arquivos de configuração
            files_copied = 0
            for root, _, files in os.walk(self.config_dir):
                for file in files:
                    if file.endswith(".json") or file.endswith(".yaml") or file.endswith(".yml"):
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, self.config_dir)
                        dst_file = os.path.join(config_backup_dir, rel_path)
                        
                        # Criar diretório de destino se não existir
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        
                        # Copiar arquivo
                        shutil.copy2(src_file, dst_file)
                        files_copied += 1
            
            return {
                "success": True,
                "files_copied": files_copied,
                "directory": config_backup_dir
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _backup_logs(self, backup_path: str) -> Dict[str, Any]:
        """
        Cria backup dos arquivos de log
        """
        try:
            # Verificar se o diretório de logs existe
            if not os.path.exists(self.logs_dir):
                return {"success": False, "error": "Logs directory not found"}
            
            # Criar diretório para logs
            logs_backup_dir = os.path.join(backup_path, "logs")
            os.makedirs(logs_backup_dir, exist_ok=True)
            
            # Copiar arquivos de log
            files_copied = 0
            for root, _, files in os.walk(self.logs_dir):
                for file in files:
                    if file.endswith(".log") or file.endswith(".json"):
                        src_file = os.path.join(root, file)
                        rel_path = os.path.relpath(src_file, self.logs_dir)
                        dst_file = os.path.join(logs_backup_dir, rel_path)
                        
                        # Criar diretório de destino se não existir
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        
                        # Copiar arquivo
                        shutil.copy2(src_file, dst_file)
                        files_copied += 1
            
            return {
                "success": True,
                "files_copied": files_copied,
                "directory": logs_backup_dir
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """
        Remove backups antigos conforme política de retenção
        """
        try:
            removed_files = {
                "daily": 0,
                "weekly": 0,
                "monthly": 0
            }
            
            # Limpar backups diários
            daily_dir = os.path.join(self.backup_dir, "daily")
            if os.path.exists(daily_dir):
                removed_files["daily"] = self._cleanup_directory(
                    daily_dir, self.daily_retention)
            
            # Limpar backups semanais
            weekly_dir = os.path.join(self.backup_dir, "weekly")
            if os.path.exists(weekly_dir):
                removed_files["weekly"] = self._cleanup_directory(
                    weekly_dir, self.weekly_retention)
            
            # Limpar backups mensais
            monthly_dir = os.path.join(self.backup_dir, "monthly")
            if os.path.exists(monthly_dir):
                removed_files["monthly"] = self._cleanup_directory(
                    monthly_dir, self.monthly_retention)
            
            # Registrar limpeza
            self.logger.log_system('backup', 'old_backups_cleaned', {
                'removed': removed_files
            })
            
            return {
                "success": True,
                "removed_files": removed_files
            }
            
        except Exception as e:
            self.logger.log_error('backup', 'cleanup_error', {'error': str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _cleanup_directory(self, directory: str, keep_count: int) -> int:
        """
        Remove arquivos mais antigos em um diretório, mantendo apenas os mais recentes
        """
        try:
            # Listar arquivos zip no diretório
            files = [f for f in os.listdir(directory) if f.endswith(".zip")]
            
            # Ordenar por data de modificação (mais antigos primeiro)
            files.sort(key=lambda f: os.path.getmtime(os.path.join(directory, f)))
            
            # Determinar quantos arquivos remover
            files_to_remove = files[:-keep_count] if len(files) > keep_count else []
            
            # Remover arquivos
            for file in files_to_remove:
                os.remove(os.path.join(directory, file))
            
            return len(files_to_remove)
            
        except Exception as e:
            self.logger.log_error('backup', 'directory_cleanup_error', {
                'directory': directory,
                'error': str(e)
            })
            return 0
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista backups disponíveis
        """
        try:
            backups = []
            
            # Determinar diretórios a verificar
            if backup_type in ["daily", "weekly", "monthly"]:
                dirs_to_check = [os.path.join(self.backup_dir, backup_type)]
            else:
                dirs_to_check = [
                    os.path.join(self.backup_dir, "daily"),
                    os.path.join(self.backup_dir, "weekly"),
                    os.path.join(self.backup_dir, "monthly")
                ]
            
            # Listar backups em cada diretório
            for directory in dirs_to_check:
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        if file.endswith(".zip"):
                            file_path = os.path.join(directory, file)
                            file_type = os.path.basename(directory)
                            
                            # Extrair timestamp do nome do arquivo
                            parts = file.split("_")
                            if len(parts) >= 4:
                                timestamp = f"{parts[-2]}_{parts[-1].replace('.zip', '')}"
                            else:
                                timestamp = "unknown"
                            
                            backups.append({
                                "filename": file,
                                "path": file_path,
                                "type": file_type,
                                "timestamp": timestamp,
                                "size_bytes": os.path.getsize(file_path),
                                "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                            })
            
            # Ordenar por data de criação (mais recentes primeiro)
            backups.sort(key=lambda b: b["created_at"], reverse=True)
            
            return backups
            
        except Exception as e:
            self.logger.log_error('backup', 'list_backups_error', {'error': str(e)})
            return []
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        Restaura um backup
        ATENÇÃO: Esta função deve ser usada com cuidado, pois substitui dados existentes
        """
        try:
            # Verificar se o arquivo de backup existe
            if not os.path.exists(backup_path) or not backup_path.endswith(".zip"):
                return {"success": False, "error": "Invalid backup file"}
            
            # Criar diretório temporário para extração
            temp_dir = os.path.join(self.backup_dir, "temp_restore")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extrair backup
            shutil.unpack_archive(backup_path, temp_dir, 'zip')
            
            # Verificar metadados
            metadata_file = os.path.join(temp_dir, "metadata.json")
            if not os.path.exists(metadata_file):
                shutil.rmtree(temp_dir)
                return {"success": False, "error": "Invalid backup: metadata.json not found"}
            
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            
            # Restaurar banco de dados
            db_result = self._restore_database(temp_dir, metadata)
            
            # Restaurar configurações
            config_result = self._restore_configs(temp_dir, metadata)
            
            # Não restaurar logs, apenas manter os atuais
            
            # Limpar diretório temporário
            shutil.rmtree(temp_dir)
            
            # Registrar restauração
            self.logger.log_system('backup', 'backup_restored', {
                'backup_file': backup_path,
                'database_restored': db_result["success"],
                'configs_restored': config_result["success"]
            })
            
            return {
                "success": db_result["success"] and config_result["success"],
                "database": db_result,
                "configs": config_result,
                "timestamp": metadata.get("timestamp", "unknown")
            }
            
        except Exception as e:
            self.logger.log_error('backup', 'restore_error', {'error': str(e)})
            
            # Limpar diretório temporário em caso de erro
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _restore_database(self, temp_dir: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restaura o banco de dados a partir do backup
        """
        try:
            # Verificar se o backup do banco de dados existe
            db_backup_file = os.path.join(temp_dir, "database.sql.gz")
            if not os.path.exists(db_backup_file):
                return {"success": False, "error": "Database backup file not found"}
            
            # Criar backup do banco de dados atual antes de restaurar
            current_db_backup = f"{self.db_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, current_db_backup)
            
            # Para SQLite
            if self.db_path.endswith(".db"):
                # Remover banco de dados atual
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
                
                # Criar novo banco de dados
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Executar script SQL do backup
                with gzip.open(db_backup_file, 'rt') as f:
                    sql_script = f.read()
                    cursor.executescript(sql_script)
                
                conn.commit()
                conn.close()
                
            # Para PostgreSQL
            elif os.environ.get("DATABASE_URL", "").startswith("postgresql"):
                # Extrair informações de conexão da URL
                db_url = os.environ.get("DATABASE_URL", "")
                
                # Descomprimir o arquivo
                temp_sql_file = os.path.join(temp_dir, "database.sql")
                with gzip.open(db_backup_file, 'rb') as f_in:
                    with open(temp_sql_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Restaurar usando psql
                restore_process = subprocess.Popen(
                    ["psql", db_url, "-f", temp_sql_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                _, stderr = restore_process.communicate()
                return_code = restore_process.returncode
                
                # Remover arquivo temporário
                os.remove(temp_sql_file)
                
                if return_code != 0:
                    return {"success": False, "error": f"psql failed: {stderr.decode()}"}
            else:
                return {"success": False, "error": "Unsupported database type"}
            
            return {
                "success": True,
                "backup_created": current_db_backup
            }
            
        except Exception as e:
            # Tentar restaurar o backup original em caso de erro
            if os.path.exists(current_db_backup) and os.path.exists(self.db_path):
                os.remove(self.db_path)
                shutil.copy2(current_db_backup, self.db_path)
            
            return {"success": False, "error": str(e)}
    
    def _restore_configs(self, temp_dir: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restaura os arquivos de configuração a partir do backup
        """
        try:
            # Verificar se o diretório de configuração existe no backup
            config_backup_dir = os.path.join(temp_dir, "config")
            if not os.path.exists(config_backup_dir):
                return {"success": False, "error": "Config directory not found in backup"}
            
            # Criar backup das configurações atuais
            current_config_backup = f"{self.config_dir}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.config_dir):
                shutil.copytree(self.config_dir, current_config_backup)
            
            # Copiar arquivos de configuração do backup
            files_copied = 0
            for root, _, files in os.walk(config_backup_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    rel_path = os.path.relpath(src_file, config_backup_dir)
                    dst_file = os.path.join(self.config_dir, rel_path)
                    
                    # Criar diretório de destino se não existir
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    
                    # Copiar arquivo
                    shutil.copy2(src_file, dst_file)
                    files_copied += 1
            
            return {
                "success": True,
                "files_copied": files_copied,
                "backup_created": current_config_backup
            }
            
        except Exception as e:
            # Tentar restaurar o backup original em caso de erro
            if os.path.exists(current_config_backup):
                shutil.rmtree(self.config_dir, ignore_errors=True)
                shutil.copytree(current_config_backup, self.config_dir)
            
            return {"success": False, "error": str(e)}

# Instância global
backup_manager = BackupManager()