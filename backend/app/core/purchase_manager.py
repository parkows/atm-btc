#!/usr/bin/env python3
"""
Módulo de Gerenciamento de Compras - LiquidGold ATM
Gerencia compras de criptomoedas pelos clientes
Integrado com sistema de SMS para coleta de endereços
"""

import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Purchase, PurchaseStatusEnum, CryptoTypeEnum, NetworkTypeEnum
from .crypto_manager import CryptoManager
from .sms_manager import sms_manager
from .logger import atm_logger
from .config import atm_config

class PurchaseManager:
    """Gerenciador de compras de criptomoedas"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.crypto_manager = CryptoManager()
        self.logger = atm_logger
        self.config = atm_config
        self.sms_manager = sms_manager
    
    def start_purchase_process(self, atm_id: str, phone_number: str) -> Dict[str, Any]:
        """Inicia processo de compra com verificação por SMS"""
        try:
            # Enviar código de verificação
            sms_result = self.sms_manager.send_verification_code(phone_number, atm_id)
            
            if sms_result['success']:
                self.logger.log_system('purchase_manager', 'purchase_process_started', {
                    'atm_id': atm_id,
                    'phone_number': phone_number
                })
                
                return {
                    'success': True,
                    'message': 'Código de verificação enviado',
                    'phone_number': phone_number,
                    'next_step': 'verify_code',
                    'expires_in': sms_result['expires_in']
                }
            else:
                raise Exception("Erro ao enviar código de verificação")
                
        except Exception as e:
            self.logger.log_error('purchase_manager', 'start_purchase_process_error', {
                'atm_id': atm_id,
                'phone_number': phone_number,
                'error': str(e)
            })
            raise
    
    def verify_phone_and_continue(self, phone_number: str, verification_code: str) -> Dict[str, Any]:
        """Verifica código e continua processo de compra"""
        try:
            # Verificar código
            verify_result = self.sms_manager.verify_code(phone_number, verification_code)
            
            if verify_result['success']:
                self.logger.log_system('purchase_manager', 'phone_verified', {
                    'phone_number': phone_number,
                    'atm_id': verify_result['atm_id']
                })
                
                return {
                    'success': True,
                    'message': 'Telefone verificado com sucesso',
                    'phone_number': phone_number,
                    'atm_id': verify_result['atm_id'],
                    'next_step': 'select_crypto'
                }
            else:
                return {
                    'success': False,
                    'message': verify_result['message']
                }
                
        except Exception as e:
            self.logger.log_error('purchase_manager', 'verify_phone_error', {
                'phone_number': phone_number,
                'error': str(e)
            })
            raise
    
    def request_wallet_address(self, phone_number: str, crypto_type: str, amount_ars: float) -> Dict[str, Any]:
        """Solicita endereço da wallet por SMS"""
        try:
            # Validar criptomoeda
            if crypto_type not in ['BTC', 'USDT']:
                raise Exception(f"Criptomoeda {crypto_type} não suportada")
            
            # Validar valor
            if not self.crypto_manager.validate_amount(crypto_type, amount_ars):
                supported_cryptos = self.crypto_manager.get_supported_cryptos()
                crypto_config = supported_cryptos['cryptos'][crypto_type]
                raise Exception(f"Valor fora dos limites para {crypto_type} (${crypto_config['min_amount']:,.2f} a ${crypto_config['max_amount']:,.2f} ARS)")
            
            # Solicitar endereço por SMS
            sms_result = self.sms_manager.request_wallet_address(phone_number, crypto_type, amount_ars)
            
            if sms_result['success']:
                self.logger.log_system('purchase_manager', 'wallet_address_requested', {
                    'phone_number': phone_number,
                    'crypto_type': crypto_type,
                    'amount_ars': amount_ars,
                    'request_id': sms_result['request_id']
                })
                
                return {
                    'success': True,
                    'message': 'SMS enviado solicitando endereço da wallet',
                    'phone_number': phone_number,
                    'crypto_type': crypto_type,
                    'amount_ars': amount_ars,
                    'request_id': sms_result['request_id'],
                    'expires_in': sms_result['expires_in']
                }
            else:
                raise Exception("Erro ao solicitar endereço da wallet")
                
        except Exception as e:
            self.logger.log_error('purchase_manager', 'request_wallet_address_error', {
                'phone_number': phone_number,
                'crypto_type': crypto_type,
                'amount_ars': amount_ars,
                'error': str(e)
            })
            raise
    
    def process_wallet_address_response(self, phone_number: str, sms_message: str) -> Dict[str, Any]:
        """Processa resposta SMS com endereço da wallet e cria compra"""
        try:
            # Processar resposta SMS
            sms_result = self.sms_manager.process_wallet_address_response(phone_number, sms_message)
            
            if not sms_result['success']:
                return sms_result
            
            # Extrair dados da resposta
            wallet_address = sms_result['wallet_address']
            crypto_type = sms_result['crypto_type']
            amount_ars = sms_result['amount_ars']
            
            # Criar compra com endereço recebido
            purchase_result = self.create_purchase(
                atm_id="LIQUIDGOLD_ATM001",  # Em produção, obter do contexto
                amount_ars=amount_ars,
                crypto_type=crypto_type,
                crypto_address=wallet_address,
                ars_payment_method="efectivo",
                phone_number=phone_number
            )
            
            return {
                'success': True,
                'message': 'Compra criada com sucesso',
                'purchase_code': purchase_result['purchase_code'],
                'wallet_address': wallet_address,
                'crypto_type': crypto_type,
                'amount_ars': amount_ars,
                'phone_number': phone_number
            }
            
        except Exception as e:
            self.logger.log_error('purchase_manager', 'process_wallet_address_error', {
                'phone_number': phone_number,
                'error': str(e)
            })
            raise
    
    def create_purchase(self, atm_id: str, amount_ars: float, crypto_type: str, 
                       crypto_address: str, ars_payment_method: str, phone_number: str = None) -> Dict[str, Any]:
        """Cria uma nova compra de criptomoeda"""
        try:
            # Validar criptomoeda
            if crypto_type not in ['BTC', 'USDT']:
                raise Exception(f"Criptomoeda {crypto_type} não suportada")
            
            # Obter cotação para compra
            quote_data = self.crypto_manager.get_quote(crypto_type, amount_ars, "COMPRA")
            
            # Gerar código único
            purchase_code = f"PURCHASE_{uuid.uuid4().hex[:8].upper()}"
            
            # Determinar tipo de rede
            network_type = NetworkTypeEnum.Lightning if crypto_type == 'BTC' else NetworkTypeEnum.TRC20
            
            # Calcular expiração (30 minutos)
            expires_at = datetime.utcnow() + timedelta(minutes=30)
            
            # Criar registro no banco
            purchase = Purchase(
                purchase_code=purchase_code,
                atm_id=atm_id,
                crypto_type=CryptoTypeEnum(crypto_type),
                network_type=network_type,
                status=PurchaseStatusEnum.aguardando_cripto,
                amount_ars=amount_ars,
                crypto_amount=quote_data['crypto_amount'],
                crypto_address=crypto_address,
                ars_payment_method=ars_payment_method,
                expires_at=expires_at
            )
            
            self.db.add(purchase)
            self.db.commit()
            self.db.refresh(purchase)
            
            # Log da criação
            self.logger.log_system('purchase_manager', 'purchase_created', {
                'purchase_code': purchase_code,
                'crypto_type': crypto_type,
                'amount_ars': amount_ars,
                'crypto_amount': quote_data['crypto_amount'],
                'phone_number': phone_number
            })
            
            return {
                'purchase_code': purchase_code,
                'amount_ars': amount_ars,
                'crypto_amount': quote_data['crypto_amount'],
                'crypto_type': crypto_type,
                'network_type': network_type.value,
                'crypto_address': crypto_address,
                'ars_payment_method': ars_payment_method,
                'phone_number': phone_number,
                'expires_at': expires_at.isoformat(),
                'quote_data': quote_data
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.log_error('purchase_manager', 'create_purchase_error', {
                'error': str(e),
                'atm_id': atm_id,
                'amount_ars': amount_ars,
                'crypto_type': crypto_type,
                'phone_number': phone_number
            })
            raise
    
    def get_purchase_status(self, purchase_code: str) -> Dict[str, Any]:
        """Obtém status de uma compra"""
        try:
            purchase = self.db.query(Purchase).filter(Purchase.purchase_code == purchase_code).first()
            
            if not purchase:
                raise Exception(f"Compra {purchase_code} não encontrada")
            
            # Verificar se expirou
            if datetime.utcnow() > purchase.expires_at and purchase.status != PurchaseStatusEnum.concluida:
                purchase.status = PurchaseStatusEnum.expirada
                self.db.commit()
            
            return {
                'purchase_code': purchase.purchase_code,
                'status': purchase.status.value,
                'amount_ars': purchase.amount_ars,
                'crypto_amount': purchase.crypto_amount,
                'crypto_type': purchase.crypto_type.value,
                'network_type': purchase.network_type.value,
                'crypto_address': purchase.crypto_address,
                'ars_payment_method': purchase.ars_payment_method,
                'created_at': purchase.created_at.isoformat(),
                'expires_at': purchase.expires_at.isoformat(),
                'completed_at': purchase.completed_at.isoformat() if purchase.completed_at else None
            }
            
        except Exception as e:
            self.logger.log_error('purchase_manager', 'get_purchase_status_error', {
                'error': str(e),
                'purchase_code': purchase_code
            })
            raise
    
    def check_crypto_received(self, purchase_code: str) -> Dict[str, Any]:
        """Verifica se a criptomoeda foi recebida"""
        try:
            purchase = self.db.query(Purchase).filter(Purchase.purchase_code == purchase_code).first()
            
            if not purchase:
                raise Exception(f"Compra {purchase_code} não encontrada")
            
            if purchase.status == PurchaseStatusEnum.concluida:
                return {'status': 'concluida', 'message': 'Compra já foi concluída'}
            
            if purchase.status == PurchaseStatusEnum.expirada:
                return {'status': 'expirada', 'message': 'Compra expirou'}
            
            # Verificar se cripto foi recebida
            crypto_status = self.crypto_manager.check_crypto_received(
                purchase.crypto_type.value, 
                purchase.crypto_address
            )
            
            if crypto_status['confirmed']:
                # Atualizar status para cripto recebida
                purchase.status = PurchaseStatusEnum.cripto_recebida
                self.db.commit()
                
                self.logger.log_system('purchase_manager', 'crypto_received', {
                    'purchase_code': purchase_code,
                    'crypto_type': purchase.crypto_type.value
                })
                
                return {
                    'status': 'cripto_recebida',
                    'message': 'Criptomoeda recebida. Aguardando pagamento ARS.',
                    'next_step': 'Enviar ARS para completar a compra'
                }
            else:
                return {
                    'status': 'aguardando_cripto',
                    'message': 'Aguardando recebimento da criptomoeda',
                    'address': purchase.crypto_address
                }
                
        except Exception as e:
            self.logger.log_error('purchase_manager', 'check_crypto_received_error', {
                'error': str(e),
                'purchase_code': purchase_code
            })
            raise
    
    def confirm_ars_payment(self, purchase_code: str) -> Dict[str, Any]:
        """Confirma pagamento em ARS e finaliza a compra"""
        try:
            purchase = self.db.query(Purchase).filter(Purchase.purchase_code == purchase_code).first()
            
            if not purchase:
                raise Exception(f"Compra {purchase_code} não encontrada")
            
            if purchase.status == PurchaseStatusEnum.concluida:
                return {'status': 'concluida', 'message': 'Compra já foi concluída'}
            
            if purchase.status == PurchaseStatusEnum.expirada:
                return {'status': 'expirada', 'message': 'Compra expirou'}
            
            if purchase.status != PurchaseStatusEnum.cripto_recebida:
                return {'status': 'erro', 'message': 'Criptomoeda ainda não foi recebida'}
            
            # Marcar como concluída
            purchase.status = PurchaseStatusEnum.concluida
            purchase.completed_at = datetime.utcnow()
            self.db.commit()
            
            self.logger.log_system('purchase_manager', 'purchase_completed', {
                'purchase_code': purchase_code,
                'crypto_type': purchase.crypto_type.value,
                'amount_ars': purchase.amount_ars,
                'crypto_amount': purchase.crypto_amount
            })
            
            return {
                'status': 'concluida',
                'message': 'Compra concluída com sucesso!',
                'purchase_code': purchase_code,
                'amount_ars': purchase.amount_ars,
                'crypto_amount': purchase.crypto_amount,
                'crypto_type': purchase.crypto_type.value,
                'completed_at': purchase.completed_at.isoformat()
            }
            
        except Exception as e:
            self.logger.log_error('purchase_manager', 'confirm_ars_payment_error', {
                'error': str(e),
                'purchase_code': purchase_code
            })
            raise
    
    def cancel_purchase(self, purchase_code: str) -> Dict[str, Any]:
        """Cancela uma compra"""
        try:
            purchase = self.db.query(Purchase).filter(Purchase.purchase_code == purchase_code).first()
            
            if not purchase:
                raise Exception(f"Compra {purchase_code} não encontrada")
            
            if purchase.status == PurchaseStatusEnum.concluida:
                return {'status': 'erro', 'message': 'Compra já foi concluída'}
            
            if purchase.status == PurchaseStatusEnum.expirada:
                return {'status': 'erro', 'message': 'Compra já expirou'}
            
            # Cancelar compra
            purchase.status = PurchaseStatusEnum.cancelada
            self.db.commit()
            
            self.logger.log_system('purchase_manager', 'purchase_cancelled', {
                'purchase_code': purchase_code
            })
            
            return {
                'status': 'cancelada',
                'message': 'Compra cancelada com sucesso',
                'purchase_code': purchase_code
            }
            
        except Exception as e:
            self.logger.log_error('purchase_manager', 'cancel_purchase_error', {
                'error': str(e),
                'purchase_code': purchase_code
            })
            raise
    
    def get_purchases_by_atm(self, atm_id: str, limit: int = 50) -> Dict[str, Any]:
        """Obtém compras de um ATM específico"""
        try:
            purchases = self.db.query(Purchase).filter(
                Purchase.atm_id == atm_id
            ).order_by(Purchase.created_at.desc()).limit(limit).all()
            
            return {
                'purchases': [
                    {
                        'purchase_code': p.purchase_code,
                        'status': p.status.value,
                        'amount_ars': p.amount_ars,
                        'crypto_amount': p.crypto_amount,
                        'crypto_type': p.crypto_type.value,
                        'created_at': p.created_at.isoformat(),
                        'expires_at': p.expires_at.isoformat()
                    }
                    for p in purchases
                ],
                'total': len(purchases)
            }
            
        except Exception as e:
            self.logger.log_error('purchase_manager', 'get_purchases_error', {
                'error': str(e),
                'atm_id': atm_id
            })
            raise 