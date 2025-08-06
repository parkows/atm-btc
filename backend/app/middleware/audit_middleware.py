#!/usr/bin/env python3
"""
Middleware de Auditoria - LiquidGold ATM
Implementação de middleware para registrar automaticamente as requisições HTTP
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable, Dict, Any, Optional
import json

from app.core.audit import audit_manager
from app.core.logger import atm_logger

class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware para registrar automaticamente as requisições HTTP
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Obter informações da requisição
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"
        
        # Ignorar rotas que não precisam ser auditadas
        if self._should_skip_audit(path):
            return await call_next(request)
        
        # Extrair informações de autenticação (se disponível)
        user_id = await self._extract_user_id(request)
        
        # Registrar início da requisição
        start_time = time.time()
        
        # Determinar recurso com base no caminho
        resource = self._get_resource_from_path(path)
        resource_id = self._extract_resource_id(path)
        
        # Processar a requisição
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Determinar status com base no código de resposta
            status = "success"
            if response.status_code >= 400:
                status = "failure"
            elif response.status_code >= 300:
                status = "warning"
            
            # Registrar auditoria
            audit_manager.log_event(
                action=f"{method}_REQUEST",
                resource=resource,
                resource_id=resource_id,
                user_id=user_id,
                ip_address=client_ip,
                details={
                    'path': str(request.url),
                    'method': method,
                    'status_code': response.status_code,
                    'process_time_ms': round(process_time * 1000, 2)
                },
                status=status
            )
            
            return response
            
        except Exception as e:
            # Registrar erro
            process_time = time.time() - start_time
            
            audit_manager.log_event(
                action=f"{method}_REQUEST",
                resource=resource,
                resource_id=resource_id,
                user_id=user_id,
                ip_address=client_ip,
                details={
                    'path': str(request.url),
                    'method': method,
                    'error': str(e),
                    'process_time_ms': round(process_time * 1000, 2)
                },
                status="failure"
            )
            
            # Registrar erro no logger
            atm_logger.log_error('api', 'request_error', {
                'path': str(request.url),
                'method': method,
                'error': str(e)
            })
            
            # Re-lançar a exceção para ser tratada pelo FastAPI
            raise
    
    def _should_skip_audit(self, path: str) -> bool:
        """
        Verifica se a rota deve ser ignorada para auditoria
        """
        # Ignorar rotas de recursos estáticos
        if path.startswith("/static/"):
            return True
        
        # Ignorar rotas de documentação
        if path.startswith("/docs") or path.startswith("/redoc") or path == "/openapi.json":
            return True
        
        # Ignorar rotas de saúde e métricas (alto volume)
        if path == "/api/health" or path == "/api/metrics":
            return True
        
        return False
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """
        Extrai ID do usuário do token JWT (se disponível)
        """
        try:
            # Verificar se há token de autenticação
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            # Em uma implementação real, decodificaria o token JWT
            # e extrairia o ID do usuário
            # Por enquanto, retornar None
            return None
            
        except Exception:
            return None
    
    def _get_resource_from_path(self, path: str) -> str:
        """
        Determina o recurso com base no caminho da requisição
        """
        # Remover prefixo /api/ se existir
        if path.startswith("/api/"):
            path = path[5:]
        
        # Dividir o caminho em partes
        parts = path.strip("/").split("/")
        
        if not parts:
            return "unknown"
        
        # O primeiro segmento é geralmente o recurso
        resource = parts[0]
        
        # Verificar recursos específicos
        if resource == "atm":
            if len(parts) > 1:
                return f"atm_{parts[1]}"
            return "atm"
        
        if resource == "admin":
            if len(parts) > 1:
                return f"admin_{parts[1]}"
            return "admin"
        
        return resource
    
    def _extract_resource_id(self, path: str) -> Optional[str]:
        """
        Extrai ID do recurso do caminho da requisição
        """
        # Dividir o caminho em partes
        parts = path.strip("/").split("/")
        
        # Verificar se há ID no caminho
        # Geralmente, IDs estão em posições ímpares após o nome do recurso
        if len(parts) >= 3 and parts[2].isalnum():
            return parts[2]
        
        return None