#!/usr/bin/env python3
"""
Middleware de Rate Limiting - LiquidGold ATM
Implementação de middleware para aplicar rate limiting em todas as requisições
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time
from typing import Callable, Dict, Optional

from app.core.rate_limiter import rate_limiter
from app.core.logger import atm_logger

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware para aplicar rate limiting em todas as requisições
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Obter IP do cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Verificar whitelist
        if rate_limiter._is_whitelisted(client_ip):
            return await call_next(request)
        
        # Determinar o escopo com base no caminho da requisição
        path = request.url.path
        scope = self._get_scope_for_path(path)
        
        # Verificar rate limit
        is_allowed, retry_after = rate_limiter._check_rate(scope, client_ip)
        
        if not is_allowed:
            # Registrar tentativa bloqueada
            atm_logger.log_security('rate_limiter', 'rate_limit_exceeded', {
                'ip': client_ip,
                'path': path,
                'scope': scope,
                'retry_after': retry_after
            })
            
            # Retornar erro 429 (Too Many Requests)
            return Response(
                content=f"Muitas requisições. Tente novamente em {retry_after} segundos.",
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(retry_after)}
            )
        
        # Medir tempo de resposta
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Adicionar headers de rate limit na resposta
        response.headers["X-Rate-Limit-Scope"] = scope
        
        # Registrar requisição bem-sucedida para análise de performance
        if process_time > 1.0:  # Registrar apenas requisições lentas (> 1s)
            atm_logger.log_system('performance', 'slow_request', {
                'ip': client_ip,
                'path': path,
                'process_time': round(process_time, 3),
                'status_code': response.status_code
            })
        
        return response
    
    def _get_scope_for_path(self, path: str) -> str:
        """
        Determina o escopo de rate limiting com base no caminho da requisição
        """
        # Rotas de login
        if path.endswith("/login") or "/auth/" in path:
            return "login"
        
        # Rotas administrativas
        if path.startswith("/api/admin"):
            return "admin"
        
        # Rotas de API
        if path.startswith("/api/"):
            return "api"
        
        # Outras rotas
        return "ip"