#!/usr/bin/env python3
"""
Módulo de Gerenciamento de Criptomoedas - LiquidGold ATM
Suporte para Bitcoin (Lightning) e USDT (TRC20)
Venda e Compra de criptomoedas
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
                'service_fee': 8.0,   # Venda: taxa competitiva
                'purchase_fee': 6.0   # Compra: taxa menor (incentivo)
            },
            'USDT': {
                'name': 'Tether USD',
                'network': 'TRC20',
                'decimals': 6,
                'min_amount': 10000,
                'max_amount': 250000,
                'service_fee': 6.0,   # Venda: taxa competitiva
                'purchase_fee': 4.0   # Compra: taxa menor (incentivo)
            }
        }
    
    def get_btc_usd_quote(self) -> float:
        """Obtém cotação BTC/USD do Binance"""
        try:
            response = requests.get(f"{self.binance_url}?symbol=BTCUSDT", timeout=5)
            data = response.json()
            price = float(data["price"])
            return price
        except Exception as e:
            self.logger.log_system('crypto_manager', 'btc_usd_quote_error', {'error': str(e)})
            raise Exception(f"Erro ao buscar cotação BTC/USD: {e}")
    
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
        """Obtém cotação USDT/ARS via múltiplas APIs"""
        try:
            # Tentar múltiplas APIs em ordem de prioridade
            
            # 1. Ripio API (corretora argentina)
            try:
                ripio_response = requests.get("https://api.ripio.com/public/v1/market/", timeout=5)
                ripio_data = ripio_response.json()
                for pair in ripio_data.get('data', []):
                    if pair.get('pair') == 'USDT_ARS':
                        return float(pair.get('last_price', 0))
            except:
                pass
            
            # 2. Buenbit API (corretora argentina)
            try:
                buenbit_response = requests.get("https://api.buenbit.com/api/v1/market/ticker", timeout=5)
                buenbit_data = buenbit_response.json()
                for ticker in buenbit_data.get('data', []):
                    if ticker.get('symbol') == 'USDT_ARS':
                        return float(ticker.get('last_price', 0))
            except:
                pass
            
            # 3. Lemon API (corretora argentina)
            try:
                lemon_response = requests.get("https://api.lemon.com/v1/market/ticker", timeout=5)
                lemon_data = lemon_response.json()
                if 'USDT_ARS' in lemon_data:
                    return float(lemon_data['USDT_ARS'].get('last', 0))
            except:
                pass
            
            # 4. Binance + USD/ARS (fallback)
            try:
                # USDT/USD
                binance_response = requests.get(f"{self.binance_url}?symbol=USDTUSD", timeout=5)
                usdt_usd_data = binance_response.json()
                usdt_usd_price = float(usdt_usd_data["price"])
                
                # USD/ARS (via API de câmbio)
                usd_ars_response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
                usd_ars_data = usd_ars_response.json()
                usd_ars_rate = float(usd_ars_data['rates']['ARS'])
                
                usdt_ars_price = usdt_usd_price * usd_ars_rate
                return usdt_ars_price
            except:
                pass
            
            # 5. CoinGecko API (fallback)
            try:
                coingecko_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=ars", timeout=5)
                coingecko_data = coingecko_response.json()
                return float(coingecko_data['tether']['ars'])
            except:
                pass
            
            # 6. Fallback final
            self.logger.log_system('crypto_manager', 'usdt_quote_fallback', {
                'message': 'Usando cotação de fallback para USDT/ARS'
            })
            return 1000.0  # 1 USDT = 1000 ARS (fallback)
            
        except Exception as e:
            self.logger.log_system('crypto_manager', 'usdt_quote_error', {'error': str(e)})
            return 1000.0  # Fallback final
    
    def get_quote(self, crypto: str, amount_ars: float, transaction_type: str = "VENDA") -> Dict[str, Any]:
        """Obtém cotação para qualquer criptomoeda (venda ou compra)"""
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
            
            # Calcular valores baseado no tipo de transação
            if transaction_type == "VENDA":
                # Cliente vende cripto por ARS
                service_fee_percent = network_config['service_fee']
                valor_liquido = amount_ars * (1 - service_fee_percent / 100)
                crypto_amount = round(valor_liquido / crypto_ars_price, network_config['decimals'])
            elif transaction_type == "COMPRA":
                # Cliente compra cripto com ARS
                service_fee_percent = network_config['purchase_fee']
                valor_total = amount_ars * (1 + service_fee_percent / 100)
                crypto_amount = round(amount_ars / crypto_ars_price, network_config['decimals'])
            else:
                raise Exception(f"Tipo de transação {transaction_type} não suportado")
            
            service_fee_ars = amount_ars * (service_fee_percent / 100)
            
            return {
                'crypto': crypto,
                'network': network_config['network'],
                'crypto_ars_price': crypto_ars_price,
                'amount_ars': amount_ars,
                'valor_liquido_ars': valor_liquido if transaction_type == "VENDA" else amount_ars,
                'crypto_amount': crypto_amount,
                'service_fee_percent': service_fee_percent,
                'service_fee_ars': service_fee_ars,
                'transaction_type': transaction_type
            }
            
        except Exception as e:
            self.logger.log_error('crypto_manager', 'quote_error', {
                'crypto': crypto,
                'amount_ars': amount_ars,
                'transaction_type': transaction_type,
                'error': str(e)
            })
            raise
    
    def create_invoice(self, crypto: str, amount_ars: float, session_code: str, transaction_type: str = "VENDA") -> Dict[str, Any]:
        """Cria invoice para venda ou compra"""
        quote_data = self.get_quote(crypto, amount_ars, transaction_type)
        
        if transaction_type == "VENDA":
            # Cliente vende cripto - gera invoice para receber cripto
            if crypto == 'BTC':
                invoice = self._create_lightning_invoice(quote_data, session_code)
            elif crypto == 'USDT':
                invoice = self._create_trc20_invoice(quote_data, session_code)
            else:
                raise Exception(f"Criptomoeda {crypto} não suportada para venda")
        else:
            raise Exception("Invoice não aplicável para compras")
        
        return {
            'session_code': session_code,
            'invoice': invoice,
            'quote_data': quote_data
        }
    
    def create_purchase_address(self, crypto: str, amount_ars: float, purchase_code: str) -> Dict[str, Any]:
        """Cria endereço para receber criptomoeda na compra"""
        quote_data = self.get_quote(crypto, amount_ars, "COMPRA")
        
        if crypto == 'BTC':
            address = self._create_lightning_address(quote_data, purchase_code)
        elif crypto == 'USDT':
            address = self._create_trc20_address(quote_data, purchase_code)
        else:
            raise Exception(f"Criptomoeda {crypto} não suportada para compra")
        
        return {
            'purchase_code': purchase_code,
            'crypto_address': address,
            'quote_data': quote_data
        }
    
    def _create_lightning_invoice(self, quote_data: Dict[str, Any], session_code: str) -> str:
        """Cria invoice Lightning Network para venda"""
        # Em produção, integrar com Lightning Network real
        return f"liquidgold@strike.me?amount={quote_data['crypto_amount']}&session={session_code}"
    
    def _create_trc20_invoice(self, quote_data: Dict[str, Any], session_code: str) -> str:
        """Cria invoice TRC20 para venda"""
        # Em produção, integrar com carteira TRC20 real
        return f"TRC20:liquidgold_wallet?amount={quote_data['crypto_amount']}&session={session_code}"
    
    def _create_lightning_address(self, quote_data: Dict[str, Any], purchase_code: str) -> str:
        """Cria endereço Lightning para receber cripto na compra"""
        # Em produção, gerar endereço Lightning real
        return f"liquidgold_buy@strike.me?purchase={purchase_code}"
    
    def _create_trc20_address(self, quote_data: Dict[str, Any], purchase_code: str) -> str:
        """Cria endereço TRC20 para receber cripto na compra"""
        # Em produção, gerar endereço TRC20 real
        return f"TRC20:liquidgold_buy_wallet?purchase={purchase_code}"
    
    def check_payment(self, crypto: str, invoice: str) -> Dict[str, Any]:
        """Verifica pagamento (apenas para vendas)"""
        if crypto == 'BTC':
            return self._check_lightning_payment(invoice)
        elif crypto == 'USDT':
            return self._check_trc20_payment(invoice)
        else:
            raise Exception(f"Criptomoeda {crypto} não suportada")
    
    def check_crypto_received(self, crypto: str, address: str) -> Dict[str, Any]:
        """Verifica se criptomoeda foi recebida (para compras)"""
        if crypto == 'BTC':
            return self._check_lightning_received(address)
        elif crypto == 'USDT':
            return self._check_trc20_received(address)
        else:
            raise Exception(f"Criptomoeda {crypto} não suportada")
    
    def _check_lightning_payment(self, invoice: str) -> Dict[str, Any]:
        """Verifica pagamento Lightning (mock)"""
        # Em produção, verificar na rede Lightning
        if invoice.endswith('7'):
            return {'status': 'pago', 'confirmed': True}
        else:
            return {'status': 'aguardando', 'confirmed': False}
    
    def _check_trc20_payment(self, invoice: str) -> Dict[str, Any]:
        """Verifica pagamento TRC20 (mock)"""
        # Em produção, verificar na rede TRC20
        if invoice.endswith('8'):
            return {'status': 'pago', 'confirmed': True}
        else:
            return {'status': 'aguardando', 'confirmed': False}
    
    def _check_lightning_received(self, address: str) -> Dict[str, Any]:
        """Verifica se cripto foi recebida via Lightning (mock)"""
        # Em produção, verificar na rede Lightning
        if address.endswith('9'):
            return {'status': 'recebido', 'confirmed': True}
        else:
            return {'status': 'aguardando', 'confirmed': False}
    
    def _check_trc20_received(self, address: str) -> Dict[str, Any]:
        """Verifica se cripto foi recebida via TRC20 (mock)"""
        # Em produção, verificar na rede TRC20
        if address.endswith('0'):
            return {'status': 'recebido', 'confirmed': True}
        else:
            return {'status': 'aguardando', 'confirmed': False}
    
    def get_supported_cryptos(self) -> Dict[str, Any]:
        """Retorna criptomoedas suportadas"""
        return {
            'cryptos': {
                crypto: {
                    'name': config['name'],
                    'network': config['network'],
                    'min_amount': config['min_amount'],
                    'max_amount': config['max_amount'],
                    'service_fee': config['service_fee'],
                    'purchase_fee': config['purchase_fee'],
                    'decimals': config['decimals']
                }
                for crypto, config in self.networks.items()
            }
        }
    
    def validate_amount(self, crypto: str, amount_ars: float) -> bool:
        """Valida valor para criptomoeda"""
        if crypto not in self.networks:
            return False
        
        config = self.networks[crypto]
        return config['min_amount'] <= amount_ars <= config['max_amount']

# Instância global
crypto_manager = CryptoManager() 