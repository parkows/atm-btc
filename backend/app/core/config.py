import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

class ATMConfig:
    def __init__(self, config_file: str = "config/atm_config.json"):
        self.config_file = Path(config_file)
        self.config_dir = self.config_file.parent
        self.config_dir.mkdir(exist_ok=True)
        
        # Configurações padrão
        self.default_config = {
            "atm": {
                "id": "LiquidGold_ATM001",
                "location": "Buenos Aires, Argentina",
                "timezone": "America/Argentina/Buenos_Aires",
                "currency": "ARS",
                "language": "es"
            },
            "bitcoin": {
                "network": "mainnet",
                "min_amount": 10000,
                "max_amount": 250000,
                "service_fee_percent": 10.0,
                "exchange_rate_source": "binance"
            },
            "security": {
                "max_daily_transactions": 50,
                "max_daily_amount": 1000000,
                "session_timeout_minutes": 5,
                "require_kyc": False,
                "fraud_detection_enabled": True
            },
            "hardware": {
                "printer_enabled": True,
                "camera_enabled": True,
                "touchscreen_enabled": True,
                "maintenance_mode": False
            },
            "notifications": {
                "email_enabled": False,
                "sms_enabled": False,
                "webhook_enabled": False,
                "webhook_url": ""
            },
            "logging": {
                "level": "INFO",
                "retention_days": 30,
                "audit_enabled": True
            }
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo ou cria padrão"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Mesclar com configurações padrão
                    return self._merge_configs(self.default_config, config)
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
                return self.default_config
        else:
            # Criar arquivo de configuração padrão
            self.save_config(self.default_config)
            return self.default_config
    
    def _merge_configs(self, default: Dict, custom: Dict) -> Dict:
        """Mescla configurações customizadas com padrão"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Dict[str, Any]):
        """Salva configuração no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração usando notação de ponto (ex: 'atm.id')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Define valor de configuração usando notação de ponto"""
        keys = key.split('.')
        config = self.config
        
        # Navegar até o nível anterior ao último
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Definir o valor final
        config[keys[-1]] = value
        self.save_config(self.config)
    
    def get_all(self) -> Dict[str, Any]:
        """Retorna todas as configurações"""
        return self.config
    
    def get_atm_id(self) -> str:
        """Obtém ID do ATM"""
        return self.get('atm.id', 'LiquidGold_ATM001')
    
    def get_limits(self) -> Dict[str, float]:
        """Obtém limites de transação"""
        return {
            'min_amount': self.get('bitcoin.min_amount', 10000),
            'max_amount': self.get('bitcoin.max_amount', 250000),
            'service_fee_percent': self.get('bitcoin.service_fee_percent', 10.0)
        }
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Obtém configurações de segurança"""
        return {
            'max_daily_transactions': self.get('security.max_daily_transactions', 50),
            'max_daily_amount': self.get('security.max_daily_amount', 1000000),
            'session_timeout_minutes': self.get('security.session_timeout_minutes', 5),
            'fraud_detection_enabled': self.get('security.fraud_detection_enabled', True)
        }
    
    def is_maintenance_mode(self) -> bool:
        """Verifica se está em modo manutenção"""
        return self.get('hardware.maintenance_mode', False)
    
    def get_notification_settings(self) -> Dict[str, Any]:
        """Obtém configurações de notificação"""
        return {
            'email_enabled': self.get('notifications.email_enabled', False),
            'sms_enabled': self.get('notifications.sms_enabled', False),
            'webhook_enabled': self.get('notifications.webhook_enabled', False),
            'webhook_url': self.get('notifications.webhook_url', '')
        }

# Instância global
atm_config = ATMConfig() 