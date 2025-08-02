#!/usr/bin/env python3
"""
Módulo de Gerenciamento de Criptomoedas - LiquidGold ATM
Suporte para Bitcoin (Lightning) e USDT (TRC20)
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from .config import atm_config
from .logger import atm_logger

class CryptoManager:
    """Gerenciador de múltiplas criptomoedas"""
    
    def __init__(self):
        self.config = atm_config
        self.logger = atm_logger
        
        # APIs de cotação
        self.bitso_url = "https://api.bitso.com/v3/ticker/?book=btc_ars"
        self.binance_url = "https://api.binance.com/api/v3/ticker/price"
        
        # Configurações de rede
        self.networks = {
            'BTC': {
                'name': 'Bitcoin',
                'network': 'Lightning',
                'decimals': 8,
                'min_amount': 10000,
                'max_amount': 250000,
                'service_fee': 10.0
            },
            'USDT': {
                'name': 'Tether USD',
                'network': 'TRC20',
                'decimals': 6,
                'min_amount': 10000,
                'max_amount': 250000,
                'service_fee': 5.0
            }
        }
    
    def get_btc_ars_quote(self) -> float:
        """Obtém cotação BTC/ARS do Bitso"""
        try:
            response = requests.get(self.bitso_url, timeout=5)
            data = response.json()
            price = float(data["payload"]["last"])
            return price
        except Exception as e:
            self.logger.log_system('crypto_manager', 'btc_quote_error', {'error': str(e)})
            raise Exception(f"Erro ao buscar cotação BTC/ARS: {e}")
    
    def get_usdt_ars_quote(self) -> float:
        """Obtém cotação USDT/ARS via Binance"""
        try:
            # Primeiro obtém USDT/USD
            response = requests.get(f"{self.binance_url}?symbol=USDTUSD", timeout=5)
            usdt_usd_data = response.json()
            usdt_usd_price = float(usdt_usd_data["price"])
            
            # Depois obtém USD/ARS (aproximação)
            # Em produção, usar API específica para USD/ARS
            usd_ars_rate = 1000.0  # Taxa aproximada USD/ARS
            
            usdt_ars_price = usdt_usd_price * usd_ars_rate
            return usdt_ars_price
            
        except Exception as e:
            # Fallback: usar cotação fixa para testes
            self.logger.log_system('crypto_manager', 'usdt_quote_error', {'error': str(e)})
            return 1000.0  # 1 USDT = 1000 ARS (aproximação para testes)
    
    def get_quote(self, crypto: str, amount_ars: float) -> Dict[str, Any]:
        """Obtém cotação para qualquer criptomoeda"""
        if crypto not in self.networks:
            raise Exception(f"Criptomoeda {crypto} não suportada")
        
        network_config = self.networks[crypto]
        
        # Validar limites
        if amount_ars < network_config['min_amount'] or amount_ars > network_config['max_amount']:
            raise Exception(f"Valor fora dos limites para {crypto} (${network_config['min_amount']:,.2f} a ${network_config['max_amount']:,.2f} ARS)")
        
        try:
            # Obter cotação
            if crypto == 'BTC':
                crypto_ars_price = self.get_btc_ars_quote()
            elif crypto == 'USDT':
                crypto_ars_price = self.get_usdt_ars_quote()
            else:
                raise Exception(f"Criptomoeda {crypto} não implementada")
            
            # Calcular valores
            service_fee_percent = network_config['service_fee']
            valor_liquido = amount_ars * (1 - service_fee_percent / 100)
            crypto_amount = round(valor_liquido / crypto_ars_price, network_config['decimals'])
            
            return {
                'crypto': crypto,
                'network': network_config['network'],
                'crypto_ars_price': crypto_ars_price,
                'amount_ars': amount_ars,
                'valor_liquido_ars': valor_liquido,
                'crypto_amount': crypto_amount,
                'service_fee_percent': service_fee_percent,
                'service_fee_ars': amount_ars * (service_fee_percent / 100)
            }
            
        except Exception as e:
            self.logger.log_system('crypto_manager', 'quote_error', {
                'crypto': crypto,
                'amount_ars': amount_ars,
                'error': str(e)
            })
            raise e
    
    def create_invoice(self, crypto: str, amount_ars: float, session_code: str) -> Dict[str, Any]:
        """Cria invoice para qualquer criptomoeda"""
        if crypto not in self.networks:
            raise Exception(f"Criptomoeda {crypto} não suportada")
        
        network_config = self.networks[crypto]
        
        # Obter cotação
        quote_data = self.get_quote(crypto, amount_ars)
        
        # Gerar invoice baseado na criptomoeda
        if crypto == 'BTC':
            invoice = self._create_lightning_invoice(quote_data, session_code)
        elif crypto == 'USDT':
            invoice = self._create_trc20_invoice(quote_data, session_code)
        else:
            raise Exception(f"Criptomoeda {crypto} não implementada")
        
        return {
            'session_code': session_code,
            'crypto': crypto,
            'network': network_config['network'],
            'amount_ars': amount_ars,
            'crypto_amount': quote_data['crypto_amount'],
            'invoice': invoice,
            'expires_at': datetime.utcnow().timestamp() + 3600,  # 1 hora
            'quote_data': quote_data
        }
    
    def _create_lightning_invoice(self, quote_data: Dict[str, Any], session_code: str) -> str:
        """Cria invoice Lightning para Bitcoin"""
        # Em produção, integrar com Strike API
        return f"liquidgold@strike.me?session={session_code}&amount={quote_data['crypto_amount']}"
    
    def _create_trc20_invoice(self, quote_data: Dict[str, Any], session_code: str) -> str:
        """Cria invoice TRC20 para USDT"""
        # Em produção, integrar com API de carteira TRC20
        return f"TRC20:liquidgold_wallet?session={session_code}&amount={quote_data['crypto_amount']}"
    
    def check_payment(self, crypto: str, invoice: str) -> Dict[str, Any]:
        """Verifica pagamento para qualquer criptomoeda"""
        if crypto not in self.networks:
            raise Exception(f"Criptomoeda {crypto} não suportada")
        
        try:
            if crypto == 'BTC':
                return self._check_lightning_payment(invoice)
            elif crypto == 'USDT':
                return self._check_trc20_payment(invoice)
            else:
                raise Exception(f"Criptomoeda {crypto} não implementada")
                
        except Exception as e:
            self.logger.log_system('crypto_manager', 'payment_check_error', {
                'crypto': crypto,
                'invoice': invoice,
                'error': str(e)
            })
            raise e
    
    def _check_lightning_payment(self, invoice: str) -> Dict[str, Any]:
        """Verifica pagamento Lightning"""
        # Em produção, verificar com Strike API
        # Mock: invoices terminados em '7' são pagos
        is_paid = invoice and invoice[-1] == '7'
        
        return {
            'status': 'paid' if is_paid else 'pending',
            'network': 'Lightning',
            'crypto': 'BTC',
            'paid_at': datetime.utcnow().isoformat() if is_paid else None
        }
    
    def _check_trc20_payment(self, invoice: str) -> Dict[str, Any]:
        """Verifica pagamento TRC20"""
        # Em produção, verificar com API da carteira TRC20
        # Mock: invoices terminados em '8' são pagos
        is_paid = invoice and invoice[-1] == '8'
        
        return {
            'status': 'paid' if is_paid else 'pending',
            'network': 'TRC20',
            'crypto': 'USDT',
            'paid_at': datetime.utcnow().isoformat() if is_paid else None
        }
    
    def get_supported_cryptos(self) -> Dict[str, Any]:
        """Retorna lista de criptomoedas suportadas"""
        return {
            crypto: {
                'name': config['name'],
                'network': config['network'],
                'min_amount': config['min_amount'],
                'max_amount': config['max_amount'],
                'service_fee': config['service_fee'],
                'decimals': config['decimals']
            }
            for crypto, config in self.networks.items()
        }
    
    def validate_amount(self, crypto: str, amount_ars: float) -> bool:
        """Valida se o valor está dentro dos limites"""
        if crypto not in self.networks:
            return False
        
        network_config = self.networks[crypto]
        return network_config['min_amount'] <= amount_ars <= network_config['max_amount']

# Instância global
crypto_manager = CryptoManager() 