#!/usr/bin/env python3
"""
Módulo de Integração Lightning Network - RedATM
Integração com Strike API para recebimento de Bitcoin
"""

import requests
import json
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

class LightningWallet:
    """Classe para gerenciar carteira Lightning Network"""
    
    def __init__(self, api_key: str, account_id: str, webhook_secret: str = None):
        self.api_key = api_key
        self.account_id = account_id
        self.webhook_secret = webhook_secret
        self.base_url = "https://api.strike.me/v1"
        self.logger = logging.getLogger(__name__)
        
        # Headers padrão
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_invoice(self, amount_sats: int, description: str, 
                      expiration_seconds: int = 3600) -> Dict:
        """
        Cria invoice Lightning Network
        
        Args:
            amount_sats: Quantidade em satoshis
            description: Descrição da transação
            expiration_seconds: Tempo de expiração em segundos
            
        Returns:
            Dict com dados do invoice
        """
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/invoices"
            
            data = {
                "amount": amount_sats,
                "description": description,
                "expiration": expiration_seconds,
                "webhook_url": "https://redatm.com/webhook/strike",
                "webhook_version": "v1"
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            invoice_data = response.json()
            
            self.logger.info(f"Invoice criado: {invoice_data.get('invoice_id')} - {amount_sats} sats")
            
            return {
                "invoice_id": invoice_data.get("invoice_id"),
                "payment_request": invoice_data.get("payment_request"),
                "amount_sats": amount_sats,
                "description": description,
                "expires_at": datetime.now() + timedelta(seconds=expiration_seconds),
                "status": "pending"
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao criar invoice: {e}")
            raise Exception(f"Falha ao criar invoice Lightning: {e}")
    
    def check_payment(self, invoice_id: str) -> Dict:
        """
        Verifica status do pagamento
        
        Args:
            invoice_id: ID do invoice
            
        Returns:
            Dict com status do pagamento
        """
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/invoices/{invoice_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            payment_data = response.json()
            
            return {
                "invoice_id": invoice_id,
                "status": payment_data.get("status"),
                "paid_at": payment_data.get("paid_at"),
                "amount_paid": payment_data.get("amount_paid"),
                "fee_paid": payment_data.get("fee_paid")
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao verificar pagamento: {e}")
            raise Exception(f"Falha ao verificar pagamento: {e}")
    
    def get_balance(self) -> Dict:
        """
        Obtém saldo da carteira
        
        Returns:
            Dict com saldo em diferentes moedas
        """
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/balance"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            balance_data = response.json()
            
            return {
                "btc_balance": balance_data.get("btc_balance", 0),
                "usd_balance": balance_data.get("usd_balance", 0),
                "last_updated": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao obter saldo: {e}")
            raise Exception(f"Falha ao obter saldo: {e}")
    
    def get_transaction_history(self, limit: int = 100) -> List[Dict]:
        """
        Obtém histórico de transações
        
        Args:
            limit: Número máximo de transações
            
        Returns:
            Lista de transações
        """
        try:
            url = f"{self.base_url}/accounts/{self.account_id}/transactions"
            params = {"limit": limit}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            transactions = response.json().get("transactions", [])
            
            return [
                {
                    "transaction_id": tx.get("transaction_id"),
                    "type": tx.get("type"),
                    "amount": tx.get("amount"),
                    "currency": tx.get("currency"),
                    "status": tx.get("status"),
                    "timestamp": tx.get("timestamp"),
                    "description": tx.get("description")
                }
                for tx in transactions
            ]
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            raise Exception(f"Falha ao obter histórico: {e}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verifica assinatura do webhook
        
        Args:
            payload: Corpo da requisição
            signature: Assinatura do webhook
            
        Returns:
            True se assinatura é válida
        """
        if not self.webhook_secret:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_webhook(self, payload: Dict, signature: str) -> Dict:
        """
        Processa webhook do Strike
        
        Args:
            payload: Dados do webhook
            signature: Assinatura do webhook
            
        Returns:
            Dict com dados processados
        """
        if not self.verify_webhook_signature(json.dumps(payload), signature):
            raise Exception("Assinatura do webhook inválida")
        
        webhook_type = payload.get("type")
        
        if webhook_type == "invoice.paid":
            return self._process_payment_webhook(payload)
        elif webhook_type == "invoice.expired":
            return self._process_expiration_webhook(payload)
        else:
            self.logger.warning(f"Webhook tipo desconhecido: {webhook_type}")
            return {"status": "unknown_webhook_type"}
    
    def _process_payment_webhook(self, payload: Dict) -> Dict:
        """Processa webhook de pagamento"""
        invoice_data = payload.get("data", {})
        
        return {
            "type": "payment_received",
            "invoice_id": invoice_data.get("invoice_id"),
            "amount_paid": invoice_data.get("amount_paid"),
            "paid_at": invoice_data.get("paid_at"),
            "status": "completed"
        }
    
    def _process_expiration_webhook(self, payload: Dict) -> Dict:
        """Processa webhook de expiração"""
        invoice_data = payload.get("data", {})
        
        return {
            "type": "invoice_expired",
            "invoice_id": invoice_data.get("invoice_id"),
            "status": "expired"
        }
    
    def get_network_status(self) -> Dict:
        """
        Obtém status da rede Lightning
        
        Returns:
            Dict com informações da rede
        """
        try:
            url = f"{self.base_url}/network/status"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            network_data = response.json()
            
            return {
                "network_status": network_data.get("status"),
                "node_count": network_data.get("node_count"),
                "channel_count": network_data.get("channel_count"),
                "capacity": network_data.get("capacity"),
                "last_updated": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao obter status da rede: {e}")
            return {
                "network_status": "unknown",
                "error": str(e)
            }
    
    def estimate_fee(self, amount_sats: int) -> Dict:
        """
        Estima taxa da transação
        
        Args:
            amount_sats: Quantidade em satoshis
            
        Returns:
            Dict com estimativa de taxa
        """
        try:
            url = f"{self.base_url}/network/fee-estimate"
            params = {"amount": amount_sats}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            fee_data = response.json()
            
            return {
                "estimated_fee_sats": fee_data.get("fee_sats"),
                "estimated_fee_usd": fee_data.get("fee_usd"),
                "confidence": fee_data.get("confidence")
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro ao estimar taxa: {e}")
            return {
                "estimated_fee_sats": 1,  # Taxa mínima
                "estimated_fee_usd": 0.01,
                "confidence": "low"
            }

class LightningWalletManager:
    """Gerenciador de múltiplas carteiras Lightning"""
    
    def __init__(self):
        self.wallets = {}
        self.logger = logging.getLogger(__name__)
    
    def add_wallet(self, name: str, api_key: str, account_id: str, 
                   webhook_secret: str = None) -> None:
        """Adiciona carteira ao gerenciador"""
        self.wallets[name] = LightningWallet(api_key, account_id, webhook_secret)
        self.logger.info(f"Carteira {name} adicionada")
    
    def get_wallet(self, name: str) -> LightningWallet:
        """Obtém carteira por nome"""
        if name not in self.wallets:
            raise Exception(f"Carteira {name} não encontrada")
        return self.wallets[name]
    
    def get_all_balances(self) -> Dict:
        """Obtém saldo de todas as carteiras"""
        balances = {}
        
        for name, wallet in self.wallets.items():
            try:
                balance = wallet.get_balance()
                balances[name] = balance
            except Exception as e:
                self.logger.error(f"Erro ao obter saldo da carteira {name}: {e}")
                balances[name] = {"error": str(e)}
        
        return balances
    
    def get_total_balance(self) -> Dict:
        """Obtém saldo total de todas as carteiras"""
        all_balances = self.get_all_balances()
        
        total_btc = 0
        total_usd = 0
        
        for balance in all_balances.values():
            if "error" not in balance:
                total_btc += balance.get("btc_balance", 0)
                total_usd += balance.get("usd_balance", 0)
        
        return {
            "total_btc_balance": total_btc,
            "total_usd_balance": total_usd,
            "wallet_count": len(self.wallets),
            "last_updated": datetime.now().isoformat()
        }

# Instância global do gerenciador
lightning_manager = LightningWalletManager() 