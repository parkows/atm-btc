#!/usr/bin/env python3
"""
Inicialização do Banco de Dados - LiquidGold ATM
Este script inicializa o banco de dados com dados iniciais necessários
para o funcionamento do sistema, como usuários administrativos.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, List, Optional
import os
import json
from datetime import datetime

from app.db.models import User, Config
from app.core.auth import auth_manager
from app.core.logger import atm_logger
from app.core.config import atm_config

async def init_users(db: AsyncSession) -> None:
    """
    Inicializa usuários administrativos no banco de dados
    """
    try:
        # Verificar se já existem usuários
        result = await db.execute(select(User).limit(1))
        existing_user = result.scalars().first()
        
        if existing_user:
            atm_logger.log_system('init_db', 'users_already_exist', {})
            return
        
        # Criar usuário admin padrão
        admin_password = os.environ.get("ADMIN_INITIAL_PASSWORD", "admin123")
        hashed_password = auth_manager.get_password_hash(admin_password)
        
        admin_user = User(
            username="admin",
            email="admin@liquidgold.com",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(admin_user)
        await db.commit()
        
        atm_logger.log_system('init_db', 'admin_user_created', {
            'username': 'admin'
        })
        
    except Exception as e:
        await db.rollback()
        atm_logger.log_error('init_db', 'init_users_error', {'error': str(e)})
        raise

async def init_config(db: AsyncSession) -> None:
    """
    Inicializa configurações padrão no banco de dados
    """
    try:
        # Verificar se já existem configurações
        result = await db.execute(select(Config).limit(1))
        existing_config = result.scalars().first()
        
        if existing_config:
            atm_logger.log_system('init_db', 'config_already_exists', {})
            return
        
        # Carregar configurações padrão
        default_config = {
            "maintenance_mode": False,
            "rate_limits": {
                "global": 1000,
                "ip": 100,
                "login": 5,
                "api": 50,
                "admin": 20
            },
            "security": {
                "jwt_expiration_minutes": 60,
                "password_min_length": 8,
                "require_special_chars": True,
                "require_numbers": True,
                "require_uppercase": True
            },
            "backup": {
                "daily_retention_days": 7,
                "weekly_retention_weeks": 4,
                "monthly_retention_months": 6,
                "backup_time": "03:00"
            },
            "notifications": {
                "email_enabled": False,
                "telegram_enabled": False,
                "slack_enabled": False
            }
        }
        
        # Criar configuração no banco
        config_entry = Config(
            key="system_config",
            value=json.dumps(default_config),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(config_entry)
        await db.commit()
        
        # Atualizar configuração em memória
        atm_config.load_from_dict(default_config)
        
        atm_logger.log_system('init_db', 'default_config_created', {})
        
    except Exception as e:
        await db.rollback()
        atm_logger.log_error('init_db', 'init_config_error', {'error': str(e)})
        raise

async def init_db(db: AsyncSession) -> None:
    """
    Inicializa o banco de dados com dados iniciais
    """
    try:
        atm_logger.log_system('init_db', 'starting_db_initialization', {})
        
        # Inicializar usuários
        await init_users(db)
        
        # Inicializar configurações
        await init_config(db)
        
        atm_logger.log_system('init_db', 'db_initialization_completed', {})
        
    except Exception as e:
        atm_logger.log_error('init_db', 'init_db_error', {'error': str(e)})
        raise

# Função para executar a inicialização diretamente
def run_init_db():
    """
    Executa a inicialização do banco de dados
    """
    from app.deps import get_db_session
    
    async def _run_init():
        async with get_db_session() as db:
            await init_db(db)
    
    asyncio.run(_run_init())

# Executar se chamado diretamente
if __name__ == "__main__":
    run_init_db()