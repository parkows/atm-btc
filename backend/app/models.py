from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class SessionStatusEnum(str, enum.Enum):
    aguardando_pagamento = "aguardando_pagamento"
    concluida = "concluida"
    expirada = "expirada"

class InvoiceStatusEnum(str, enum.Enum):
    aguardando = "aguardando"
    pago = "pago"
    expirado = "expirado"

class CryptoTypeEnum(str, enum.Enum):
    BTC = "BTC"
    USDT = "USDT"

class NetworkTypeEnum(str, enum.Enum):
    Lightning = "Lightning"
    TRC20 = "TRC20"

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_code = Column(String, unique=True, index=True, nullable=False)
    atm_id = Column(String, nullable=False)
    crypto_type = Column(Enum(CryptoTypeEnum), nullable=False, default=CryptoTypeEnum.BTC)
    network_type = Column(Enum(NetworkTypeEnum), nullable=False, default=NetworkTypeEnum.Lightning)
    status = Column(Enum(SessionStatusEnum), default=SessionStatusEnum.aguardando_pagamento)
    amount_ars = Column(Float, nullable=False)
    crypto_amount = Column(Float, nullable=False)
    invoice = Column(String, nullable=True)
    invoice_status = Column(Enum(InvoiceStatusEnum), default=InvoiceStatusEnum.aguardando)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    crypto_type = Column(Enum(CryptoTypeEnum), nullable=False)
    network_type = Column(Enum(NetworkTypeEnum), nullable=False)
    status = Column(String, nullable=False)
    tx_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
