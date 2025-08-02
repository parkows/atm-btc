import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from .config import atm_config

class I18nManager:
    def __init__(self):
        self.translations = {}
        self.current_language = atm_config.get('atm.language', 'es')
        self.fallback_language = 'en'
        self.load_translations()
    
    def load_translations(self):
        """Carrega traduções dos arquivos JSON"""
        translations_dir = Path("translations")
        translations_dir.mkdir(exist_ok=True)
        
        # Criar arquivos de tradução padrão se não existirem
        self._create_default_translations(translations_dir)
        
        # Carregar traduções
        for lang_file in translations_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar traduções para {lang_code}: {e}")
    
    def _create_default_translations(self, translations_dir: Path):
        """Cria arquivos de tradução padrão"""
        
        # Espanhol (Argentina)
        es_translations = {
            "atm": {
                "title": "LiquidGold",
                "subtitle": "Mucho más que un cajero.",
                "welcome": "Bienvenido",
                "select_option": "Seleccioná una opción",
                "cancel": "Cancelar",
                "confirm": "Confirmar",
                "back": "Volver",
                "continue": "Continuar",
                "accept": "Aceptar",
                "modify": "Modificar"
            },
            "bitcoin": {
                "title": "VENDER BITCOIN",
                "subtitle": "Red Lightning",
                "enter_amount": "Ingresá el valor en pesos que querés recibir",
                "amount_placeholder": "0",
                "amount_helper": "(múltiplos de 1.000) - Máximo: $250.000",
                "exchange_rate": "Cotización Bitcoin",
                "conversion": "Conversión en tiempo real",
                "service_fee": "Tasa de servicio: 10%",
                "exchange_rate_info": "Tasa de cambio: 1 USD = 1000 ARS",
                "confirm_amount": "Valor en pesos que vas a recibir",
                "transaction_cost": "Esta transacción tiene un costo de {cost} (10%)",
                "total_debit": "Valor total que se va a debitar de tu billetera: {btc} BTC",
                "bitcoin_to_sell": "Bitcoin que vas a vender: {btc} BTC",
                "qr_instruction": "Si estás de acuerdo, escaneá el QR Code Lightning y confirmá la venta desde la app de tu billetera Bitcoin",
                "waiting_confirmation": "Esperando confirmación...",
                "transaction_completed": "Tu venta de Bitcoin fue completada",
                "print_receipt": "¿Querés imprimir tu comprobante?",
                "environmental_message": "Usando menos papel, colaborás con la preservación del medio ambiente"
            },
            "cards": {
                "card_operations": "OPERACIONES CON TARJETA",
                "qr_withdrawal": "RETIRÁ CON QR",
                "recharge": "RECARGÁ",
                "pix_withdrawal": "SAQUE COM PIX (Brasil)",
                "deposits": "DEPÓSITOS",
                "sell_bitcoin": "VENDER BITCOIN"
            },
            "errors": {
                "invalid_amount": "Valor inválido",
                "amount_too_low": "Valor mínimo es ${min} ARS",
                "amount_too_high": "Valor máximo es ${max} ARS",
                "session_expired": "Sesión expirada",
                "transaction_failed": "Error en la transacción",
                "network_error": "Error de conexión",
                "system_error": "Error del sistema"
            },
            "status": {
                "waiting_payment": "Aguardando pago",
                "paid": "Pago",
                "expired": "Expirado",
                "completed": "Completado",
                "failed": "Fallido"
            }
        }
        
        # Inglês
        en_translations = {
            "atm": {
                "title": "LiquidGold",
                "subtitle": "Much more than an ATM.",
                "welcome": "Welcome",
                "select_option": "Select an option",
                "cancel": "Cancel",
                "confirm": "Confirm",
                "back": "Back",
                "continue": "Continue",
                "accept": "Accept",
                "modify": "Modify"
            },
            "bitcoin": {
                "title": "SELL BITCOIN",
                "subtitle": "Red Lightning",
                "enter_amount": "Enter the amount in pesos you want to receive",
                "amount_placeholder": "0",
                "amount_helper": "(multiples of 1,000) - Maximum: $250,000",
                "exchange_rate": "Bitcoin Exchange Rate",
                "conversion": "Real-time conversion",
                "service_fee": "Service fee: 10%",
                "exchange_rate_info": "Exchange rate: 1 USD = 1000 ARS",
                "confirm_amount": "Amount in pesos you will receive",
                "transaction_cost": "This transaction has a cost of {cost} (10%)",
                "total_debit": "Total amount to be debited from your wallet: {btc} BTC",
                "bitcoin_to_sell": "Bitcoin you will sell: {btc} BTC",
                "qr_instruction": "If you agree, scan the Lightning QR Code and confirm the sale from your Bitcoin wallet app",
                "waiting_confirmation": "Waiting for confirmation...",
                "transaction_completed": "Your Bitcoin sale was completed",
                "print_receipt": "Do you want to print your receipt?",
                "environmental_message": "Using less paper helps preserve the environment"
            },
            "cards": {
                "card_operations": "CARD OPERATIONS",
                "qr_withdrawal": "WITHDRAW WITH QR",
                "recharge": "RECHARGE",
                "pix_withdrawal": "PIX WITHDRAWAL (Brazil)",
                "deposits": "DEPOSITS",
                "sell_bitcoin": "SELL BITCOIN"
            },
            "errors": {
                "invalid_amount": "Invalid amount",
                "amount_too_low": "Minimum amount is ${min} ARS",
                "amount_too_high": "Maximum amount is ${max} ARS",
                "session_expired": "Session expired",
                "transaction_failed": "Transaction failed",
                "network_error": "Connection error",
                "system_error": "System error"
            },
            "status": {
                "waiting_payment": "Waiting for payment",
                "paid": "Paid",
                "expired": "Expired",
                "completed": "Completed",
                "failed": "Failed"
            }
        }
        
        # Português
        pt_translations = {
            "atm": {
                "title": "LiquidGold",
                "subtitle": "Muito mais que um caixa eletrônico.",
                "welcome": "Bem-vindo",
                "select_option": "Selecione uma opção",
                "cancel": "Cancelar",
                "confirm": "Confirmar",
                "back": "Voltar",
                "continue": "Continuar",
                "accept": "Aceitar",
                "modify": "Modificar"
            },
            "bitcoin": {
                "title": "VENDER BITCOIN",
                "subtitle": "Red Lightning",
                "enter_amount": "Digite o valor em pesos que você quer receber",
                "amount_placeholder": "0",
                "amount_helper": "(múltiplos de 1.000) - Máximo: $250.000",
                "exchange_rate": "Cotação do Bitcoin",
                "conversion": "Conversão em tempo real",
                "service_fee": "Taxa de serviço: 10%",
                "exchange_rate_info": "Taxa de câmbio: 1 USD = 1000 ARS",
                "confirm_amount": "Valor em pesos que você vai receber",
                "transaction_cost": "Esta transação tem um custo de {cost} (10%)",
                "total_debit": "Valor total que será debitado da sua carteira: {btc} BTC",
                "bitcoin_to_sell": "Bitcoin que você vai vender: {btc} BTC",
                "qr_instruction": "Se você concordar, escaneie o QR Code Lightning e confirme a venda no app da sua carteira Bitcoin",
                "waiting_confirmation": "Aguardando confirmação...",
                "transaction_completed": "Sua venda de Bitcoin foi completada",
                "print_receipt": "Você quer imprimir seu comprovante?",
                "environmental_message": "Usando menos papel, você colabora com a preservação do meio ambiente"
            },
            "cards": {
                "card_operations": "OPERACÕES COM CARTÃO",
                "qr_withdrawal": "SAQUE COM QR",
                "recharge": "RECARREGAR",
                "pix_withdrawal": "SAQUE COM PIX (Brasil)",
                "deposits": "DEPÓSITOS",
                "sell_bitcoin": "VENDER BITCOIN"
            },
            "errors": {
                "invalid_amount": "Valor inválido",
                "amount_too_low": "Valor mínimo é ${min} ARS",
                "amount_too_high": "Valor máximo é ${max} ARS",
                "session_expired": "Sessão expirada",
                "transaction_failed": "Erro na transação",
                "network_error": "Erro de conexão",
                "system_error": "Erro do sistema"
            },
            "status": {
                "waiting_payment": "Aguardando pagamento",
                "paid": "Pago",
                "expired": "Expirado",
                "completed": "Completado",
                "failed": "Falhado"
            }
        }
        
        # Salvar arquivos de tradução
        translations = {
            'es': es_translations,
            'en': en_translations,
            'pt': pt_translations
        }
        
        for lang_code, translation_data in translations.items():
            lang_file = translations_dir / f"{lang_code}.json"
            if not lang_file.exists():
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(translation_data, f, indent=2, ensure_ascii=False)
    
    def set_language(self, language: str):
        """Define o idioma atual"""
        if language in self.translations:
            self.current_language = language
        else:
            self.current_language = self.fallback_language
    
    def get_text(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Obtém texto traduzido"""
        if language is None:
            language = self.current_language
        
        # Tentar idioma solicitado
        if language in self.translations:
            text = self._get_nested_value(self.translations[language], key)
            if text:
                return text.format(**kwargs) if kwargs else text
        
        # Fallback para idioma padrão
        if self.fallback_language in self.translations:
            text = self._get_nested_value(self.translations[self.fallback_language], key)
            if text:
                return text.format(**kwargs) if kwargs else text
        
        # Se não encontrar, retornar a chave
        return key
    
    def _get_nested_value(self, data: Dict, key: str) -> Optional[str]:
        """Obtém valor aninhado usando notação de ponto"""
        keys = key.split('.')
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value if isinstance(value, str) else None
    
    def get_all_texts(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Obtém todas as traduções para um idioma"""
        if language is None:
            language = self.current_language
        
        return self.translations.get(language, {})
    
    def get_available_languages(self) -> List[str]:
        """Retorna lista de idiomas disponíveis"""
        return list(self.translations.keys())
    
    def format_currency(self, amount: float, currency: str = "ARS") -> str:
        """Formata valor monetário de acordo com o idioma"""
        if self.current_language == "es":
            return f"${amount:,.2f} {currency}"
        elif self.current_language == "pt":
            return f"R$ {amount:,.2f} {currency}"
        else:
            return f"${amount:,.2f} {currency}"
    
    def format_number(self, number: float) -> str:
        """Formata número de acordo com o idioma"""
        if self.current_language == "es":
            return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif self.current_language == "pt":
            return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            return f"{number:,.2f}"

# Instância global do gerenciador de internacionalização
i18n_manager = I18nManager() 