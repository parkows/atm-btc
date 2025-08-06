#!/usr/bin/env python3
"""
Sistema de Auditoria - LiquidGold ATM
Implementação de auditoria para rastreabilidade e segurança
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os
import threading
import time
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.logger import atm_logger
from app.core.config import atm_config
from app.deps import get_db_session_factory

# Base para modelos SQLAlchemy
Base = declarative_base()

class AuditLog(Base):
    """
    Modelo para registro de auditoria
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String(50), index=True, nullable=True)
    action = Column(String(100), index=True)
    resource = Column(String(100), index=True)
    resource_id = Column(String(100), index=True, nullable=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    status = Column(String(20), index=True)  # success, failure, warning

class AuditManager:
    """
    Gerenciador de auditoria para rastreabilidade e segurança
    """
    
    def __init__(self):
        self.logger = atm_logger
        self.config = atm_config
        
        # Obter session factory do banco de dados
        self.db_session_factory = get_db_session_factory()
        
        # Verificar se a tabela existe e criar se necessário
        self._ensure_table_exists()
        
        # Fila de eventos para processamento assíncrono
        self.event_queue = []
        self.queue_lock = threading.Lock()
        
        # Iniciar thread de processamento
        self._start_processing_thread()
    
    def _ensure_table_exists(self):
        """
        Verifica se a tabela de auditoria existe e cria se necessário
        """
        try:
            engine = self.db_session_factory.kw['bind']
            inspector = inspect(engine)
            
            if not inspector.has_table(AuditLog.__tablename__):
                Base.metadata.create_all(bind=engine)
                self.logger.log_system('audit', 'table_created', {
                    'table': AuditLog.__tablename__
                })
        except Exception as e:
            self.logger.log_error('audit', 'table_creation_error', {'error': str(e)})
    
    def _start_processing_thread(self):
        """
        Inicia thread para processamento assíncrono de eventos de auditoria
        """
        def processing_task():
            while True:
                try:
                    # Processar eventos na fila
                    events_to_process = []
                    
                    with self.queue_lock:
                        if self.event_queue:
                            events_to_process = self.event_queue.copy()
                            self.event_queue.clear()
                    
                    if events_to_process:
                        self._process_events(events_to_process)
                        
                except Exception as e:
                    self.logger.log_error('audit', 'processing_error', {'error': str(e)})
                
                # Aguardar antes da próxima verificação
                time.sleep(5)  # Verificar a cada 5 segundos
        
        # Iniciar thread
        processing_thread = threading.Thread(target=processing_task, daemon=True)
        processing_thread.start()
    
    def _process_events(self, events: List[Dict[str, Any]]):
        """
        Processa eventos de auditoria em lote
        """
        if not events:
            return
        
        try:
            # Criar sessão do banco de dados
            db = self.db_session_factory()
            
            try:
                # Criar objetos AuditLog para cada evento
                audit_logs = []
                for event in events:
                    audit_log = AuditLog(
                        timestamp=event.get('timestamp', datetime.utcnow()),
                        user_id=event.get('user_id'),
                        action=event.get('action'),
                        resource=event.get('resource'),
                        resource_id=event.get('resource_id'),
                        ip_address=event.get('ip_address'),
                        details=json.dumps(event.get('details', {})) if event.get('details') else None,
                        status=event.get('status', 'success')
                    )
                    audit_logs.append(audit_log)
                
                # Adicionar ao banco de dados
                db.add_all(audit_logs)
                db.commit()
                
                # Log de sucesso
                self.logger.log_system('audit', 'events_processed', {
                    'count': len(audit_logs)
                })
                
            except Exception as e:
                db.rollback()
                raise e
            finally:
                db.close()
                
        except Exception as e:
            self.logger.log_error('audit', 'db_error', {'error': str(e)})
            
            # Em caso de erro, tentar salvar em arquivo
            self._save_to_file(events)
    
    def _save_to_file(self, events: List[Dict[str, Any]]):
        """
        Salva eventos em arquivo em caso de falha no banco de dados
        """
        try:
            # Garantir que o diretório existe
            os.makedirs('logs/audit', exist_ok=True)
            
            # Nome do arquivo com timestamp
            filename = f"logs/audit/audit_fallback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Salvar eventos em arquivo JSON
            with open(filename, 'w') as f:
                json.dump(events, f, default=str)
            
            self.logger.log_system('audit', 'saved_to_file', {
                'filename': filename,
                'count': len(events)
            })
            
        except Exception as e:
            self.logger.log_error('audit', 'file_save_error', {'error': str(e)})
    
    def log_event(self, action: str, resource: str, resource_id: Optional[str] = None, 
                 user_id: Optional[str] = None, ip_address: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None, status: str = "success"):
        """
        Registra evento de auditoria
        """
        event = {
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'resource_id': resource_id,
            'ip_address': ip_address,
            'details': details,
            'status': status
        }
        
        # Adicionar à fila para processamento assíncrono
        with self.queue_lock:
            self.event_queue.append(event)
    
    def get_logs(self, limit: int = 100, offset: int = 0, 
                filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtém logs de auditoria com filtros opcionais
        """
        try:
            # Criar sessão do banco de dados
            db = self.db_session_factory()
            
            try:
                # Construir query base
                query = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
                
                # Aplicar filtros
                if filters:
                    if 'user_id' in filters:
                        query = query.filter(AuditLog.user_id == filters['user_id'])
                    if 'action' in filters:
                        query = query.filter(AuditLog.action == filters['action'])
                    if 'resource' in filters:
                        query = query.filter(AuditLog.resource == filters['resource'])
                    if 'status' in filters:
                        query = query.filter(AuditLog.status == filters['status'])
                    if 'start_date' in filters and 'end_date' in filters:
                        query = query.filter(AuditLog.timestamp.between(
                            filters['start_date'], filters['end_date']))
                
                # Aplicar paginação
                query = query.limit(limit).offset(offset)
                
                # Executar query
                results = query.all()
                
                # Converter para dicionários
                logs = []
                for log in results:
                    log_dict = {
                        'id': log.id,
                        'timestamp': log.timestamp.isoformat(),
                        'user_id': log.user_id,
                        'action': log.action,
                        'resource': log.resource,
                        'resource_id': log.resource_id,
                        'ip_address': log.ip_address,
                        'status': log.status
                    }
                    
                    # Converter details de JSON para dict
                    if log.details:
                        try:
                            log_dict['details'] = json.loads(log.details)
                        except:
                            log_dict['details'] = log.details
                    else:
                        log_dict['details'] = {}
                    
                    logs.append(log_dict)
                
                return logs
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.log_error('audit', 'get_logs_error', {'error': str(e)})
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de auditoria
        """
        try:
            # Criar sessão do banco de dados
            db = self.db_session_factory()
            
            try:
                # Total de logs
                total_count = db.query(AuditLog).count()
                
                # Contagem por status
                success_count = db.query(AuditLog).filter(AuditLog.status == 'success').count()
                failure_count = db.query(AuditLog).filter(AuditLog.status == 'failure').count()
                warning_count = db.query(AuditLog).filter(AuditLog.status == 'warning').count()
                
                # Contagem por recurso (top 5)
                resource_counts = db.query(
                    AuditLog.resource, 
                    db.func.count(AuditLog.id).label('count')
                ).group_by(AuditLog.resource).order_by(db.func.count(AuditLog.id).desc()).limit(5).all()
                
                # Contagem por ação (top 5)
                action_counts = db.query(
                    AuditLog.action, 
                    db.func.count(AuditLog.id).label('count')
                ).group_by(AuditLog.action).order_by(db.func.count(AuditLog.id).desc()).limit(5).all()
                
                return {
                    'total_count': total_count,
                    'by_status': {
                        'success': success_count,
                        'failure': failure_count,
                        'warning': warning_count
                    },
                    'top_resources': [
                        {'resource': r[0], 'count': r[1]} for r in resource_counts
                    ],
                    'top_actions': [
                        {'action': a[0], 'count': a[1]} for a in action_counts
                    ]
                }
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.log_error('audit', 'get_statistics_error', {'error': str(e)})
            return {
                'total_count': 0,
                'by_status': {'success': 0, 'failure': 0, 'warning': 0},
                'top_resources': [],
                'top_actions': []
            }

# Instância global
audit_manager = AuditManager()