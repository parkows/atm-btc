#!/usr/bin/env python3
"""
Sistema de Cache - LiquidGold ATM
Implementação de cache com Redis para melhorar performance
"""

import json
import time
import os
import redis
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta

from app.core.logger import atm_logger

# Configuração do Redis para cache
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Inicializar cliente Redis
try:
    redis_client = redis.from_url(REDIS_URL)
except Exception as e:
    atm_logger.log_error('cache_manager', 'redis_connection_error', {'error': str(e)})
    redis_client = None

class CacheManager:
    """
    Gerenciador de cache utilizando Redis
    Implementa padrões de cache para diferentes tipos de dados
    """
    
    def __init__(self):
        self.redis = redis_client
        self.logger = atm_logger
        
        # Configurações de TTL (Time To Live) em segundos
        self.ttl_config = {
            'quotes': 60,           # Cotações: 1 minuto
            'session_status': 300,   # Status de sessão: 5 minutos
            'system_health': 120,    # Saúde do sistema: 2 minutos
            'reports': 3600,         # Relatórios: 1 hora
            'config': 1800,          # Configurações: 30 minutos
            'default': 600           # Padrão: 10 minutos
        }
        
        # Estatísticas de cache
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém valor do cache
        """
        try:
            data = self.redis.get(key)
            if data:
                self.stats['hits'] += 1
                return json.loads(data)
            else:
                self.stats['misses'] += 1
                return default
        except Exception as e:
            self.logger.log_error('cache', 'get_error', {
                'key': key,
                'error': str(e)
            })
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, category: str = 'default') -> bool:
        """
        Define valor no cache com TTL específico ou baseado na categoria
        """
        try:
            # Determinar TTL
            if ttl is None:
                ttl = self.ttl_config.get(category, self.ttl_config['default'])
            
            # Serializar e armazenar
            self.redis.setex(key, ttl, json.dumps(value))
            self.stats['sets'] += 1
            return True
        except Exception as e:
            self.logger.log_error('cache', 'set_error', {
                'key': key,
                'error': str(e)
            })
            return False
    
    def delete(self, key: str) -> bool:
        """
        Remove valor do cache
        """
        try:
            self.redis.delete(key)
            self.stats['deletes'] += 1
            return True
        except Exception as e:
            self.logger.log_error('cache', 'delete_error', {
                'key': key,
                'error': str(e)
            })
            return False
    
    def flush_category(self, category: str) -> int:
        """
        Remove todos os valores de uma categoria (por prefixo)
        """
        try:
            pattern = f"{category}:*"
            keys = self.redis.keys(pattern)
            if keys:
                count = self.redis.delete(*keys)
                self.stats['deletes'] += count
                return count
            return 0
        except Exception as e:
            self.logger.log_error('cache', 'flush_category_error', {
                'category': category,
                'error': str(e)
            })
            return 0
    
    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas de uso do cache
        """
        return self.stats
    
    # Métodos específicos para diferentes tipos de dados
    
    def get_quote(self, crypto_type: str, transaction_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtém cotação em cache
        """
        key = f"quotes:{crypto_type}:{transaction_type}"
        return self.get(key)
    
    def set_quote(self, crypto_type: str, transaction_type: str, quote_data: Dict[str, Any]) -> bool:
        """
        Armazena cotação em cache
        """
        key = f"quotes:{crypto_type}:{transaction_type}"
        return self.set(key, quote_data, category='quotes')
    
    def get_session_status(self, session_code: str) -> Optional[Dict[str, Any]]:
        """
        Obtém status de sessão em cache
        """
        key = f"session_status:{session_code}"
        return self.get(key)
    
    def set_session_status(self, session_code: str, status_data: Dict[str, Any]) -> bool:
        """
        Armazena status de sessão em cache
        """
        key = f"session_status:{session_code}"
        return self.set(key, status_data, category='session_status')
    
    def invalidate_session_status(self, session_code: str) -> bool:
        """
        Invalida cache de status de sessão
        """
        key = f"session_status:{session_code}"
        return self.delete(key)

# Instância global
cache_manager = CacheManager()