import psutil
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from .config import atm_config
from .logger import atm_logger
from .notifications import notification_manager
from ..models import Session as SessionModel

class HealthMonitor:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.logger = atm_logger
        self.notifications = notification_manager
        self.last_check = datetime.utcnow()
        self.health_status = {
            'system': 'healthy',
            'database': 'healthy',
            'network': 'healthy',
            'hardware': 'healthy',
            'last_check': self.last_check.isoformat()
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Verifica saúde geral do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            
            # Rede
            network_status = self._check_network_connectivity()
            
            # Database
            db_status = self._check_database_health()
            
            # Hardware
            hardware_status = self._check_hardware_status()
            
            health_data = {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'status': 'healthy' if cpu_percent < 80 else 'warning'
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'available_gb': round(memory_available, 2),
                    'status': 'healthy' if memory_percent < 85 else 'warning'
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'free_gb': round(disk_free, 2),
                    'status': 'healthy' if disk_percent < 90 else 'warning'
                },
                'network': network_status,
                'database': db_status,
                'hardware': hardware_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Determinar status geral
            overall_status = 'healthy'
            if any(component['status'] == 'error' for component in health_data.values() if isinstance(component, dict) and 'status' in component):
                overall_status = 'error'
            elif any(component['status'] == 'warning' for component in health_data.values() if isinstance(component, dict) and 'status' in component):
                overall_status = 'warning'
            
            health_data['overall_status'] = overall_status
            
            # Log e notificações
            self._handle_health_alerts(health_data)
            
            return health_data
            
        except Exception as e:
            self.logger.log_system('monitoring', 'health_check_error', {'error': str(e)})
            return {'error': str(e), 'overall_status': 'error'}
    
    def _check_network_connectivity(self) -> Dict[str, Any]:
        """Verifica conectividade de rede"""
        try:
            # Testar conectividade com Binance (para cotação)
            binance_response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            binance_status = 'healthy' if binance_response.status_code == 200 else 'error'
            
            # Testar conectividade geral
            google_response = requests.get('https://www.google.com', timeout=5)
            general_status = 'healthy' if google_response.status_code == 200 else 'error'
            
            return {
                'binance_api': binance_status,
                'general_connectivity': general_status,
                'status': 'healthy' if binance_status == 'healthy' and general_status == 'healthy' else 'warning'
            }
            
        except Exception as e:
            return {
                'binance_api': 'error',
                'general_connectivity': 'error',
                'status': 'error',
                'error': str(e)
            }
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Verifica saúde do banco de dados"""
        try:
            db = self.db_session_factory()
            
            # Testar conexão
            db.execute("SELECT 1")
            
            # Verificar sessões ativas
            active_sessions = db.query(SessionModel).filter(
                SessionModel.expires_at > datetime.utcnow()
            ).count()
            
            # Verificar sessões expiradas
            expired_sessions = db.query(SessionModel).filter(
                SessionModel.expires_at <= datetime.utcnow()
            ).count()
            
            db.close()
            
            return {
                'connection': 'healthy',
                'active_sessions': active_sessions,
                'expired_sessions': expired_sessions,
                'status': 'healthy'
            }
            
        except Exception as e:
            return {
                'connection': 'error',
                'error': str(e),
                'status': 'error'
            }
    
    def _check_hardware_status(self) -> Dict[str, Any]:
        """Verifica status do hardware (simulado)"""
        try:
            # Simular verificação de hardware
            # Em um ATM real, aqui verificaria impressoras, câmeras, etc.
            
            hardware_status = {
                'printer': 'healthy' if atm_config.get('hardware.printer_enabled') else 'disabled',
                'camera': 'healthy' if atm_config.get('hardware.camera_enabled') else 'disabled',
                'touchscreen': 'healthy' if atm_config.get('hardware.touchscreen_enabled') else 'disabled',
                'maintenance_mode': atm_config.is_maintenance_mode()
            }
            
            # Determinar status geral do hardware
            if hardware_status['maintenance_mode']:
                overall_status = 'maintenance'
            elif any(status == 'error' for status in hardware_status.values() if status != 'maintenance'):
                overall_status = 'error'
            elif any(status == 'disabled' for status in hardware_status.values() if status != 'maintenance'):
                overall_status = 'warning'
            else:
                overall_status = 'healthy'
            
            hardware_status['status'] = overall_status
            return hardware_status
            
        except Exception as e:
            return {
                'printer': 'error',
                'camera': 'error',
                'touchscreen': 'error',
                'status': 'error',
                'error': str(e)
            }
    
    def _handle_health_alerts(self, health_data: Dict[str, Any]):
        """Processa alertas baseados no status de saúde"""
        previous_status = self.health_status.get('overall_status', 'healthy')
        current_status = health_data.get('overall_status', 'healthy')
        
        # Log do status
        self.logger.log_system('monitoring', 'health_check', {
            'overall_status': current_status,
            'components': health_data
        })
        
        # Alertas de mudança de status
        if current_status != previous_status:
            if current_status == 'error':
                self.notifications.notify_maintenance_required(
                    'system',
                    f'Status do sistema mudou para ERROR. Anterior: {previous_status}'
                )
            elif current_status == 'warning':
                self.logger.log_system('monitoring', 'health_warning', {
                    'previous_status': previous_status,
                    'current_status': current_status
                })
        
        # Alertas específicos por componente
        for component, data in health_data.items():
            if isinstance(data, dict) and 'status' in data:
                if data['status'] == 'error':
                    self.notifications.notify_maintenance_required(
                        component,
                        f'Componente {component} com status ERROR'
                    )
        
        # Atualizar status anterior
        self.health_status = health_data
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do sistema"""
        try:
            # Métricas básicas
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de rede
            network_io = psutil.net_io_counters()
            
            # Métricas de transações (últimas 24h)
            db = self.db_session_factory()
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            daily_transactions = db.query(SessionModel).filter(
                SessionModel.created_at >= yesterday
            ).count()
            
            daily_amount = db.query(SessionModel).filter(
                SessionModel.created_at >= yesterday,
                SessionModel.status == 'pago'
            ).with_entities(
                db.func.sum(SessionModel.amount_ars)
            ).scalar() or 0
            
            db.close()
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'network_bytes_sent': network_io.bytes_sent,
                'network_bytes_recv': network_io.bytes_recv,
                'daily_transactions': daily_transactions,
                'daily_amount': daily_amount,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.log_system('monitoring', 'metrics_error', {'error': str(e)})
            return {'error': str(e)}
    
    def check_daily_limits(self) -> Dict[str, Any]:
        """Verifica limites diários de transações"""
        try:
            db = self.db_session_factory()
            today = datetime.utcnow().date()
            
            # Transações de hoje
            today_transactions = db.query(SessionModel).filter(
                db.func.date(SessionModel.created_at) == today
            ).count()
            
            # Valor total de hoje
            today_amount = db.query(SessionModel).filter(
                db.func.date(SessionModel.created_at) == today,
                SessionModel.status == 'pago'
            ).with_entities(
                db.func.sum(SessionModel.amount_ars)
            ).scalar() or 0
            
            db.close()
            
            # Limites configurados
            limits = atm_config.get_security_settings()
            max_transactions = limits['max_daily_transactions']
            max_amount = limits['max_daily_amount']
            
            return {
                'today_transactions': today_transactions,
                'today_amount': today_amount,
                'max_transactions': max_transactions,
                'max_amount': max_amount,
                'transactions_remaining': max_transactions - today_transactions,
                'amount_remaining': max_amount - today_amount,
                'transactions_limit_reached': today_transactions >= max_transactions,
                'amount_limit_reached': today_amount >= max_amount
            }
            
        except Exception as e:
            self.logger.log_system('monitoring', 'limits_check_error', {'error': str(e)})
            return {'error': str(e)}

# Instância global do monitor (será inicializada no main.py)
health_monitor = None 