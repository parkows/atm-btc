from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.schemas import (
    SessionCreateRequest, SessionCreateResponse, SessionStatusResponse,
    InvoiceAssociationRequest, InvoiceAssociationResponse, PaymentStatusResponse,
    QuoteRequest, QuoteResponse, SupportedCryptosResponse, StandardResponse
)
from app.deps import session_manager, SessionLocal
from app.core.crypto_manager import crypto_manager
from app.models import Session as SessionModel
from datetime import datetime

router = APIRouter()

@router.get("/supported-cryptos", response_model=SupportedCryptosResponse)
def get_supported_cryptos():
    """Obtém lista de criptomoedas suportadas"""
    try:
        cryptos = crypto_manager.get_supported_cryptos()
        return SupportedCryptosResponse(cryptos=cryptos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter criptomoedas suportadas: {str(e)}")

@router.post("/quote", response_model=QuoteResponse)
def get_quote(request: QuoteRequest):
    """Obtém cotação para qualquer criptomoeda"""
    try:
        quote_data = crypto_manager.get_quote(request.crypto_type, request.amount_ars)
        return QuoteResponse(**quote_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quote/{crypto_type}")
def get_quote_legacy(crypto_type: str, amount_ars: float):
    """Endpoint legado para cotação (mantido para compatibilidade)"""
    try:
        quote_data = crypto_manager.get_quote(crypto_type, amount_ars)
        return quote_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session", response_model=SessionCreateResponse)
def create_session(request: SessionCreateRequest):
    """Cria uma nova sessão de transação"""
    try:
        return session_manager.create_session(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/{session_code}", response_model=SessionStatusResponse)
def get_session_status(session_code: str):
    """Obtém status de uma sessão"""
    try:
        return session_manager.get_status(session_code)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/session/{session_code}/invoice", response_model=InvoiceAssociationResponse)
def associate_invoice(session_code: str, request: InvoiceAssociationRequest):
    """Associa invoice a uma sessão"""
    try:
        return session_manager.associate_invoice(session_code, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/session/{session_code}/payment-status", response_model=PaymentStatusResponse)
def get_payment_status(session_code: str):
    """Obtém status do pagamento"""
    try:
        return session_manager.get_payment_status(session_code)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/session/{session_code}/invoice-status")
def update_invoice_status(session_code: str, invoice_status: str):
    """Atualiza status do invoice"""
    try:
        session_manager.update_invoice_status(session_code, invoice_status)
        return StandardResponse(detail=f"Status do invoice atualizado para {invoice_status}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions")
def list_sessions(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    atm_id: Optional[str] = Query(None, description="Filtrar por ATM ID"),
    crypto_type: Optional[str] = Query(None, description="Filtrar por tipo de criptomoeda"),
    network_type: Optional[str] = Query(None, description="Filtrar por tipo de rede"),
    date_from: Optional[str] = Query(None, description="Data inicial (ISO format)"),
    date_to: Optional[str] = Query(None, description="Data final (ISO format)")
):
    """Lista sessões com filtros opcionais"""
    try:
        db: DBSession = SessionLocal()
        query = db.query(SessionModel)
        
        if status:
            query = query.filter(SessionModel.status == status)
        if atm_id:
            query = query.filter(SessionModel.atm_id == atm_id)
        if crypto_type:
            query = query.filter(SessionModel.crypto_type == crypto_type)
        if network_type:
            query = query.filter(SessionModel.network_type == network_type)
        if date_from:
            query = query.filter(SessionModel.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(SessionModel.created_at <= datetime.fromisoformat(date_to))
        
        sessions = query.order_by(SessionModel.created_at.desc()).all()
        db.close()
        
        return [
            {
                "session_code": s.session_code,
                "atm_id": s.atm_id,
                "crypto_type": s.crypto_type.value,
                "network_type": s.network_type.value,
                "status": s.status.value,
                "amount_ars": s.amount_ars,
                "crypto_amount": s.crypto_amount,
                "invoice": s.invoice,
                "invoice_status": s.invoice_status.value if s.invoice_status else None,
                "created_at": s.created_at,
                "expires_at": s.expires_at
            }
            for s in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar sessões: {str(e)}")
