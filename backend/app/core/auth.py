#!/usr/bin/env python3
"""
Sistema de Autenticação - LiquidGold ATM
Implementação de autenticação JWT para segurança da API
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.logger import atm_logger
from app.core.config import atm_config

# Configurações de segurança
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "liquidgold_atm_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Esquema de autenticação OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")

# Contexto de criptografia para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    """
    Gerenciador de autenticação e autorização
    """
    
    def __init__(self):
        self.logger = atm_logger
        self.config = atm_config
        
        # Usuário admin padrão (deve ser alterado em produção)
        self.default_admin = {
            "username": "admin",
            "hashed_password": pwd_context.hash("admin123"),
            "is_active": True,
            "is_superuser": True
        }
        
        # Cache de usuários (em memória)
        self.users_db = {"admin": self.default_admin}
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha está correta
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Gera hash da senha
        """
        return pwd_context.hash(password)
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Obtém usuário pelo username
        """
        if username in self.users_db:
            return self.users_db[username]
        return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário
        """
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        if not user["is_active"]:
            return None
        return user
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Cria token JWT
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
        """
        Obtém usuário atual a partir do token JWT
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception
        
        user = self.get_user(username)
        if user is None:
            raise credentials_exception
        
        return user
    
    async def get_current_active_user(self, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """
        Verifica se o usuário está ativo
        """
        if not current_user["is_active"]:
            raise HTTPException(status_code=400, detail="Usuário inativo")
        return current_user
    
    async def get_current_superuser(self, current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        """
        Verifica se o usuário é superusuário
        """
        if not current_user["is_superuser"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente"
            )
        return current_user
    
    def add_user(self, username: str, password: str, is_superuser: bool = False) -> Dict[str, Any]:
        """
        Adiciona novo usuário
        """
        if username in self.users_db:
            raise ValueError(f"Usuário {username} já existe")
        
        hashed_password = self.get_password_hash(password)
        
        user = {
            "username": username,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_superuser": is_superuser
        }
        
        self.users_db[username] = user
        
        self.logger.log_security('auth', 'user_created', {
            'username': username,
            'is_superuser': is_superuser
        })
        
        return user

# Instância global
auth_manager = AuthManager()