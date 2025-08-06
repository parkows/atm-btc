#!/usr/bin/env python3
"""
Rotas de Backup - LiquidGold ATM
Implementação de endpoints para gerenciamento de backups
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from app.core.backup_manager import backup_manager
from app.core.auth import auth_manager
from app.core.logger import atm_logger

router = APIRouter()

@router.post("/create", response_model=Dict[str, Any])
async def create_backup(
    backup_type: str = "manual",
    current_user: Dict[str, Any] = Depends(auth_manager.get_current_superuser)
):
    """
    Cria um backup do sistema (apenas superusuários)
    """
    try:
        # Validar tipo de backup
        if backup_type not in ["daily", "weekly", "monthly", "manual"]:
            backup_type = "manual"
        
        # Criar backup
        result = backup_manager.create_backup(backup_type)
        
        # Registrar ação de auditoria
        from app.core.audit import audit_manager
        audit_manager.log_event(
            action="CREATE_BACKUP",
            resource="backup",
            user_id=current_user["username"],
            details={
                "backup_type": backup_type,
                "result": result
            },
            status="success" if result["success"] else "failure"
        )
        
        return result
        
    except Exception as e:
        atm_logger.log_error('backup_api', 'create_backup_error', {'error': str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar backup: {str(e)}"
        )

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_backups(
    backup_type: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(auth_manager.get_current_superuser)
):
    """
    Lista backups disponíveis (apenas superusuários)
    """
    try:
        # Listar backups
        backups = backup_manager.list_backups(backup_type)
        
        return backups
        
    except Exception as e:
        atm_logger.log_error('backup_api', 'list_backups_error', {'error': str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar backups: {str(e)}"
        )

@router.post("/restore", response_model=Dict[str, Any])
async def restore_backup(
    backup_path: str,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(auth_manager.get_current_superuser)
):
    """
    Restaura um backup (apenas superusuários)
    ATENÇÃO: Esta operação substitui dados existentes
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(backup_path) or not backup_path.endswith(".zip"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo de backup inválido"
            )
        
        # Registrar ação de auditoria antes da restauração
        from app.core.audit import audit_manager
        audit_manager.log_event(
            action="RESTORE_BACKUP",
            resource="backup",
            resource_id=os.path.basename(backup_path),
            user_id=current_user["username"],
            details={
                "backup_path": backup_path,
                "timestamp": datetime.now().isoformat()
            },
            status="success"
        )
        
        # Executar restauração em background para não bloquear a API
        def restore_task():
            try:
                result = backup_manager.restore_backup(backup_path)
                
                # Registrar resultado
                atm_logger.log_system('backup', 'restore_completed', {
                    'backup_path': backup_path,
                    'success': result["success"],
                    'error': result.get("error")
                })
                
            except Exception as e:
                atm_logger.log_error('backup', 'restore_task_error', {'error': str(e)})
        
        # Adicionar tarefa em background
        background_tasks.add_task(restore_task)
        
        return {
            "success": True,
            "message": "Restauração iniciada em background",
            "backup_path": backup_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        atm_logger.log_error('backup_api', 'restore_backup_error', {'error': str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao restaurar backup: {str(e)}"
        )

@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_backups(
    current_user: Dict[str, Any] = Depends(auth_manager.get_current_superuser)
):
    """
    Remove backups antigos conforme política de retenção (apenas superusuários)
    """
    try:
        # Limpar backups antigos
        result = backup_manager.cleanup_old_backups()
        
        # Registrar ação de auditoria
        from app.core.audit import audit_manager
        audit_manager.log_event(
            action="CLEANUP_BACKUPS",
            resource="backup",
            user_id=current_user["username"],
            details=result,
            status="success" if result["success"] else "failure"
        )
        
        return result
        
    except Exception as e:
        atm_logger.log_error('backup_api', 'cleanup_backups_error', {'error': str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao limpar backups antigos: {str(e)}"
        )