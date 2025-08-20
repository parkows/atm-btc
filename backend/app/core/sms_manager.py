"""
Módulo de Gerenciamento de SMS - LiquidGold ATM
Utiliza Infobip para envio de SMS para Argentina e outros países
"""

import os
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import random
import string

from infobip_api_python_sdk import SendSmsApi, SmsDestination, SmsTextualMessage
from infobip_api_python_sdk import Configuration
from infobip_api_python_sdk import ApiException

# Configurar logger
logger = logging.getLogger(__name__)

class SMSManager:
    """Gerenciador de SMS usando Infobip"""
    
    def __init__(self):
        """Inicializa o gerenciador de SMS"""
        # Configurações padrão (para desenvolvimento)
        self.api_key = os.getenv('INFOBIP_API_KEY', '79bec273e41a23ad3b8faa773e443ab8-deb0d324-2fb7-484e-9133-03c2a215c1d6')
        self.base_url = os.getenv('INFOBIP_BASE_URL', 'https://9kegvy.api.infobip.com')
        self.sender = os.getenv('INFOBIP_SENDER', 'LiquidGold')
        
        if not self.api_key:
            logger.warning("INFOBIP_API_KEY não configurada - SMS desabilitado")
            self.enabled = False
        else:
            self.enabled = True
            self._setup_client()
    
    def _setup_client(self):
        """Configura o cliente Infobip"""
        try:
            configuration = Configuration(
                host=self.base_url,
                api_key={"APIKeyHeader": self.api_key}
            )
            self.sms_api = SendSmsApi(configuration)
            logger.info(f"Cliente Infobip configurado com sucesso - URL: {self.base_url}")
            logger.info(f"API Key: {self.api_key[:20]}...")
        except Exception as e:
            logger.error(f"Erro ao configurar cliente Infobip: {e}")
            self.enabled = False
    
    def send_sms(self, phone_number: str, message: str, reference: Optional[str] = None) -> Dict:
        """
        Envia um SMS
        
        Args:
            phone_number: Número do telefone (formato internacional)
            message: Mensagem a ser enviada
            reference: Referência opcional para rastreamento
            
        Returns:
            Dict com resultado da operação
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "SMS desabilitado - API key não configurada",
                "reference": reference
            }
        
        try:
            # Validar número de telefone
            if not self._validate_phone_number(phone_number):
                return {
                    "success": False,
                    "error": "Número de telefone inválido",
                    "phone_number": phone_number,
                    "reference": reference
                }
            
            # Criar destino
            destination = SmsDestination(
                to=phone_number
            )
            
            # Criar mensagem
            sms_message = SmsTextualMessage(
                destinations=[destination],
                from_=self.sender,
                text=message
            )
            
            # Enviar SMS
            response = self.sms_api.send_sms(sms_message)
            
            # Processar resposta
            if response.messages and len(response.messages) > 0:
                message_info = response.messages[0]
                
                result = {
                    "success": True,
                    "message_id": message_info.message_id,
                    "status": message_info.status.group_name,
                    "phone_number": phone_number,
                    "reference": reference,
                    "sent_at": datetime.utcnow().isoformat(),
                    "cost": getattr(message_info, 'cost', None)
                }
                
                logger.info(f"SMS enviado com sucesso: {message_info.message_id}")
                return result
            else:
                return {
                    "success": False,
                    "error": "Resposta vazia do Infobip",
                    "phone_number": phone_number,
                    "reference": reference
                }
                
        except ApiException as e:
            error_msg = f"Erro da API Infobip: {e.body}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "phone_number": phone_number,
                "reference": reference
            }
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "phone_number": phone_number,
                "reference": reference
            }
    
    def send_verification_code(self, phone_number: str, code: str, expires_in_minutes: int = 10) -> Dict:
        """
        Envia código de verificação por SMS para confirmação do número
        
        Args:
            phone_number: Número do telefone
            code: Código de verificação
            expires_in_minutes: Tempo de expiração em minutos
            
        Returns:
            Dict com resultado da operação
        """
        message = f"🔐 LiquidGold ATM - Código de verificação: {code}\n\n⏰ Válido por {expires_in_minutes} minutos\n\n📱 Use este código para confirmar seu número\n\n🚫 Não compartilhe com ninguém"
        
        logger.info(f"Enviando código de verificação para {phone_number}: {code}")
        
        return self.send_sms(
            phone_number=phone_number,
            message=message,
            reference=f"VERIFY_{code}"
        )
    
    def send_transaction_confirmation(self, phone_number: str, transaction_data: Dict) -> Dict:
        """
        Envia confirmação de transação por SMS
        
        Args:
            phone_number: Número do telefone
            transaction_data: Dados da transação
            
        Returns:
            Dict com resultado da operação
        """
        # Formatar valores
        amount_ars = f"${transaction_data.get('amount_ars', 0):,.2f}"
        amount_crypto = f"{transaction_data.get('amount_crypto', 0):.8f}"
        crypto_type = transaction_data.get('crypto_type', 'BTC')
        transaction_type = transaction_data.get('transaction_type', 'VENDA')
        
        if transaction_type == "VENDA":
            message = f"✅ LiquidGold ATM - Venda confirmada!\n\n💰 {crypto_type}: {amount_crypto}\n💵 ARS: {amount_ars}\n\n📱 Seu pagamento será processado em breve."
        else:
            message = f"✅ LiquidGold ATM - Compra confirmada!\n\n💰 {crypto_type}: {amount_crypto}\n💵 ARS: {amount_ars}\n\n📱 Sua criptomoeda será enviada em breve."
        
        return self.send_sms(
            phone_number=phone_number,
            message=message,
            reference=f"TXN_{transaction_data.get('id', 'UNKNOWN')}"
        )
    
    def send_wallet_request(self, phone_number: str, crypto_type: str, amount_ars: float) -> Dict:
        """
        Solicita carteira do usuário por SMS (segunda chamada da API)
        
        Args:
            phone_number: Número do telefone
            crypto_type: Tipo de criptomoeda
            amount_ars: Valor em ARS
            
        Returns:
            Dict com resultado da operação
        """
        message = f"📱 LiquidGold ATM - Solicitação de carteira\n\n💰 {crypto_type}: ${amount_ars:,.2f} ARS\n\n📝 Por favor, envie seu endereço {crypto_type} para continuar a transação.\n\n⏰ Esta solicitação expira em 30 minutos.\n\n💡 Responda este SMS com seu endereço {crypto_type}"
        
        logger.info(f"Solicitando carteira {crypto_type} para {phone_number} - Valor: ${amount_ars:,.2f} ARS")
        
        return self.send_sms(
            phone_number=phone_number,
            message=message,
            reference=f"WALLET_{crypto_type}_{int(amount_ars)}"
        )
    
    def send_transaction_status_update(self, phone_number: str, status: str, transaction_id: str) -> Dict:
        """
        Envia atualização de status da transação
        
        Args:
            phone_number: Número do telefone
            status: Novo status
            transaction_id: ID da transação
            
        Returns:
            Dict com resultado da operação
        """
        status_messages = {
            "processing": "🔄 LiquidGold ATM - Sua transação está sendo processada...",
            "completed": "✅ LiquidGold ATM - Transação concluída com sucesso!",
            "failed": "❌ LiquidGold ATM - Transação falhou. Entre em contato com o suporte.",
            "cancelled": "🚫 LiquidGold ATM - Transação cancelada pelo usuário."
        }
        
        message = status_messages.get(status, f"📱 LiquidGold ATM - Status atualizado: {status}")
        message += f"\n\n🆔 ID: {transaction_id}"
        
        return self.send_sms(
            phone_number=phone_number,
            message=message,
            reference=f"STATUS_{transaction_id}"
        )
    
    def generate_verification_code(self, length: int = 6) -> str:
        """
        Gera código de verificação aleatório
        
        Args:
            length: Comprimento do código
            
        Returns:
            Código de verificação
        """
        return ''.join(random.choices(string.digits, k=length))
    
    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        Valida formato do número de telefone
        
        Args:
            phone_number: Número do telefone
            
        Returns:
            True se válido, False caso contrário
        """
        # Remover espaços e caracteres especiais
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Verificar se começa com + e tem pelo menos 10 dígitos
        if phone_number.startswith('+') and len(clean_number) >= 10:
            return True
        
        # Verificar se tem pelo menos 10 dígitos sem +
        if len(clean_number) >= 10:
            return True
        
        return False
    
    def get_sms_status(self, message_id: str) -> Dict:
        """
        Obtém status de um SMS enviado
        
        Args:
            message_id: ID da mensagem
            
        Returns:
            Dict com status da mensagem
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "SMS desabilitado"
            }
        
        try:
            # Implementar consulta de status se necessário
            # Por enquanto, retorna status básico
            return {
                "success": True,
                "message_id": message_id,
                "status": "delivered",  # Assumindo que foi entregue
                "checked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message_id": message_id
            }
    
    def get_balance(self) -> Dict:
        """
        Obtém saldo da conta Infobip
        
        Returns:
            Dict com informações de saldo
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "SMS desabilitado"
            }
        
        try:
            # Implementar consulta de saldo se necessário
            return {
                "success": True,
                "balance": "N/A",  # Implementar quando necessário
                "currency": "USD",
                "checked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Instância global
sms_manager = SMSManager() 