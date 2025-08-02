#!/usr/bin/env python3
"""
APIs do ATM - LiquidGold
Endpoints para operações de venda e compra de criptomoedas
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..deps import get_db
from ..schemas import (
    SessionCreateRequest, SessionCreateResponse, SessionStatusResponse,
    PaymentStatusResponse, QuoteRequest, QuoteResponse, SupportedCryptosResponse,
    PurchaseCreateRequest, PurchaseCreateResponse, PurchaseStatusResponse
)
from ..core.session_manager import SessionManager
from ..core.purchase_manager import PurchaseManager
from ..core.crypto_manager import CryptoManager
from ..core.logger import atm_logger

router = APIRouter(prefix="/api/atm", tags=["ATM Operations"])

# Instâncias globais
crypto_manager = CryptoManager()

@router.get("/supported-cryptos", response_model=SupportedCryptosResponse)
async def get_supported_cryptos():
    """Lista criptomoedas suportadas"""
    try:
        return crypto_manager.get_supported_cryptos()
    except Exception as e:
        atm_logger.log_error('api', 'supported_cryptos_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quote", response_model=QuoteResponse)
async def get_quote(request: QuoteRequest):
    """Obtém cotação para criptomoeda"""
    try:
        quote_data = crypto_manager.get_quote(
            request.crypto_type, 
            request.amount_ars,
            request.transaction_type
        )
        return QuoteResponse(**quote_data)
    except Exception as e:
        atm_logger.log_error('api', 'quote_error', {
            'crypto_type': request.crypto_type,
            'amount_ars': request.amount_ars,
            'transaction_type': request.transaction_type,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest, db: Session = Depends(get_db)):
    """Cria sessão de venda de criptomoeda"""
    try:
        session_manager = SessionManager(db)
        response = session_manager.create_session(request)
        return response
    except Exception as e:
        atm_logger.log_error('api', 'create_session_error', {
            'atm_id': request.atm_id,
            'amount_ars': request.amount_ars,
            'crypto_type': request.crypto_type,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_code}", response_model=SessionStatusResponse)
async def get_session_status(session_code: str, db: Session = Depends(get_db)):
    """Obtém status de uma sessão"""
    try:
        session_manager = SessionManager(db)
        response = session_manager.get_session_status(session_code)
        return response
    except Exception as e:
        atm_logger.log_error('api', 'session_status_error', {
            'session_code': session_code,
            'error': str(e)
        })
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/sessions/{session_code}/payment-status", response_model=PaymentStatusResponse)
async def check_payment_status(session_code: str, db: Session = Depends(get_db)):
    """Verifica status do pagamento de uma sessão"""
    try:
        session_manager = SessionManager(db)
        response = session_manager.check_payment_status(session_code)
        return response
    except Exception as e:
        atm_logger.log_error('api', 'payment_status_error', {
            'session_code': session_code,
            'error': str(e)
        })
        raise HTTPException(status_code=404, detail=str(e))

# Novos endpoints para COMPRA
@router.post("/purchases", response_model=PurchaseCreateResponse)
async def create_purchase(request: PurchaseCreateRequest, db: Session = Depends(get_db)):
    """Cria uma nova compra de criptomoeda"""
    try:
        purchase_manager = PurchaseManager(db)
        response = purchase_manager.create_purchase(
            atm_id=request.atm_id,
            amount_ars=request.amount_ars,
            crypto_type=request.crypto_type,
            crypto_address=request.crypto_address,
            ars_payment_method=request.ars_payment_method
        )
        return PurchaseCreateResponse(**response)
    except Exception as e:
        atm_logger.log_error('api', 'create_purchase_error', {
            'atm_id': request.atm_id,
            'amount_ars': request.amount_ars,
            'crypto_type': request.crypto_type,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/purchases/{purchase_code}", response_model=PurchaseStatusResponse)
async def get_purchase_status(purchase_code: str, db: Session = Depends(get_db)):
    """Obtém status de uma compra"""
    try:
        purchase_manager = PurchaseManager(db)
        response = purchase_manager.get_purchase_status(purchase_code)
        return PurchaseStatusResponse(**response)
    except Exception as e:
        atm_logger.log_error('api', 'purchase_status_error', {
            'purchase_code': purchase_code,
            'error': str(e)
        })
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/purchases/{purchase_code}/check-crypto")
async def check_crypto_received(purchase_code: str, db: Session = Depends(get_db)):
    """Verifica se a criptomoeda foi recebida"""
    try:
        purchase_manager = PurchaseManager(db)
        response = purchase_manager.check_crypto_received(purchase_code)
        return response
    except Exception as e:
        atm_logger.log_error('api', 'check_crypto_error', {
            'purchase_code': purchase_code,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/purchases/{purchase_code}/confirm-ars")
async def confirm_ars_payment(purchase_code: str, db: Session = Depends(get_db)):
    """Confirma pagamento em ARS e finaliza a compra"""
    try:
        purchase_manager = PurchaseManager(db)
        response = purchase_manager.confirm_ars_payment(purchase_code)
        return response
    except Exception as e:
        atm_logger.log_error('api', 'confirm_ars_error', {
            'purchase_code': purchase_code,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/purchases/{purchase_code}/cancel")
async def cancel_purchase(purchase_code: str, db: Session = Depends(get_db)):
    """Cancela uma compra"""
    try:
        purchase_manager = PurchaseManager(db)
        response = purchase_manager.cancel_purchase(purchase_code)
        return response
    except Exception as e:
        atm_logger.log_error('api', 'cancel_purchase_error', {
            'purchase_code': purchase_code,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/purchases/atm/{atm_id}")
async def get_purchases_by_atm(atm_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Obtém compras de um ATM específico"""
    try:
        purchase_manager = PurchaseManager(db)
        response = purchase_manager.get_purchases_by_atm(atm_id, limit)
        return response
    except Exception as e:
        atm_logger.log_error('api', 'get_purchases_error', {
            'atm_id': atm_id,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints legados para compatibilidade
@router.get("/quote/{crypto_type}")
async def get_quote_legacy(crypto_type: str, amount_ars: float):
    """Endpoint legado para cotação"""
    try:
        quote_data = crypto_manager.get_quote(crypto_type, amount_ars, "VENDA")
        return quote_data
    except Exception as e:
        atm_logger.log_error('api', 'quote_legacy_error', {
            'crypto_type': crypto_type,
            'amount_ars': amount_ars,
            'error': str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))
