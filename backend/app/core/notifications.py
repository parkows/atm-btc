import requests
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from .config import atm_config
from .logger import atm_logger

class NotificationManager:
    def __init__(self):
        self.config = atm_config.get_notification_settings()
        self.logger = atm_logger
    
    def send_webhook(self, event: str, data: Dict[str, Any]) -> bool:
        """Envia notificação via webhook"""
        if not self.config['webhook_enabled'] or not self.config['webhook_url']:
            return False
        
        try:
            payload = {
                'event': event,
                'data': data,
                'timestamp': datetime.utcnow().isoformat(),
                'atm_id': atm_config.get_atm_id()
            }
            
            response = requests.post(
                self.config['webhook_url'],
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.logger.log_system('notifications', 'webhook_sent', {
                    'event': event,
                    'status_code': response.status_code
                })
                return True
            else:
                self.logger.log_system('notifications', 'webhook_failed', {
                    'event': event,
                    'status_code': response.status_code,
                    'response': response.text
                })
                return False
                
        except Exception as e:
            self.logger.log_system('notifications', 'webhook_error', {
                'event': event,
                'error': str(e)
            })
            return False
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Envia notificação por email"""
        if not self.config['email_enabled']:
            return False
        
        try:
            # Configuração básica de email (pode ser expandida)
            msg = MIMEMultipart()
            msg['From'] = 'atm@liquidgold.com'
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Aqui você configuraria o servidor SMTP real
            # Por enquanto, apenas logamos
            self.logger.log_system('notifications', 'email_sent', {
                'to': to_email,
                'subject': subject
            })
            return True
            
        except Exception as e:
            self.logger.log_system('notifications', 'email_error', {
                'to': to_email,
                'error': str(e)
            })
            return False
    
    def notify_transaction_started(self, data: Dict[str, Any]):
        """Notifica quando uma transação é iniciada"""
        self.send_webhook('transaction_started', data)
        
        if self.config['email_enabled']:
            subject = f"Nova transação iniciada - {data.get('session_code', 'N/A')}"
            body = f"""
            Nova transação iniciada:
            - Sessão: {data.get('session_code', 'N/A')}
            - ATM: {data.get('atm_id', 'N/A')}
            - Valor: ${data.get('amount_ars', 0):,.2f} ARS
            - Timestamp: {datetime.utcnow().isoformat()}
            """
            self.send_email('admin@liquidgold.com', subject, body)
    
    def notify_transaction_completed(self, data: Dict[str, Any]):
        """Notifica quando uma transação é completada"""
        self.send_webhook('transaction_completed', data)
        
        if self.config['email_enabled']:
            subject = f"Transação completada - {data.get('session_code', 'N/A')}"
            body = f"""
            Transação completada com sucesso:
            - Sessão: {data.get('session_code', 'N/A')}
            - Valor: ${data.get('amount_ars', 0):,.2f} ARS
            - BTC: {data.get('btc_expected', 0):.8f} BTC
            - Timestamp: {datetime.utcnow().isoformat()}
            """
            self.send_email('admin@liquidgold.com', subject, body)
    
    def notify_transaction_failed(self, data: Dict[str, Any]):
        """Notifica quando uma transação falha"""
        self.send_webhook('transaction_failed', data)
        
        if self.config['email_enabled']:
            subject = f"Transação falhou - {data.get('session_code', 'N/A')}"
            body = f"""
            Transação falhou:
            - Sessão: {data.get('session_code', 'N/A')}
            - Motivo: {data.get('reason', 'Desconhecido')}
            - Timestamp: {datetime.utcnow().isoformat()}
            """
            self.send_email('admin@liquidgold.com', subject, body)
    
    def notify_maintenance_required(self, component: str, issue: str):
        """Notifica quando manutenção é necessária"""
        data = {
            'component': component,
            'issue': issue,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.send_webhook('maintenance_required', data)
        
        if self.config['email_enabled']:
            subject = f"Manutenção necessária - {component}"
            body = f"""
            Manutenção necessária:
            - Componente: {component}
            - Problema: {issue}
            - Timestamp: {datetime.utcnow().isoformat()}
            """
            self.send_email('maintenance@liquidgold.com', subject, body)
    
    def notify_security_alert(self, event: str, details: Dict[str, Any]):
        """Notifica alertas de segurança"""
        data = {
            'event': event,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.send_webhook('security_alert', data)
        
        if self.config['email_enabled']:
            subject = f"Alerta de Segurança - {event}"
            body = f"""
            Alerta de Segurança:
            - Evento: {event}
            - Detalhes: {json.dumps(details, indent=2)}
            - Timestamp: {datetime.utcnow().isoformat()}
            """
            self.send_email('security@liquidgold.com', subject, body)
    
    def notify_daily_summary(self, summary: Dict[str, Any]):
        """Notifica resumo diário"""
        self.send_webhook('daily_summary', summary)
        
        if self.config['email_enabled']:
            subject = "Resumo Diário - LiquidGold ATM"
            body = f"""
            Resumo Diário:
            - Total de Transações: {summary.get('total_transactions', 0)}
            - Volume Total: ${summary.get('total_volume', 0):,.2f} ARS
            - Taxa de Sucesso: {summary.get('success_rate', 0):.2f}%
            - Erros: {summary.get('errors', 0)}
            - Timestamp: {datetime.utcnow().isoformat()}
            """
            self.send_email('admin@liquidgold.com', subject, body)

# Instância global
notification_manager = NotificationManager() 