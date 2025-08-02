#!/usr/bin/env python3
"""
Módulo de Gerenciamento de WhatsApp Business - LiquidGold ATM
Gerencia envio e recebimento de mensagens WhatsApp para compras de criptomoedas
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .logger import atm_logger
from .config import atm_config

class WhatsAppManager:
    """Gerenciador de WhatsApp Business para compras de criptomoedas"""
    
    def __init__(self):
        self.logger = atm_logger
        self.config = atm_config
        
        # Configurações de WhatsApp Business (mock para desenvolvimento)
        self.whatsapp_api_url = "https://graph.facebook.com/v17.0/phone_number_id/messages"
        self.whatsapp_token = "mock_token_for_development"
        self.phone_number_id = "mock_phone_number_id"
        
        # Códigos de verificação armazenados (em produção, usar Redis/DB)
        self.verification_codes = {}
        self.pending_addresses = {}
    
    def send_verification_code(self, phone_number: str, atm_id: str) -> Dict[str, Any]:
        """Envia código de verificação por WhatsApp"""
        try:
            # Gerar código de 6 dígitos
            import random
            verification_code = f"{random.randint(100000, 999999)}"
            
            # Armazenar código (em produção, usar Redis com TTL)
            self.verification_codes[phone_number] = {
                'code': verification_code,
                'atm_id': atm_id,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(minutes=5)
            }
            
            # Mensagem WhatsApp
            message = f"🔐 *LiquidGold ATM - Código de Verificação*\n\nSeu código de verificação é: *{verification_code}*\n\n⏰ Válido por 5 minutos\n\n💡 Digite este código no ATM para continuar"
            
            # Enviar WhatsApp (mock para desenvolvimento)
            if self._send_whatsapp(phone_number, message):
                self.logger.log_system('whatsapp_manager', 'verification_code_sent', {
                    'phone_number': phone_number,
                    'atm_id': atm_id,
                    'code': verification_code
                })
                
                return {
                    'success': True,
                    'message': 'Código de verificação enviado via WhatsApp',
                    'phone_number': phone_number,
                    'method': 'whatsapp',
                    'expires_in': 300  # 5 minutos
                }
            else:
                raise Exception("Erro ao enviar WhatsApp")
                
        except Exception as e:
            self.logger.log_system('whatsapp_manager', 'send_verification_error', {
                'phone_number': phone_number,
                'error': str(e)
            })
            raise
    
    def verify_code(self, phone_number: str, code: str) -> Dict[str, Any]:
        """Verifica código de confirmação"""
        try:
            if phone_number not in self.verification_codes:
                return {
                    'success': False,
                    'message': 'Código não encontrado ou expirado'
                }
            
            stored_data = self.verification_codes[phone_number]
            
            # Verificar se expirou
            if datetime.utcnow() > stored_data['expires_at']:
                del self.verification_codes[phone_number]
                return {
                    'success': False,
                    'message': 'Código expirado'
                }
            
            # Verificar código
            if code == stored_data['code']:
                # Código válido - remover da memória
                atm_id = stored_data['atm_id']
                del self.verification_codes[phone_number]
                
                self.logger.log_system('whatsapp_manager', 'verification_success', {
                    'phone_number': phone_number,
                    'atm_id': atm_id
                })
                
                return {
                    'success': True,
                    'message': 'Código verificado com sucesso',
                    'atm_id': atm_id,
                    'method': 'whatsapp'
                }
            else:
                return {
                    'success': False,
                    'message': 'Código incorreto'
                }
                
        except Exception as e:
            self.logger.log_system('whatsapp_manager', 'verify_code_error', {
                'phone_number': phone_number,
                'error': str(e)
            })
            raise
    
    def request_wallet_address(self, phone_number: str, crypto_type: str, amount_ars: float) -> Dict[str, Any]:
        """Solicita endereço da wallet por WhatsApp"""
        try:
            # Gerar ID único para a solicitação
            import uuid
            request_id = str(uuid.uuid4())[:8]
            
            # Armazenar dados da solicitação
            self.pending_addresses[request_id] = {
                'phone_number': phone_number,
                'crypto_type': crypto_type,
                'amount_ars': amount_ars,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(minutes=10)
            }
            
            # Mensagem WhatsApp
            message = f"💰 *LiquidGold ATM - Compra de {crypto_type}*\n\nPara comprar *{crypto_type}* por *${amount_ars:,.2f} ARS*, responda esta mensagem com o endereço da sua wallet {crypto_type}.\n\n📝 *ID:* {request_id}\n\n⏰ Você tem 10 minutos para responder"
            
            if self._send_whatsapp(phone_number, message):
                self.logger.log_system('whatsapp_manager', 'wallet_address_requested', {
                    'phone_number': phone_number,
                    'crypto_type': crypto_type,
                    'amount_ars': amount_ars,
                    'request_id': request_id
                })
                
                return {
                    'success': True,
                    'message': 'WhatsApp enviado solicitando endereço da wallet',
                    'request_id': request_id,
                    'method': 'whatsapp',
                    'expires_in': 600  # 10 minutos
                }
            else:
                raise Exception("Erro ao enviar WhatsApp")
                
        except Exception as e:
            self.logger.log_system('whatsapp_manager', 'request_wallet_address_error', {
                'phone_number': phone_number,
                'crypto_type': crypto_type,
                'error': str(e)
            })
            raise
    
    def process_wallet_address_response(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Processa resposta WhatsApp com endereço da wallet"""
        try:
            # Extrair ID da mensagem (formato: "ID: ABC123")
            import re
            id_match = re.search(r'ID:\s*([A-Z0-9]+)', message)
            if not id_match:
                return {
                    'success': False,
                    'message': 'Formato de resposta inválido'
                }
            
            request_id = id_match.group(1)
            
            # Verificar se a solicitação existe
            if request_id not in self.pending_addresses:
                return {
                    'success': False,
                    'message': 'Solicitação não encontrada ou expirada'
                }
            
            request_data = self.pending_addresses[request_id]
            
            # Verificar se expirou
            if datetime.utcnow() > request_data['expires_at']:
                del self.pending_addresses[request_id]
                return {
                    'success': False,
                    'message': 'Solicitação expirada'
                }
            
            # Extrair endereço da wallet (remover ID da mensagem)
            wallet_address = message.replace(f"ID: {request_id}", "").strip()
            
            # Validar formato do endereço
            if not self._validate_wallet_address(wallet_address, request_data['crypto_type']):
                return {
                    'success': False,
                    'message': 'Formato de endereço inválido'
                }
            
            # Remover da memória
            del self.pending_addresses[request_id]
            
            self.logger.log_system('whatsapp_manager', 'wallet_address_received', {
                'phone_number': phone_number,
                'crypto_type': request_data['crypto_type'],
                'wallet_address': wallet_address,
                'amount_ars': request_data['amount_ars']
            })
            
            return {
                'success': True,
                'message': 'Endereço da wallet recebido via WhatsApp',
                'wallet_address': wallet_address,
                'crypto_type': request_data['crypto_type'],
                'amount_ars': request_data['amount_ars'],
                'phone_number': phone_number,
                'method': 'whatsapp'
            }
            
        except Exception as e:
            self.logger.log_system('whatsapp_manager', 'process_wallet_address_error', {
                'phone_number': phone_number,
                'message': message,
                'error': str(e)
            })
            raise
    
    def _send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Envia WhatsApp (mock para desenvolvimento)"""
        try:
            # Em produção, integrar com WhatsApp Business API
            print(f"📱 WhatsApp enviado para {phone_number}: {message}")
            
            # Simular delay de envio
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            self.logger.log_system('whatsapp_manager', 'send_whatsapp_error', {
                'phone_number': phone_number,
                'error': str(e)
            })
            return False
    
    def _validate_wallet_address(self, address: str, crypto_type: str) -> bool:
        """Valida formato do endereço da wallet"""
        try:
            if crypto_type == 'BTC':
                # Validar endereço Bitcoin (formato básico)
                return len(address) >= 26 and len(address) <= 35 and address.startswith(('1', '3', 'bc1'))
            
            elif crypto_type == 'USDT':
                # Validar endereço TRC20 (formato básico)
                return len(address) == 34 and address.startswith('T')
            
            else:
                return False
                
        except Exception:
            return False
    
    def get_pending_requests(self) -> Dict[str, Any]:
        """Obtém solicitações pendentes (para debug)"""
        return {
            'verification_codes': len(self.verification_codes),
            'pending_addresses': len(self.pending_addresses),
            'total_pending': len(self.verification_codes) + len(self.pending_addresses)
        }

# Instância global
whatsapp_manager = WhatsAppManager() 