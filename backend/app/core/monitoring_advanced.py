#!/usr/bin/env python3
"""
Sistema de Monitoramento Avançado - LiquidGold ATM
Monitoramento em tempo real com métricas e alertas
"""

import time
import json
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
import psutil
import requests
from dataclasses import dataclass, asdict

from .config import atm_config
from .logger import atm_logger

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    active_connections: int
    requests_per_second: float
    error_rate: float
    response_time_avg: float
    uptime_seconds: float

@dataclass
class BusinessMetrics:
    """Métricas de negócio"""
    timestamp: datetime
    total_sessions: int
    btc_sessions: int
    usdt_sessions: int
    total_volume_ars: float
    btc_volume_ars: float
    usdt_volume_ars: float
    success_rate: float
    active_sessions: int
    completed_sessions: int
    failed_sessions: int

class AdvancedMonitoring:
    """Sistema de monitoramento avançado"""
    
    def __init__(self):
        self.config = atm_config
        self.logger = atm_logger
        
        # Métricas em tempo real
        self.system_metrics = deque(maxlen=1000)  # Últimas 1000 medições
        self.business_metrics = deque(maxlen=1000)
        
        # Alertas
        self.alerts = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'error_rate': 5.0,
            'response_time_ms': 1000.0,
            'success_rate': 95.0
        }
        
        # Contadores
        self.request_counter = 0
        self.error_counter = 0
        self.session_counter = defaultdict(int)
        self.volume_counter = defaultdict(float)
        
        # Thread de monitoramento
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Webhooks
        self.webhook_urls = []
        self.webhook_enabled = True
    
    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.log_system('monitoring', 'monitoring_started', {
            'timestamp': datetime.now().isoformat()
        })
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        self.logger.log_system('monitoring', 'monitoring_stopped', {
            'timestamp': datetime.now().isoformat()
        })
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.is_monitoring:
            try:
                # Coletar métricas do sistema
                system_metrics = self._collect_system_metrics()
                self.system_metrics.append(system_metrics)
                
                # Coletar métricas de negócio
                business_metrics = self._collect_business_metrics()
                self.business_metrics.append(business_metrics)
                
                # Verificar alertas
                self._check_alerts(system_metrics, business_metrics)
                
                # Enviar webhooks se necessário
                if self.webhook_enabled and self.webhook_urls:
                    self._send_webhooks(system_metrics, business_metrics)
                
                # Aguardar próximo ciclo
                time.sleep(self.config.get('monitoring.metrics_interval', 60))
                
            except Exception as e:
                self.logger.log_system('monitoring', 'monitoring_error', {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                time.sleep(10)  # Aguardar antes de tentar novamente
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Rede
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Conexões ativas
            active_connections = len(psutil.net_connections())
            
            # Métricas de aplicação
            requests_per_second = self._calculate_requests_per_second()
            error_rate = self._calculate_error_rate()
            response_time_avg = self._calculate_avg_response_time()
            
            # Uptime
            uptime_seconds = time.time() - psutil.boot_time()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                active_connections=active_connections,
                requests_per_second=requests_per_second,
                error_rate=error_rate,
                response_time_avg=response_time_avg,
                uptime_seconds=uptime_seconds
            )
            
        except Exception as e:
            self.logger.log_system('monitoring', 'system_metrics_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={},
                active_connections=0,
                requests_per_second=0.0,
                error_rate=0.0,
                response_time_avg=0.0,
                uptime_seconds=0.0
            )
    
    def _collect_business_metrics(self) -> BusinessMetrics:
        """Coleta métricas de negócio"""
        try:
            # Contadores de sessão
            total_sessions = sum(self.session_counter.values())
            btc_sessions = self.session_counter.get('BTC', 0)
            usdt_sessions = self.session_counter.get('USDT', 0)
            
            # Volumes
            total_volume = sum(self.volume_counter.values())
            btc_volume = self.volume_counter.get('BTC', 0.0)
            usdt_volume = self.volume_counter.get('USDT', 0.0)
            
            # Taxa de sucesso
            success_rate = 100.0 if self.request_counter == 0 else \
                ((self.request_counter - self.error_counter) / self.request_counter) * 100
            
            # Sessões ativas (simulação)
            active_sessions = len([m for m in self.business_metrics 
                                 if (datetime.now() - m.timestamp).seconds < 300])
            
            # Sessões completadas
            completed_sessions = total_sessions - active_sessions
            
            # Sessões falharam
            failed_sessions = self.error_counter
            
            return BusinessMetrics(
                timestamp=datetime.now(),
                total_sessions=total_sessions,
                btc_sessions=btc_sessions,
                usdt_sessions=usdt_sessions,
                total_volume_ars=total_volume,
                btc_volume_ars=btc_volume,
                usdt_volume_ars=usdt_volume,
                success_rate=success_rate,
                active_sessions=active_sessions,
                completed_sessions=completed_sessions,
                failed_sessions=failed_sessions
            )
            
        except Exception as e:
            self.logger.log_system('monitoring', 'business_metrics_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return BusinessMetrics(
                timestamp=datetime.now(),
                total_sessions=0,
                btc_sessions=0,
                usdt_sessions=0,
                total_volume_ars=0.0,
                btc_volume_ars=0.0,
                usdt_volume_ars=0.0,
                success_rate=0.0,
                active_sessions=0,
                completed_sessions=0,
                failed_sessions=0
            )
    
    def _calculate_requests_per_second(self) -> float:
        """Calcula requests por segundo"""
        if len(self.system_metrics) < 2:
            return 0.0
        
        # Últimas 2 medições
        recent_metrics = list(self.system_metrics)[-2:]
        if len(recent_metrics) < 2:
            return 0.0
        
        time_diff = (recent_metrics[1].timestamp - recent_metrics[0].timestamp).total_seconds()
        if time_diff == 0:
            return 0.0
        
        return self.request_counter / time_diff
    
    def _calculate_error_rate(self) -> float:
        """Calcula taxa de erro"""
        if self.request_counter == 0:
            return 0.0
        return (self.error_counter / self.request_counter) * 100
    
    def _calculate_avg_response_time(self) -> float:
        """Calcula tempo médio de resposta"""
        if not self.system_metrics:
            return 0.0
        
        recent_metrics = list(self.system_metrics)[-10:]  # Últimas 10 medições
        response_times = [m.response_time_avg for m in recent_metrics if m.response_time_avg > 0]
        
        if not response_times:
            return 0.0
        
        return sum(response_times) / len(response_times)
    
    def _check_alerts(self, system_metrics: SystemMetrics, business_metrics: BusinessMetrics):
        """Verifica e gera alertas"""
        alerts = []
        
        # Alertas do sistema
        if system_metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'system',
                'level': 'warning',
                'message': f'CPU usage high: {system_metrics.cpu_percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            })
        
        if system_metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'system',
                'level': 'warning',
                'message': f'Memory usage high: {system_metrics.memory_percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            })
        
        if system_metrics.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
            alerts.append({
                'type': 'system',
                'level': 'critical',
                'message': f'Disk usage critical: {system_metrics.disk_usage_percent:.1f}%',
                'timestamp': datetime.now().isoformat()
            })
        
        # Alertas de negócio
        if business_metrics.success_rate < self.alert_thresholds['success_rate']:
            alerts.append({
                'type': 'business',
                'level': 'critical',
                'message': f'Success rate low: {business_metrics.success_rate:.1f}%',
                'timestamp': datetime.now().isoformat()
            })
        
        if system_metrics.response_time_avg > self.alert_thresholds['response_time_ms']:
            alerts.append({
                'type': 'performance',
                'level': 'warning',
                'message': f'Response time high: {system_metrics.response_time_avg:.1f}ms',
                'timestamp': datetime.now().isoformat()
            })
        
        # Adicionar alertas à lista
        for alert in alerts:
            self.alerts.append(alert)
            self.logger.log_system('monitoring', 'alert_generated', alert)
        
        # Manter apenas últimos 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _send_webhooks(self, system_metrics: SystemMetrics, business_metrics: BusinessMetrics):
        """Envia webhooks com métricas"""
        if not self.webhook_urls:
            return
        
        payload = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': asdict(system_metrics),
            'business_metrics': asdict(business_metrics),
            'alerts': self.alerts[-10:]  # Últimos 10 alertas
        }
        
        for webhook_url in self.webhook_urls:
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                if response.status_code != 200:
                    self.logger.log_system('monitoring', 'webhook_error', {
                        'url': webhook_url,
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                self.logger.log_system('monitoring', 'webhook_exception', {
                    'url': webhook_url,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    def add_webhook_url(self, url: str):
        """Adiciona URL de webhook"""
        if url not in self.webhook_urls:
            self.webhook_urls.append(url)
            self.logger.log_system('monitoring', 'webhook_added', {
                'url': url,
                'timestamp': datetime.now().isoformat()
            })
    
    def remove_webhook_url(self, url: str):
        """Remove URL de webhook"""
        if url in self.webhook_urls:
            self.webhook_urls.remove(url)
            self.logger.log_system('monitoring', 'webhook_removed', {
                'url': url,
                'timestamp': datetime.now().isoformat()
            })
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais"""
        if not self.system_metrics or not self.business_metrics:
            return {}
        
        latest_system = self.system_metrics[-1]
        latest_business = self.business_metrics[-1]
        
        return {
            'system': asdict(latest_system),
            'business': asdict(latest_business),
            'alerts': self.alerts[-10:],  # Últimos 10 alertas
            'webhooks_enabled': self.webhook_enabled,
            'webhook_count': len(self.webhook_urls)
        }
    
    def get_metrics_history(self, hours: int = 24) -> Dict[str, List]:
        """Retorna histórico de métricas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        system_history = [
            asdict(m) for m in self.system_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        business_history = [
            asdict(m) for m in self.business_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        return {
            'system_metrics': system_history,
            'business_metrics': business_history,
            'alerts': [a for a in self.alerts if datetime.fromisoformat(a['timestamp']) >= cutoff_time]
        }
    
    def increment_request_counter(self):
        """Incrementa contador de requests"""
        self.request_counter += 1
    
    def increment_error_counter(self):
        """Incrementa contador de erros"""
        self.error_counter += 1
    
    def record_session(self, crypto_type: str, amount_ars: float):
        """Registra nova sessão"""
        self.session_counter[crypto_type] += 1
        self.volume_counter[crypto_type] += amount_ars

# Instância global do monitoramento
advanced_monitoring = AdvancedMonitoring() 