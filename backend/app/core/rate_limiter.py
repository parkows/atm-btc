#!/usr/bin/env python3
"""
Sistema de Rate Limiting - LiquidGold ATM
Implementação de limitação de taxa para proteção contra ataques de força bruta e DoS
"""

from fastapi import Request, HTTPException, status
from typing import Dict, List, Tuple, Optional, Callable, Any
from datetime import datetime, timedelta
import time
import threading
import ipaddress
from collections import defaultdict, deque

from app.core.logger import atm_logger
from app.core.config import atm_config
from app.core.cache_manager import cache_manager

class RateLimiter:
    """
    Gerenciador de limitação de taxa para proteção contra ataques
    """
    
    def __init__(self):
        self.logger = atm_logger
        self.config = atm_config
        self.cache = cache_manager
        
        # Configurações padrão
        self.default_limits = {
            "global": {"rate": 1000, "per": 60},  # 1000 requisições por minuto globalmente
            "ip": {"rate": 100, "per": 60},      # 100 requisições por minuto por IP
            "login": {"rate": 5, "per": 60},     # 5 tentativas de login por minuto
            "api": {"rate": 200, "per": 60},     # 200 requisições de API por minuto
            "admin": {"rate": 50, "per": 60}     # 50 requisições admin por minuto
        }
        
        # Carregar configurações do arquivo de configuração
        self._load_config()
        
        # Cache em memória para IPs com alta taxa de requisições
        self.ip_cache = {}
        
        # Lista de IPs na whitelist (não sujeitos a rate limiting)
        self.whitelist = [
            "127.0.0.1",           # Localhost
            "::1",                 # Localhost IPv6
            "192.168.0.0/16"       # Rede local
        ]
        
        # Iniciar limpeza periódica do cache
        self._start_cleanup_thread()
    
    def _load_config(self):
        """
        Carrega configurações de rate limiting do arquivo de configuração
        """
        try:
            rate_limits = self.config.get("security.rate_limits")
            if rate_limits:
                for key, value in rate_limits.items():
                    if key in self.default_limits and isinstance(value, dict):
                        if "rate" in value and "per" in value:
                            self.default_limits[key] = value
            
            # Carregar whitelist
            whitelist = self.config.get("security.rate_limit_whitelist")
            if whitelist and isinstance(whitelist, list):
                self.whitelist = whitelist
                
        except Exception as e:
            self.logger.log_error('rate_limiter', 'config_load_error', {'error': str(e)})
    
    def _start_cleanup_thread(self):
        """
        Inicia thread para limpeza periódica do cache
        """
        def cleanup_task():
            while True:
                try:
                    now = time.time()
                    # Limpar entradas expiradas do cache em memória
                    keys_to_remove = []
                    for key, (timestamps, last_access) in self.ip_cache.items():
                        # Remover timestamps antigos
                        while timestamps and timestamps[0] < now - 3600:  # 1 hora
                            timestamps.popleft()
                        
                        # Remover entradas não acessadas por mais de 1 hora
                        if last_access < now - 3600:
                            keys_to_remove.append(key)
                    
                    for key in keys_to_remove:
                        del self.ip_cache[key]
                    
                    # Log da limpeza
                    if keys_to_remove:
                        self.logger.log_system('rate_limiter', 'cache_cleanup', {
                            'removed_entries': len(keys_to_remove),
                            'remaining_entries': len(self.ip_cache)
                        })
                        
                except Exception as e:
                    self.logger.log_error('rate_limiter', 'cleanup_error', {'error': str(e)})
                
                # Executar a cada 5 minutos
                time.sleep(300)
        
        # Iniciar thread
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
    
    def _is_whitelisted(self, ip: str) -> bool:
        """
        Verifica se um IP está na whitelist
        """
        try:
            client_ip = ipaddress.ip_address(ip)
            
            for item in self.whitelist:
                # Verificar se é um CIDR (rede)
                if '/' in item:
                    network = ipaddress.ip_network(item, strict=False)
                    if client_ip in network:
                        return True
                # Verificar IP individual
                else:
                    whitelist_ip = ipaddress.ip_address(item)
                    if client_ip == whitelist_ip:
                        return True
            
            return False
        except Exception:
            return False
    
    def _get_cache_key(self, scope: str, identifier: str) -> str:
        """
        Gera chave para o cache
        """
        return f"rate_limit:{scope}:{identifier}"
    
    def _check_rate(self, scope: str, identifier: str) -> Tuple[bool, int]:
        """
        Verifica se o limite de taxa foi excedido
        Retorna (is_allowed, retry_after)
        """
        # Obter limites para o escopo
        if scope not in self.default_limits:
            scope = "global"  # Fallback para limites globais
        
        limit = self.default_limits[scope]
        max_requests = limit["rate"]
        window = limit["per"]
        
        now = time.time()
        cache_key = self._get_cache_key(scope, identifier)
        
        # Verificar no Redis primeiro
        try:
            # Tentar obter do Redis
            rate_data = self.cache.get(cache_key, category="rate_limits")
            if rate_data:
                timestamps = rate_data.get("timestamps", [])
                # Filtrar timestamps dentro da janela de tempo
                valid_timestamps = [ts for ts in timestamps if ts > now - window]
                
                # Verificar se excedeu o limite
                if len(valid_timestamps) >= max_requests:
                    oldest = min(valid_timestamps) if valid_timestamps else now
                    retry_after = int(oldest + window - now) + 1
                    return False, retry_after
                
                # Atualizar timestamps
                valid_timestamps.append(now)
                self.cache.set(cache_key, {"timestamps": valid_timestamps}, 
                               ttl=window*2, category="rate_limits")
                return True, 0
            else:
                # Criar novo registro
                self.cache.set(cache_key, {"timestamps": [now]}, 
                               ttl=window*2, category="rate_limits")
                return True, 0
        except Exception as e:
            # Fallback para cache em memória em caso de erro no Redis
            self.logger.log_error('rate_limiter', 'redis_error', {'error': str(e)})
            
            # Usar cache em memória
            if identifier not in self.ip_cache:
                self.ip_cache[identifier] = (deque([now]), now)
                return True, 0
            
            timestamps, _ = self.ip_cache[identifier]
            
            # Filtrar timestamps dentro da janela de tempo
            while timestamps and timestamps[0] < now - window:
                timestamps.popleft()
            
            # Verificar se excedeu o limite
            if len(timestamps) >= max_requests:
                oldest = timestamps[0] if timestamps else now
                retry_after = int(oldest + window - now) + 1
                return False, retry_after
            
            # Atualizar timestamps
            timestamps.append(now)
            self.ip_cache[identifier] = (timestamps, now)
            return True, 0
    
    def limit(self, scope: str = "global"):
        """
        Decorator para aplicar rate limiting em endpoints
        """
        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                # Obter request do FastAPI
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if not request:
                    for _, value in kwargs.items():
                        if isinstance(value, Request):
                            request = value
                            break
                
                if not request:
                    # Se não encontrar o request, permitir a requisição
                    return await func(*args, **kwargs)
                
                # Obter IP do cliente
                client_ip = request.client.host if request.client else "unknown"
                
                # Verificar whitelist
                if self._is_whitelisted(client_ip):
                    return await func(*args, **kwargs)
                
                # Verificar rate limit
                is_allowed, retry_after = self._check_rate(scope, client_ip)
                
                if not is_allowed:
                    # Registrar tentativa bloqueada
                    self.logger.log_security('rate_limiter', 'rate_limit_exceeded', {
                        'ip': client_ip,
                        'scope': scope,
                        'retry_after': retry_after
                    })
                    
                    # Retornar erro 429 (Too Many Requests)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Muitas requisições. Tente novamente mais tarde.",
                        headers={"Retry-After": str(retry_after)}
                    )
                
                # Permitir a requisição
                return await func(*args, **kwargs)
            
            return wrapper
        
        return decorator

# Instância global
rate_limiter = RateLimiter()