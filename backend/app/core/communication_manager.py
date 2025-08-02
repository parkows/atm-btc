#!/usr/bin/env python3
"""
Módulo de Gerenciamento de Comunicação - LiquidGold ATM
Gerencia SMS e WhatsApp de forma unificada
"""

from typing import Dict, Any, Optional
from .sms_manager import sms_manager
from .whatsapp_manager import whatsapp_manager
from .logger import atm_logger

class CommunicationManager:
    """Gerenciador unificado de comunicação (SMS + WhatsApp)"""
    
    def __init__(self):
        self.logger = atm_logger
        self.sms_manager = sms_manager
        self.whatsapp_manager = whatsapp_manager
    
    def send_verification_code(self, phone_number: str, atm_id: str, method: str = "whatsapp") -> Dict[str, Any]:
        """Envia código de verificação via método escolhido"""
        try:
            if method.lower() == "whatsapp":
                return self.whatsapp_manager.send_verification_code(phone_number, atm_id)
            elif method.lower() == "sms":
                return self.sms_manager.send_verification_code(phone_number, atm_id)
            else:
                raise Exception(f"Método de comunicação '{method}' não suportado")
                
        except Exception as e:
            self.logger.log_system('communication_manager', 'send_verification_error', {
                'phone_number': phone_number,
                'method': method,
                'error': str(e)
            })
            raise
    
    def verify_code(self, phone_number: str, code: str, method: str = "whatsapp") -> Dict[str, Any]:
        """Verifica código via método escolhido"""
        try:
            if method.lower() == "whatsapp":
                return self.whatsapp_manager.verify_code(phone_number, code)
            elif method.lower() == "sms":
                return self.sms_manager.verify_code(phone_number, code)
            else:
                raise Exception(f"Método de comunicação '{method}' não suportado")
                
        except Exception as e:
            self.logger.log_system('communication_manager', 'verify_code_error', {
                'phone_number': phone_number,
                'method': method,
                'error': str(e)
            })
            raise
    
    def request_wallet_address(self, phone_number: str, crypto_type: str, amount_ars: float, method: str = "whatsapp") -> Dict[str, Any]:
        """Solicita endereço da wallet via método escolhido"""
        try:
            if method.lower() == "whatsapp":
                return self.whatsapp_manager.request_wallet_address(phone_number, crypto_type, amount_ars)
            elif method.lower() == "sms":
                return self.sms_manager.request_wallet_address(phone_number, crypto_type, amount_ars)
            else:
                raise Exception(f"Método de comunicação '{method}' não suportado")
                
        except Exception as e:
            self.logger.log_system('communication_manager', 'request_wallet_address_error', {
                'phone_number': phone_number,
                'crypto_type': crypto_type,
                'method': method,
                'error': str(e)
            })
            raise
    
    def process_wallet_address_response(self, phone_number: str, message: str, method: str = "whatsapp") -> Dict[str, Any]:
        """Processa resposta via método escolhido"""
        try:
            if method.lower() == "whatsapp":
                return self.whatsapp_manager.process_wallet_address_response(phone_number, message)
            elif method.lower() == "sms":
                return self.sms_manager.process_wallet_address_response(phone_number, message)
            else:
                raise Exception(f"Método de comunicação '{method}' não suportado")
                
        except Exception as e:
            self.logger.log_system('communication_manager', 'process_wallet_address_error', {
                'phone_number': phone_number,
                'method': method,
                'error': str(e)
            })
            raise
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de ambos os sistemas"""
        try:
            sms_stats = self.sms_manager.get_pending_requests()
            whatsapp_stats = self.whatsapp_manager.get_pending_requests()
            
            return {
                'sms': sms_stats,
                'whatsapp': whatsapp_stats,
                'total_pending': sms_stats['total_pending'] + whatsapp_stats['total_pending']
            }
            
        except Exception as e:
            self.logger.log_system('communication_manager', 'get_stats_error', {
                'error': str(e)
            })
            return {
                'sms': {'total_pending': 0},
                'whatsapp': {'total_pending': 0},
                'total_pending': 0
            }

# Instância global
communication_manager = CommunicationManager() 