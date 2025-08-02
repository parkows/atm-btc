#!/usr/bin/env python3
"""
Sistema de Webhooks - LiquidGold ATM
Notificações em tempo real para eventos do sistema
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass, asdict
from enum import Enum

from .config import atm_config
from .logger import atm_logger

class WebhookEventType(Enum):
    """Tipos de eventos para webhooks"""
    SESSION_CREATED = "session_created"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"
    PAYMENT_RECEIVED = "payment_received"
    SYSTEM_ALERT = "system_alert"
    BUSINESS_METRICS = "business_metrics"
    SECURITY_ALERT = "security_alert"
    CRYPTO_QUOTE = "crypto_quote"

@dataclass
class WebhookEvent:
    """Estrutura de evento para webhook"""
    event_type: WebhookEventType
    timestamp: datetime
    data: Dict[str, Any]
    session_id: Optional[str] = None
    crypto_type: Optional[str] = None
    amount_ars: Optional[float] = None

class WebhookManager:
    """Gerenciador de webhooks para notificações"""
    
    def __init__(self):
        self.config = atm_config
        self.logger = atm_logger
        
        # URLs de webhook por tipo de evento
        self.webhook_urls = {
            event_type: [] for event_type in WebhookEventType
        }
        
        # Configurações de webhook
        self.webhook_config = {
            'enabled': True,
            'timeout': 10,
            'retry_attempts': 3,
            'retry_delay': 5,
            'max_queue_size': 1000
        }
        
        # Fila de eventos
        self.event_queue = []
        self.queue_lock = threading.Lock()
        
        # Thread de processamento
        self.processing_thread = None
        self.is_processing = False
        
        # Estatísticas
        self.stats = {
            'events_sent': 0,
            'events_failed': 0,
            'webhooks_registered': 0
        }
    
    def start_processing(self):
        """Inicia processamento de webhooks em background"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        
        self.logger.log_system('webhook_manager', 'webhook_processing_started', {
            'timestamp': datetime.now().isoformat()
        })
    
    def stop_processing(self):
        """Para processamento de webhooks"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join()
        
        self.logger.log_system('webhook_manager', 'webhook_processing_stopped', {
            'timestamp': datetime.now().isoformat()
        })
    
    def _processing_loop(self):
        """Loop principal de processamento de webhooks"""
        while self.is_processing:
            try:
                # Processar eventos da fila
                with self.queue_lock:
                    if self.event_queue:
                        event = self.event_queue.pop(0)
                        self._send_webhook_event(event)
                
                # Aguardar próximo ciclo
                time.sleep(1)
                
            except Exception as e:
                self.logger.log_system('webhook_manager', 'processing_error', {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                time.sleep(5)
    
    def _send_webhook_event(self, event: WebhookEvent):
        """Envia evento para webhooks registrados"""
        urls = self.webhook_urls.get(event.event_type, [])
        
        if not urls:
            return
        
        payload = {
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data,
            'session_id': event.session_id,
            'crypto_type': event.crypto_type,
            'amount_ars': event.amount_ars
        }
        
        for url in urls:
            self._send_webhook_to_url(url, payload)
    
    def _send_webhook_to_url(self, url: str, payload: Dict[str, Any]):
        """Envia webhook para URL específica com retry"""
        for attempt in range(self.webhook_config['retry_attempts']):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'LiquidGold-ATM-Webhook/1.0'
                    },
                    timeout=self.webhook_config['timeout']
                )
                
                if response.status_code in [200, 201, 202]:
                    self.stats['events_sent'] += 1
                    self.logger.log_system('webhook_manager', 'webhook_sent_success', {
                        'url': url,
                        'event_type': payload['event_type'],
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat()
                    })
                    return
                else:
                    self.logger.log_system('webhook_manager', 'webhook_sent_error', {
                        'url': url,
                        'event_type': payload['event_type'],
                        'status_code': response.status_code,
                        'response_text': response.text[:200],
                        'timestamp': datetime.now().isoformat()
                    })
                    
            except Exception as e:
                self.logger.log_system('webhook_manager', 'webhook_sent_exception', {
                    'url': url,
                    'event_type': payload['event_type'],
                    'error': str(e),
                    'attempt': attempt + 1,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Aguardar antes de tentar novamente
            if attempt < self.webhook_config['retry_attempts'] - 1:
                time.sleep(self.webhook_config['retry_delay'])
        
        # Se chegou aqui, falhou em todas as tentativas
        self.stats['events_failed'] += 1
    
    def register_webhook(self, event_type: WebhookEventType, url: str):
        """Registra webhook para tipo de evento"""
        if url not in self.webhook_urls[event_type]:
            self.webhook_urls[event_type].append(url)
            self.stats['webhooks_registered'] += 1
            
            self.logger.log_system('webhook_manager', 'webhook_registered', {
                'event_type': event_type.value,
                'url': url,
                'timestamp': datetime.now().isoformat()
            })
    
    def unregister_webhook(self, event_type: WebhookEventType, url: str):
        """Remove webhook para tipo de evento"""
        if url in self.webhook_urls[event_type]:
            self.webhook_urls[event_type].remove(url)
            self.stats['webhooks_registered'] -= 1
            
            self.logger.log_system('webhook_manager', 'webhook_unregistered', {
                'event_type': event_type.value,
                'url': url,
                'timestamp': datetime.now().isoformat()
            })
    
    def send_event(self, event: WebhookEvent):
        """Envia evento para processamento"""
        if not self.webhook_config['enabled']:
            return
        
        with self.queue_lock:
            if len(self.event_queue) < self.webhook_config['max_queue_size']:
                self.event_queue.append(event)
            else:
                self.logger.log_system('webhook_manager', 'queue_full', {
                    'queue_size': len(self.event_queue),
                    'event_type': event.event_type.value,
                    'timestamp': datetime.now().isoformat()
                })
    
    def send_session_created(self, session_data: Dict[str, Any]):
        """Envia evento de sessão criada"""
        event = WebhookEvent(
            event_type=WebhookEventType.SESSION_CREATED,
            timestamp=datetime.now(),
            data=session_data,
            session_id=session_data.get('session_code'),
            crypto_type=session_data.get('crypto_type'),
            amount_ars=session_data.get('amount_ars')
        )
        self.send_event(event)
    
    def send_session_completed(self, session_data: Dict[str, Any]):
        """Envia evento de sessão completada"""
        event = WebhookEvent(
            event_type=WebhookEventType.SESSION_COMPLETED,
            timestamp=datetime.now(),
            data=session_data,
            session_id=session_data.get('session_code'),
            crypto_type=session_data.get('crypto_type'),
            amount_ars=session_data.get('amount_ars')
        )
        self.send_event(event)
    
    def send_session_failed(self, session_data: Dict[str, Any], error: str):
        """Envia evento de sessão falhou"""
        event_data = {**session_data, 'error': error}
        event = WebhookEvent(
            event_type=WebhookEventType.SESSION_FAILED,
            timestamp=datetime.now(),
            data=event_data,
            session_id=session_data.get('session_code'),
            crypto_type=session_data.get('crypto_type'),
            amount_ars=session_data.get('amount_ars')
        )
        self.send_event(event)
    
    def send_payment_received(self, payment_data: Dict[str, Any]):
        """Envia evento de pagamento recebido"""
        event = WebhookEvent(
            event_type=WebhookEventType.PAYMENT_RECEIVED,
            timestamp=datetime.now(),
            data=payment_data,
            session_id=payment_data.get('session_code'),
            crypto_type=payment_data.get('crypto_type'),
            amount_ars=payment_data.get('amount_ars')
        )
        self.send_event(event)
    
    def send_system_alert(self, alert_data: Dict[str, Any]):
        """Envia evento de alerta do sistema"""
        event = WebhookEvent(
            event_type=WebhookEventType.SYSTEM_ALERT,
            timestamp=datetime.now(),
            data=alert_data
        )
        self.send_event(event)
    
    def send_security_alert(self, security_data: Dict[str, Any]):
        """Envia evento de alerta de segurança"""
        event = WebhookEvent(
            event_type=WebhookEventType.SECURITY_ALERT,
            timestamp=datetime.now(),
            data=security_data
        )
        self.send_event(event)
    
    def send_business_metrics(self, metrics_data: Dict[str, Any]):
        """Envia evento de métricas de negócio"""
        event = WebhookEvent(
            event_type=WebhookEventType.BUSINESS_METRICS,
            timestamp=datetime.now(),
            data=metrics_data
        )
        self.send_event(event)
    
    def send_crypto_quote(self, quote_data: Dict[str, Any]):
        """Envia evento de cotação de criptomoeda"""
        event = WebhookEvent(
            event_type=WebhookEventType.CRYPTO_QUOTE,
            timestamp=datetime.now(),
            data=quote_data,
            crypto_type=quote_data.get('crypto'),
            amount_ars=quote_data.get('amount_ars')
        )
        self.send_event(event)
    
    def get_webhook_status(self) -> Dict[str, Any]:
        """Retorna status dos webhooks"""
        return {
            'enabled': self.webhook_config['enabled'],
            'processing': self.is_processing,
            'queue_size': len(self.event_queue),
            'stats': self.stats,
            'registered_webhooks': {
                event_type.value: len(urls) 
                for event_type, urls in self.webhook_urls.items()
            }
        }
    
    def get_registered_webhooks(self) -> Dict[str, List[str]]:
        """Retorna webhooks registrados"""
        return {
            event_type.value: urls 
            for event_type, urls in self.webhook_urls.items()
        }
    
    def clear_webhooks(self, event_type: Optional[WebhookEventType] = None):
        """Limpa webhooks registrados"""
        if event_type:
            self.webhook_urls[event_type].clear()
            self.logger.log_system('webhook_manager', 'webhooks_cleared', {
                'event_type': event_type.value,
                'timestamp': datetime.now().isoformat()
            })
        else:
            for event_type in WebhookEventType:
                self.webhook_urls[event_type].clear()
            self.logger.log_system('webhook_manager', 'all_webhooks_cleared', {
                'timestamp': datetime.now().isoformat()
            })

# Instância global do gerenciador de webhooks
webhook_manager = WebhookManager() 