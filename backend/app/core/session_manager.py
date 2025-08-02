import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from sqlalchemy.orm import Session as DBSession
from app.models import Session as SessionModel, SessionStatusEnum, InvoiceStatusEnum, CryptoTypeEnum, NetworkTypeEnum, TransactionTypeEnum
from app.schemas import (
    SessionCreateRequest, SessionCreateResponse, SessionStatusResponse,
    InvoiceAssociationRequest, InvoiceAssociationResponse, PaymentStatusResponse
)
import requests
import logging
from .config import atm_config
from .logger import atm_logger
from .notifications import notification_manager
from .security import SecurityManager
from .i18n import i18n_manager
from .crypto_manager import crypto_manager

class SessionManager:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.logger = atm_logger
        self.notifications = notification_manager
        self.config = atm_config
        self.security_manager = SecurityManager(db_session_factory)
        self.crypto_manager = crypto_manager

    def create_session(self, request: SessionCreateRequest) -> SessionCreateResponse:
        """Cria uma nova sessão de transação"""
        try:
            # Log da criação da sessão
            self.logger.log_transaction('session_created', 'session_creation_started', {
                'atm_id': request.atm_id,
                'amount_ars': request.amount_ars,
                'crypto_type': request.crypto_type,
                'transaction_type': request.transaction_type,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Validar criptomoeda
            if request.crypto_type not in ['BTC', 'USDT']:
                raise Exception(f"Criptomoeda {request.crypto_type} não suportada")
            
            # Validar tipo de transação
            if request.transaction_type not in ['VENDA', 'COMPRA']:
                raise Exception(f"Tipo de transação {request.transaction_type} não suportado")
            
            # Validar limites usando crypto manager
            if not self.crypto_manager.validate_amount(request.crypto_type, request.amount_ars):
                supported_cryptos = self.crypto_manager.get_supported_cryptos()
                crypto_config = supported_cryptos['cryptos'][request.crypto_type]
                error_msg = f"Valor fora dos limites para {request.crypto_type} (${crypto_config['min_amount']:,.2f} a ${crypto_config['max_amount']:,.2f} ARS)"
                self.logger.log_security('invalid_amount', 'medium', {
                    'amount': request.amount_ars,
                    'crypto_type': request.crypto_type
                })
                raise Exception(error_msg)
            
            # Detecção de fraude
            fraud_check = self.security_manager.detect_fraud_patterns(
                f"session_{uuid.uuid4()}", 
                request.amount_ars
            )
            
            if fraud_check['blocked']:
                self.logger.log_security('fraud_blocked', 'high', {
                    'amount': request.amount_ars,
                    'crypto_type': request.crypto_type,
                    'transaction_type': request.transaction_type,
                    'fraud_score': fraud_check['fraud_score'],
                    'reasons': fraud_check['reasons']
                })
                raise Exception("Transação bloqueada por suspeita de fraude")
            
            # Criar sessão no banco
            db = self.db_session_factory()
            session_code = f"{uuid.uuid4().int % 1000:03d}-{uuid.uuid4().int % 1000:03d}"
            expires_at = datetime.utcnow() + timedelta(minutes=self.config.get('security.session_timeout_minutes', 5))
            
            # Obter cotação e criar invoice usando crypto manager
            invoice_data = self.crypto_manager.create_invoice(
                request.crypto_type, 
                request.amount_ars, 
                session_code,
                request.transaction_type
            )
            
            # Determinar tipos de enum
            crypto_type_enum = CryptoTypeEnum.BTC if request.crypto_type == 'BTC' else CryptoTypeEnum.USDT
            network_type_enum = NetworkTypeEnum.Lightning if request.crypto_type == 'BTC' else NetworkTypeEnum.TRC20
            transaction_type_enum = TransactionTypeEnum.VENDA if request.transaction_type == 'VENDA' else TransactionTypeEnum.COMPRA
            
            session = SessionModel(
                session_code=session_code,
                atm_id=request.atm_id,
                crypto_type=crypto_type_enum,
                network_type=network_type_enum,
                transaction_type=transaction_type_enum,
                status=SessionStatusEnum.aguardando_pagamento,
                amount_ars=request.amount_ars,
                crypto_amount=invoice_data['quote_data']['crypto_amount'],
                invoice=invoice_data['invoice'],
                invoice_status=InvoiceStatusEnum.aguardando,
                created_at=datetime.utcnow(),
                expires_at=expires_at
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # Log de sucesso
            self.logger.log_transaction('session_created', 'session_creation_success', {
                'session_code': session_code,
                'atm_id': request.atm_id,
                'amount_ars': request.amount_ars,
                'crypto_type': request.crypto_type,
                'transaction_type': request.transaction_type,
                'crypto_amount': invoice_data['quote_data']['crypto_amount']
            })
            
            # Notificação
            self.notifications.send_session_created(
                session_code=session_code,
                crypto_type=request.crypto_type,
                amount_ars=request.amount_ars,
                crypto_amount=invoice_data['quote_data']['crypto_amount'],
                transaction_type=request.transaction_type
            )
            
            return SessionCreateResponse(
                session_code=session_code,
                amount_ars=request.amount_ars,
                crypto_amount=invoice_data['quote_data']['crypto_amount'],
                crypto_type=request.crypto_type,
                network_type=network_type_enum.value,
                transaction_type=request.transaction_type,
                expires_at=expires_at,
                invoice=invoice_data['invoice']
            )
            
        except Exception as e:
            self.logger.log_error('session_manager', 'create_session_error', {
                'error': str(e),
                'atm_id': request.atm_id,
                'amount_ars': request.amount_ars,
                'crypto_type': request.crypto_type,
                'transaction_type': request.transaction_type
            })
            raise

    def get_status(self, session_code: str) -> SessionStatusResponse:
        """Obtém status de uma sessão"""
        try:
            db = self.db_session_factory()
            session = db.query(SessionModel).filter(SessionModel.session_code == session_code).first()
            
            if not session:
                raise Exception("Sessão não encontrada")
            
            # Verificar se expirou
            if datetime.utcnow() > session.expires_at:
                session.status = SessionStatusEnum.expirada
                db.commit()
            
            db.close()
            
            return SessionStatusResponse(
                session_code=session.session_code,
                status=session.status.value,
                amount_ars=session.amount_ars,
                crypto_amount=session.crypto_amount,
                crypto_type=session.crypto_type.value,
                network_type=session.network_type.value,
                invoice=session.invoice,
                invoice_status=session.invoice_status.value,
                created_at=session.created_at,
                expires_at=session.expires_at
            )
            
        except Exception as e:
            self.logger.log_transaction(session_code, 'status_check_failed', {'error': str(e)})
            raise e

    def associate_invoice(self, session_code: str, request: InvoiceAssociationRequest) -> InvoiceAssociationResponse:
        """Associa invoice a uma sessão"""
        try:
            db = self.db_session_factory()
            session = db.query(SessionModel).filter(SessionModel.session_code == session_code).first()
            
            if not session:
                db.close()
                raise Exception("Sessão não encontrada")
            
            if session.status != SessionStatusEnum.aguardando_pagamento:
                db.close()
                raise Exception("Sessão não está aguardando pagamento")
            
            # Atualizar invoice
            session.invoice = request.invoice
            session.invoice_status = InvoiceStatusEnum.aguardando
            db.commit()
            db.close()
            
            self.logger.log_transaction(session_code, 'invoice_associated', {
                'invoice': request.invoice,
                'crypto_type': session.crypto_type.value,
                'network_type': session.network_type.value
            })
            
            return InvoiceAssociationResponse(
                session_code=session_code,
                invoice=request.invoice,
                status="associated"
            )
            
        except Exception as e:
            if 'db' in locals():
                db.close()
            self.logger.log_transaction(session_code, 'invoice_association_failed', {'error': str(e)})
            raise e

    def get_payment_status(self, session_code: str) -> PaymentStatusResponse:
        """Obtém status do pagamento"""
        try:
            db = self.db_session_factory()
            session = db.query(SessionModel).filter(SessionModel.session_code == session_code).first()
            
            if not session:
                db.close()
                raise Exception("Sessão não encontrada")
            
            # Verificar pagamento usando crypto manager
            payment_status = "aguardando"
            if session.invoice_status == InvoiceStatusEnum.pago:
                payment_status = "pago"
            elif session.invoice_status == InvoiceStatusEnum.expirado:
                payment_status = "expirado"
            
            db.close()
            
            return PaymentStatusResponse(
                session_code=session_code,
                payment_status=payment_status,
                amount_ars=session.amount_ars,
                crypto_amount=session.crypto_amount,
                crypto_type=session.crypto_type.value,
                network_type=session.network_type.value
            )
            
        except Exception as e:
            if 'db' in locals():
                db.close()
            self.logger.log_transaction(session_code, 'payment_status_check_failed', {'error': str(e)})
            raise e

    def update_invoice_status(self, session_code: str, invoice_status: str) -> None:
        """Atualiza status do invoice"""
        try:
            db = self.db_session_factory()
            session = db.query(SessionModel).filter(SessionModel.session_code == session_code).first()
            
            if not session:
                db.close()
                raise Exception("Sessão não encontrada")
            
            # Atualizar status
            if invoice_status == "pago":
                session.invoice_status = InvoiceStatusEnum.pago
                session.status = SessionStatusEnum.concluida
                
                # Notificar pagamento recebido
                self.notifications.notify_transaction_completed({
                    'session_code': session_code,
                    'amount_ars': session.amount_ars,
                    'crypto_amount': session.crypto_amount,
                    'crypto_type': session.crypto_type.value,
                    'network_type': session.network_type.value
                })
                
            elif invoice_status == "expirado":
                session.invoice_status = InvoiceStatusEnum.expirado
                session.status = SessionStatusEnum.expirada
                
                # Notificar expiração
                self.notifications.notify_transaction_failed({
                    'session_code': session_code,
                    'reason': 'invoice_expired',
                    'crypto_type': session.crypto_type.value
                })
            
            db.commit()
            db.close()
            
            self.logger.log_transaction(session_code, 'invoice_status_updated', {
                'new_status': invoice_status,
                'crypto_type': session.crypto_type.value,
                'network_type': session.network_type.value
            })
            
        except Exception as e:
            if 'db' in locals():
                db.close()
            self.logger.log_transaction(session_code, 'invoice_status_update_failed', {'error': str(e)})
            raise e
