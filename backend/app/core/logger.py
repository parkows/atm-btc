import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os

class ATMLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar diferentes tipos de log
        self.setup_loggers()
    
    def setup_loggers(self):
        """Configura diferentes loggers para diferentes propósitos"""
        
        # Logger principal para transações
        self.transaction_logger = self._setup_logger(
            'transactions',
            'transaction.log',
            logging.INFO
        )
        
        # Logger para auditoria
        self.audit_logger = self._setup_logger(
            'audit',
            'audit.log',
            logging.INFO
        )
        
        # Logger para sistema
        self.system_logger = self._setup_logger(
            'system',
            'system.log',
            logging.INFO
        )
        
        # Logger para segurança
        self.security_logger = self._setup_logger(
            'security',
            'security.log',
            logging.WARNING
        )
    
    def _setup_logger(self, name: str, filename: str, level: int) -> logging.Logger:
        """Configura um logger específico"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Evitar duplicação de handlers
        if logger.handlers:
            return logger
        
        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_dir / filename)
        file_handler.setLevel(level)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def log_transaction(self, session_code: str, action: str, details: Dict[str, Any]):
        """Log de transações financeiras"""
        log_entry = {
            'session_code': session_code,
            'action': action,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.transaction_logger.info(json.dumps(log_entry))
    
    def log_audit(self, user_id: str, action: str, resource: str, details: Dict[str, Any]):
        """Log de auditoria para compliance"""
        log_entry = {
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.audit_logger.info(json.dumps(log_entry))
    
    def log_system(self, component: str, event: str, details: Dict[str, Any]):
        """Log de eventos do sistema"""
        log_entry = {
            'component': component,
            'event': event,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.system_logger.info(json.dumps(log_entry))
    
    def log_security(self, event: str, severity: str, details: Dict[str, Any]):
        """Log de eventos de segurança"""
        log_entry = {
            'event': event,
            'severity': severity,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.security_logger.warning(json.dumps(log_entry))
    
    def log_error(self, component: str, error_type: str, details: Dict[str, Any]):
        """Log de erros do sistema"""
        log_entry = {
            'component': component,
            'error_type': error_type,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.system_logger.error(json.dumps(log_entry))

# Instância global do logger
atm_logger = ATMLogger() 