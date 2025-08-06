#!/usr/bin/env python3
"""
Rotas de Autenticação - LiquidGold ATM
Implementação de endpoints para autenticação e gerenciamento de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, List
from datetime import timedelta
from sqlalchemy.orm import Session

from app.deps import get_db
from app.core.auth import auth_manager, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.logger import atm_logger

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login para obter token JWT
    """
    user = auth_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        atm_logger.log_security('auth', 'login_failed', {
            'username': form_data.username,
            'ip': 'request.client.host'  # Implementar obtenção do IP real
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_manager.create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    atm_logger.log_security('auth', 'login_success', {
        'username': form_data.username,
        'ip': 'request.client.host'  # Implementar obtenção do IP real
    })
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=Dict[str, Any])
async def read_users_me(current_user: Dict[str, Any] = Depends(auth_manager.get_current_active_user)):
    """
    Retorna informações do usuário atual
    """
    return {
        "username": current_user["username"],
        "is_superuser": current_user["is_superuser"]
    }

@router.post("/users", response_model=Dict[str, Any])
async def create_user(
    username: str,
    password: str,
    is_superuser: bool = False,
    current_user: Dict[str, Any] = Depends(auth_manager.get_current_superuser)
):
    """
    Cria novo usuário (apenas superusuários)
    """
    try:
        user = auth_manager.add_user(username, password, is_superuser)
        return {
            "username": user["username"],
            "is_active": user["is_active"],
            "is_superuser": user["is_superuser"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: Dict[str, Any] = Depends(auth_manager.get_current_active_user)
):
    """
    Altera senha do usuário atual
    """
    # Verificar senha atual
    if not auth_manager.verify_password(current_password, current_user["hashed_password"]):
        atm_logger.log_security('auth', 'change_password_failed', {
            'username': current_user["username"],
            'reason': 'incorrect_current_password'
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Atualizar senha
    username = current_user["username"]
    current_user["hashed_password"] = auth_manager.get_password_hash(new_password)
    auth_manager.users_db[username] = current_user
    
    atm_logger.log_security('auth', 'change_password_success', {
        'username': username
    })
    
    return {"detail": "Senha alterada com sucesso"}