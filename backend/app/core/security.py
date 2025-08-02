import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from .config import atm_config
from .logger import atm_logger
from .notifications import notification_manager
from ..models import Session as SessionModel

class SecurityManager:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.logger = atm_logger
        self.notifications = notification_manager
        self.security_settings = atm_config.get_security_settings()
        
        # Cache de tentativas de fraude
        self.fraud_attempts = {}
        self.suspicious_ips = set()
    
    def validate_transaction_limits(self, amount: float, session_code: str) -> Tuple[bool, str]:
        """Valida limites de transação"""
        try:
            # Verificar limites configurados
            limits = atm_config.get_limits()
            min_amount = limits['min_amount']
            max_amount = limits['max_amount']
            
            if amount < min_amount:
                return False, f"Valor mínimo é ${min_amount:,.2f} ARS"
            
            if amount > max_amount:
                return False, f"Valor máximo é ${max_amount:,.2f} ARS"
            
            # Verificar limites diários
            daily_limits = self._check_daily_limits(amount)
            if not daily_limits['can_transact']:
                return False, daily_limits['reason']
            
            # Log da validação
            self.logger.log_audit('system', 'transaction_validation', 'limits', {
                'session_code': session_code,
                'amount': amount,
                'validation_passed': True
            })
            
            return True, "Limites válidos"
            
        except Exception as e:
            self.logger.log_security('validation_error', 'high', {
                'session_code': session_code,
                'amount': amount,
                'error': str(e)
            })
            return False, f"Erro na validação: {str(e)}"
    
    def _check_daily_limits(self, amount: float) -> Dict[str, Any]:
        """Verifica limites diários de transações"""
        try:
            db = self.db_session_factory()
            today = datetime.utcnow().date()
            
            # Transações de hoje
            today_transactions = db.query(SessionModel).filter(
                db.func.date(SessionModel.created_at) == today
            ).count()
            
            # Valor total de hoje
            today_amount = db.query(SessionModel).filter(
                db.func.date(SessionModel.created_at) == today,
                SessionModel.status == 'pago'
            ).with_entities(
                db.func.sum(SessionModel.amount_ars)
            ).scalar() or 0
            
            db.close()
            
            # Limites configurados
            max_transactions = self.security_settings['max_daily_transactions']
            max_amount = self.security_settings['max_daily_amount']
            
            # Verificar se pode transacionar
            if today_transactions >= max_transactions:
                return {
                    'can_transact': False,
                    'reason': f"Limite diário de transações atingido ({max_transactions})"
                }
            
            if today_amount + amount > max_amount:
                return {
                    'can_transact': False,
                    'reason': f"Limite diário de valor atingido (${max_amount:,.2f} ARS)"
                }
            
            return {
                'can_transact': True,
                'reason': "Limites diários válidos"
            }
            
        except Exception as e:
            self.logger.log_security('daily_limits_error', 'high', {'error': str(e)})
            return {
                'can_transact': False,
                'reason': f"Erro ao verificar limites: {str(e)}"
            }
    
    def detect_fraud_patterns(self, session_code: str, amount: float, ip_address: str = None) -> Dict[str, Any]:
        """Detecta padrões de fraude"""
        try:
            fraud_score = 0
            fraud_reasons = []
            
            # Verificar tentativas repetidas
            if session_code in self.fraud_attempts:
                attempts = self.fraud_attempts[session_code]
                if len(attempts) > 3:
                    fraud_score += 30
                    fraud_reasons.append("Muitas tentativas de transação")
            
            # Verificar valores suspeitos
            if amount % 1000 != 0:  # Valores devem ser múltiplos de 1000
                fraud_score += 20
                fraud_reasons.append("Valor não é múltiplo de 1000")
            
            # Verificar IP suspeito
            if ip_address and ip_address in self.suspicious_ips:
                fraud_score += 40
                fraud_reasons.append("IP suspeito")
            
            # Verificar padrões de tempo (transações muito rápidas)
            db = self.db_session_factory()
            recent_transactions = db.query(SessionModel).filter(
                SessionModel.created_at >= datetime.utcnow() - timedelta(minutes=5)
            ).count()
            
            if recent_transactions > 10:
                fraud_score += 25
                fraud_reasons.append("Muitas transações em pouco tempo")
            
            db.close()
            
            # Determinar nível de risco
            risk_level = "low"
            if fraud_score >= 70:
                risk_level = "high"
            elif fraud_score >= 40:
                risk_level = "medium"
            
            # Registrar tentativa
            if session_code not in self.fraud_attempts:
                self.fraud_attempts[session_code] = []
            
            self.fraud_attempts[session_code].append({
                'timestamp': datetime.utcnow(),
                'amount': amount,
                'fraud_score': fraud_score,
                'risk_level': risk_level
            })
            
            # Limpar tentativas antigas (mais de 1 hora)
            self._cleanup_old_attempts()
            
            # Alertas de segurança
            if risk_level == "high":
                self.notifications.notify_security_alert('fraud_detected', {
                    'session_code': session_code,
                    'amount': amount,
                    'fraud_score': fraud_score,
                    'reasons': fraud_reasons,
                    'ip_address': ip_address
                })
                
                self.logger.log_security('fraud_detected', 'high', {
                    'session_code': session_code,
                    'amount': amount,
                    'fraud_score': fraud_score,
                    'reasons': fraud_reasons,
                    'ip_address': ip_address
                })
            
            return {
                'fraud_score': fraud_score,
                'risk_level': risk_level,
                'reasons': fraud_reasons,
                'blocked': risk_level == "high"
            }
            
        except Exception as e:
            self.logger.log_security('fraud_detection_error', 'high', {'error': str(e)})
            return {
                'fraud_score': 0,
                'risk_level': 'unknown',
                'reasons': [f"Erro na detecção: {str(e)}"],
                'blocked': False
            }
    
    def _cleanup_old_attempts(self):
        """Remove tentativas antigas do cache"""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        for session_code in list(self.fraud_attempts.keys()):
            self.fraud_attempts[session_code] = [
                attempt for attempt in self.fraud_attempts[session_code]
                if attempt['timestamp'] > cutoff_time
            ]
            
            if not self.fraud_attempts[session_code]:
                del self.fraud_attempts[session_code]
    
    def validate_session_security(self, session_code: str) -> Tuple[bool, str]:
        """Valida segurança da sessão"""
        try:
            db = self.db_session_factory()
            session = db.query(SessionModel).filter_by(session_code=session_code).first()
            
            if not session:
                return False, "Sessão não encontrada"
            
            # Verificar se a sessão expirou
            if session.expires_at < datetime.utcnow():
                return False, "Sessão expirada"
            
            # Verificar se a sessão já foi usada
            if session.status.value in ['pago', 'concluida']:
                return False, "Sessão já foi utilizada"
            
            db.close()
            
            return True, "Sessão válida"
            
        except Exception as e:
            self.logger.log_security('session_validation_error', 'medium', {
                'session_code': session_code,
                'error': str(e)
            })
            return False, f"Erro na validação: {str(e)}"
    
    def generate_audit_trail(self, session_code: str) -> Dict[str, Any]:
        """Gera trilha de auditoria para uma sessão"""
        try:
            db = self.db_session_factory()
            session = db.query(SessionModel).filter_by(session_code=session_code).first()
            
            if not session:
                return {'error': 'Sessão não encontrada'}
            
            audit_trail = {
                'session_code': session_code,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'status': session.status.value if session.status else None,
                'amount_ars': session.amount_ars,
                'btc_expected': session.btc_expected,
                'invoice': session.invoice,
                'invoice_status': session.invoice_status.value if session.invoice_status else None,
                'security_events': []
            }
            
            # Adicionar eventos de segurança relacionados
            # (em um sistema real, isso viria de logs específicos)
            
            db.close()
            
            return audit_trail
            
        except Exception as e:
            self.logger.log_security('audit_trail_error', 'medium', {
                'session_code': session_code,
                'error': str(e)
            })
            return {'error': str(e)}
    
    def check_compliance_requirements(self, amount: float) -> Dict[str, Any]:
        """Verifica requisitos de compliance"""
        try:
            compliance_checks = {
                'kyc_required': False,
                'aml_check_required': False,
                'reporting_required': False,
                'reasons': []
            }
            
            # Verificar se KYC é necessário
            if self.security_settings['require_kyc']:
                compliance_checks['kyc_required'] = True
                compliance_checks['reasons'].append("KYC obrigatório configurado")
            
            # Verificar se AML é necessário (para valores altos)
            if amount > 50000:  # 50k ARS
                compliance_checks['aml_check_required'] = True
                compliance_checks['reasons'].append("Valor alto - AML check necessário")
            
            # Verificar se relatório é necessário
            if amount > 100000:  # 100k ARS
                compliance_checks['reporting_required'] = True
                compliance_checks['reasons'].append("Valor alto - Relatório obrigatório")
            
            return compliance_checks
            
        except Exception as e:
            self.logger.log_security('compliance_check_error', 'medium', {'error': str(e)})
            return {
                'kyc_required': False,
                'aml_check_required': False,
                'reporting_required': False,
                'error': str(e)
            }
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitiza entrada de dados"""
        if not input_data:
            return ""
        
        # Remover caracteres perigosos
        sanitized = re.sub(r'[<>"\']', '', input_data)
        
        # Limitar tamanho
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized.strip()
    
    def generate_session_token(self) -> str:
        """Gera token seguro para sessão"""
        return secrets.token_urlsafe(32)
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash de dados sensíveis"""
        return hashlib.sha256(data.encode()).hexdigest()

# Instância global do gerenciador de segurança (será inicializada no main.py)
security_manager = None 