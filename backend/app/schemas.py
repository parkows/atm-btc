from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SessionCreateRequest(BaseModel):
    atm_id: str = Field(..., description="ID do ATM")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_type: str = Field(..., description="Tipo de criptomoeda (BTC ou USDT)")
    transaction_type: str = Field(default="VENDA", description="Tipo de transação (VENDA ou COMPRA)")

class SessionCreateResponse(BaseModel):
    session_code: str = Field(..., description="Código da sessão")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    crypto_type: str = Field(..., description="Tipo de criptomoeda")
    network_type: str = Field(..., description="Tipo de rede")
    transaction_type: str = Field(..., description="Tipo de transação")
    expires_at: datetime = Field(..., description="Data de expiração")
    invoice: str = Field(..., description="Endereço do invoice")

class SessionStatusResponse(BaseModel):
    session_code: str = Field(..., description="Código da sessão")
    status: str = Field(..., description="Status da sessão")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    crypto_type: str = Field(..., description="Tipo de criptomoeda")
    network_type: str = Field(..., description="Tipo de rede")
    transaction_type: str = Field(..., description="Tipo de transação")
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
    transaction_type: str = Field(..., description="Tipo de transação")

# Novos schemas para COMPRA
class PurchaseCreateRequest(BaseModel):
    atm_id: str = Field(..., description="ID do ATM")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_type: str = Field(..., description="Tipo de criptomoeda (BTC ou USDT)")
    crypto_address: str = Field(..., description="Endereço para receber criptomoeda")
    ars_payment_method: str = Field(..., description="Método de pagamento ARS")

class PurchaseCreateResponse(BaseModel):
    purchase_code: str = Field(..., description="Código da compra")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    crypto_type: str = Field(..., description="Tipo de criptomoeda")
    network_type: str = Field(..., description="Tipo de rede")
    crypto_address: str = Field(..., description="Endereço para receber criptomoeda")
    ars_payment_method: str = Field(..., description="Método de pagamento ARS")
    expires_at: datetime = Field(..., description="Data de expiração")

class PurchaseStatusResponse(BaseModel):
    purchase_code: str = Field(..., description="Código da compra")
    status: str = Field(..., description="Status da compra")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    crypto_type: str = Field(..., description="Tipo de criptomoeda")
    network_type: str = Field(..., description="Tipo de rede")
    crypto_address: str = Field(..., description="Endereço para receber criptomoeda")
    ars_payment_method: str = Field(..., description="Método de pagamento ARS")
    created_at: datetime = Field(..., description="Data de criação")
    expires_at: datetime = Field(..., description="Data de expiração")
    completed_at: Optional[datetime] = Field(None, description="Data de conclusão")

class QuoteRequest(BaseModel):
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    crypto_type: str = Field(..., description="Tipo de criptomoeda (BTC ou USDT)")
    transaction_type: str = Field(default="VENDA", description="Tipo de transação (VENDA ou COMPRA)")

class QuoteResponse(BaseModel):
    crypto: str = Field(..., description="Tipo de criptomoeda")
    network: str = Field(..., description="Tipo de rede")
    crypto_ars_price: float = Field(..., description="Preço da criptomoeda em ARS")
    amount_ars: float = Field(..., description="Valor em pesos argentinos")
    valor_liquido_ars: float = Field(..., description="Valor líquido em ARS")
    crypto_amount: float = Field(..., description="Quantidade de criptomoeda")
    service_fee_percent: float = Field(..., description="Taxa de serviço em %")
    service_fee_ars: float = Field(..., description="Taxa de serviço em ARS")
    transaction_type: str = Field(..., description="Tipo de transação")

class SupportedCryptosResponse(BaseModel):
    cryptos: dict = Field(..., description="Criptomoedas suportadas")

class StandardResponse(BaseModel):
    detail: str = Field(..., description="Mensagem de resposta")
