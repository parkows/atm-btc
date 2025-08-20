"""
Endpoints da API para funcionalidades de SMS
Integração com o sistema LiquidGold ATM
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional
from pydantic import BaseModel
import logging

from app.core.sms_manager import sms_manager
from app.core.auth import auth_manager

# Configurar logger
logger = logging.getLogger(__name__)

# Router para SMS
router = APIRouter()

# Schemas para SMS
class SMSVerificationRequest(BaseModel):
    phone_number: str
    atm_id: str

class SMSVerificationResponse(BaseModel):
    success: bool
    message: str
    verification_code: Optional[str] = None
    expires_in_minutes: int = 10

class SMSVerificationCodeRequest(BaseModel):
    phone_number: str
    code: str
    atm_id: str

class SMSVerificationCodeResponse(BaseModel):
    success: bool
    message: str
    verified: bool

class SMSSendRequest(BaseModel):
    phone_number: str
    message: str
    reference: Optional[str] = None

class SMSSendResponse(BaseModel):
    success: bool
    message: str
    message_id: Optional[str] = None
    status: Optional[str] = None

class SMSTransactionConfirmationRequest(BaseModel):
    phone_number: str
    transaction_data: Dict

class SMSWalletRequest(BaseModel):
    phone_number: str
    crypto_type: str
    amount_ars: float

class SMSStatusUpdateRequest(BaseModel):
    phone_number: str
    status: str
    transaction_id: str

@router.post("/send-verification", response_model=SMSVerificationResponse)
async def send_verification_code(request: SMSVerificationRequest):
    """
    Envia código de verificação por SMS
    """
    try:
        # Gerar código de verificação
        verification_code = sms_manager.generate_verification_code()
        
        # Enviar SMS
        result = sms_manager.send_verification_code(
            phone_number=request.phone_number,
            code=verification_code,
            expires_in_minutes=10
        )
        
        if result["success"]:
            logger.info(f"Código de verificação enviado para {request.phone_number}")
            
            # Em produção, armazenar o código no banco/Redis
            # Por enquanto, retornamos o código (apenas para desenvolvimento)
            
            return SMSVerificationResponse(
                success=True,
                message="Código de verificação enviado com sucesso",
                verification_code=verification_code,  # Remover em produção
                expires_in_minutes=10
            )
        else:
            logger.error(f"Erro ao enviar código: {result.get('error')}")
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao enviar SMS: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.post("/verify-code", response_model=SMSVerificationCodeResponse)
async def verify_verification_code(request: SMSVerificationCodeRequest):
    """
    Verifica código de verificação enviado por SMS
    """
    try:
        # Em produção, verificar o código no banco/Redis
        # Por enquanto, aceitamos qualquer código de 6 dígitos
        
        if len(request.code) == 6 and request.code.isdigit():
            logger.info(f"Código verificado com sucesso para {request.phone_number}")
            
            return SMSVerificationCodeResponse(
                success=True,
                message="Código verificado com sucesso",
                verified=True
            )
        else:
            return SMSVerificationCodeResponse(
                success=False,
                message="Código inválido",
                verified=False
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.post("/send", response_model=SMSSendResponse)
async def send_sms(request: SMSSendRequest):
    """
    Envia SMS personalizado
    """
    try:
        result = sms_manager.send_sms(
            phone_number=request.phone_number,
            message=request.message,
            reference=request.reference
        )
        
        if result["success"]:
            return SMSSendResponse(
                success=True,
                message="SMS enviado com sucesso",
                message_id=result.get("message_id"),
                status=result.get("status")
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao enviar SMS: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.post("/transaction-confirmation")
async def send_transaction_confirmation(request: SMSTransactionConfirmationRequest):
    """
    Envia confirmação de transação por SMS
    """
    try:
        result = sms_manager.send_transaction_confirmation(
            phone_number=request.phone_number,
            transaction_data=request.transaction_data
        )
        
        if result["success"]:
            logger.info(f"Confirmação de transação enviada para {request.phone_number}")
            return {
                "success": True,
                "message": "Confirmação de transação enviada",
                "message_id": result.get("message_id")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao enviar confirmação: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.post("/wallet-request")
async def send_wallet_request(request: SMSWalletRequest):
    """
    Solicita endereço da wallet por SMS
    """
    try:
        result = sms_manager.send_wallet_request(
            phone_number=request.phone_number,
            crypto_type=request.crypto_type,
            amount_ars=request.amount_ars
        )
        
        if result["success"]:
            logger.info(f"Solicitação de carteira enviada para {request.phone_number}")
            return {
                "success": True,
                "message": "Solicitação de carteira enviada",
                "message_id": result.get("message_id")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao enviar solicitação: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.post("/status-update")
async def send_status_update(request: SMSStatusUpdateRequest):
    """
    Envia atualização de status por SMS
    """
    try:
        result = sms_manager.send_transaction_status_update(
            phone_number=request.phone_number,
            status=request.status,
            transaction_id=request.transaction_id
        )
        
        if result["success"]:
            logger.info(f"Atualização de status enviada para {request.phone_number}")
            return {
                "success": True,
                "message": "Atualização de status enviada",
                "message_id": result.get("message_id")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao enviar atualização: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.get("/status/{message_id}")
async def get_sms_status(message_id: str):
    """
    Obtém status de um SMS enviado
    """
    try:
        result = sms_manager.get_sms_status(message_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao consultar status: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.get("/balance")
async def get_sms_balance():
    """
    Obtém saldo da conta Infobip
    """
    try:
        result = sms_manager.get_balance()
        
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao consultar saldo: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.get("/health")
async def sms_health_check():
    """
    Verifica saúde do sistema de SMS
    """
    return {
        "service": "SMS Manager",
        "status": "healthy" if sms_manager.enabled else "disabled",
        "provider": "Infobip",
        "timestamp": sms_manager.get_balance().get("checked_at", "N/A")
    }
