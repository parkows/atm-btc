from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SessionCreateRequest(BaseModel):
    atm_id: str = Field(..., description="ID do ATM")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_type: str = Field(..., description="Tipo de criptomoeda (BTC ou USDT)")

class SessionCreateResponse(BaseModel):
    session_code: str = Field(..., description="Código da sessão")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    crypto_type: str = Field(..., description="Tipo de criptomoeda")
    network_type: str = Field(..., description="Tipo de rede")
    expires_at: datetime = Field(..., description="Data de expiração")
    invoice: str = Field(..., description="Endereço do invoice")

class SessionStatusResponse(BaseModel):
    session_code: str = Field(..., description="Código da sessão")
    status: str = Field(..., description="Status da sessão")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    crypto_type: str = Field(..., description="Tipo de criptomoeda")
    network_type: str = Field(..., description="Tipo de rede")
    invoice: str = Field(..., description="Endereço do invoice")
    invoice_status: str = Field(..., description="Status do invoice")
    created_at: datetime = Field(..., description="Data de criação")
    expires_at: datetime = Field(..., description="Data de expiração")

class InvoiceAssociationRequest(BaseModel):
    invoice: str = Field(..., description="Endereço do invoice")

class InvoiceAssociationResponse(BaseModel):
    session_code: str = Field(..., description="Código da sessão")
    invoice: str = Field(..., description="Endereço do invoice")
    status: str = Field(..., description="Status da associação")

class PaymentStatusResponse(BaseModel):
    session_code: str = Field(..., description="Código da sessão")
    payment_status: str = Field(..., description="Status do pagamento")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    crypto_type: str = Field(..., description="Tipo de criptomoeda")
    network_type: str = Field(..., description="Tipo de rede")

class QuoteRequest(BaseModel):
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_type: str = Field(..., description="Tipo de criptomoeda (BTC ou USDT)")

class QuoteResponse(BaseModel):
    crypto: str = Field(..., description="Tipo de criptomoeda")
    network: str = Field(..., description="Tipo de rede")
    crypto_ars_price: float = Field(..., description="Preço da criptomoeda em ARS")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    valor_liquido_ars: float = Field(..., description="Valor líquido em ARS")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    service_fee_percent: float = Field(..., description="Taxa de serviço em %")
    service_fee_ars: float = Field(..., description="Taxa de serviço em ARS")

class SupportedCryptosResponse(BaseModel):
    cryptos: dict = Field(..., description="Criptomoedas suportadas")

class StandardResponse(BaseModel):
    detail: str = Field(..., description="Mensagem de resposta")
