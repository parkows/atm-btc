#!/usr/bin/env python3
"""
Modelos de Banco de Dados - LiquidGold ATM
Define os modelos SQLAlchemy para o sistema
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    """
    Modelo para usuários do sistema
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Transaction(Base):
    """
    Modelo para transações (vendas e compras)
    """
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_code = Column(String(50), unique=True, index=True, nullable=False)
    transaction_type = Column(String(20), index=True, nullable=False)  # VENDA ou COMPRA
    crypto_type = Column(String(10), index=True, nullable=False)  # BTC ou USDT
    amount_ars = Column(Float, nullable=False)
    amount_crypto = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    fee_percent = Column(Float, nullable=False)
    fee_amount = Column(Float, nullable=False)
    status = Column(String(20), index=True, nullable=False)  # PENDENTE, CONCLUIDA, CANCELADA, etc.
    crypto_address = Column(String(100), nullable=True)  # Para compras
    crypto_txid = Column(String(100), nullable=True)  # ID da transação na blockchain
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    completed_at = Column(DateTime, nullable=True)

class Session(Base):
    """
    Modelo para sessões de venda
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_code = Column(String(50), unique=True, index=True, nullable=False)
    crypto_type = Column(String(10), index=True, nullable=False)  # BTC ou USDT
    amount_ars = Column(Float, nullable=False)
    amount_crypto = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    invoice = Column(String(255), nullable=True)  # Lightning invoice ou endereço TRC20
    status = Column(String(20), index=True, nullable=False)  # PENDENTE, PAGO, EXPIRADO, etc.
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)

class Config(Base):
    """
    Modelo para configurações do sistema
    """
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)  # JSON serializado
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class AuditLog(Base):
    """
    Modelo para logs de auditoria
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    user_id = Column(String(50), index=True, nullable=True)  # Username ou ID do usuário
    action = Column(String(50), index=True, nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource = Column(String(50), index=True, nullable=False)  # Recurso afetado (transaction, user, config, etc.)
    resource_id = Column(String(50), index=True, nullable=True)  # ID do recurso afetado
    ip_address = Column(String(50), nullable=True)  # Endereço IP
    details = Column(JSON, nullable=True)  # Detalhes adicionais em JSON
    status = Column(String(20), index=True, nullable=False)  # success, failure, warning