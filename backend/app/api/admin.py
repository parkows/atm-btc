from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.deps import get_db
from app.core.logger import atm_logger
from app.core.config import atm_config
from app.core.notifications import notification_manager
from app.core.monitoring import health_monitor
from app.core.reports import report_generator
from app.core.security import security_manager
from app.core.i18n import i18n_manager
from app.schemas import StandardResponse

router = APIRouter()

@router.get("/health")
async def get_system_health():
    """Endpoint para verificação de saúde do sistema"""
    try:
        health_data = health_monitor.check_system_health()
        atm_logger.log_audit('admin', 'health_check', 'system', {
            'timestamp': datetime.utcnow().isoformat()
        })
        return health_data
    except Exception as e:
        atm_logger.log_system('admin', 'health_check_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao verificar saúde do sistema")

@router.get("/metrics")
async def get_system_metrics():
    """Endpoint para métricas do sistema"""
    try:
        metrics = health_monitor.get_system_metrics()
        return metrics
    except Exception as e:
        atm_logger.log_system('admin', 'metrics_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao obter métricas")

@router.get("/limits")
async def get_daily_limits():
    """Endpoint para verificar limites diários"""
    try:
        limits = health_monitor.check_daily_limits()
        return limits
    except Exception as e:
        atm_logger.log_system('admin', 'limits_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao verificar limites")

@router.get("/config")
async def get_system_config():
    """Endpoint para obter configurações do sistema"""
    try:
        config = {
            'atm': {
                'id': atm_config.get_atm_id(),
                'location': atm_config.get('atm.location'),
                'timezone': atm_config.get('atm.timezone'),
                'currency': atm_config.get('atm.currency'),
                'language': atm_config.get('atm.language')
            },
            'bitcoin': {
                'network': atm_config.get('bitcoin.network'),
                'min_amount': atm_config.get('bitcoin.min_amount'),
                'max_amount': atm_config.get('bitcoin.max_amount'),
                'service_fee_percent': atm_config.get('bitcoin.service_fee_percent'),
                'exchange_rate_source': atm_config.get('bitcoin.exchange_rate_source')
            },
            'security': atm_config.get_security_settings(),
            'hardware': {
                'printer_enabled': atm_config.get('hardware.printer_enabled'),
                'camera_enabled': atm_config.get('hardware.camera_enabled'),
                'touchscreen_enabled': atm_config.get('hardware.touchscreen_enabled'),
                'maintenance_mode': atm_config.is_maintenance_mode()
            },
            'notifications': atm_config.get_notification_settings(),
            'logging': {
                'level': atm_config.get('logging.level'),
                'retention_days': atm_config.get('logging.retention_days'),
                'audit_enabled': atm_config.get('logging.audit_enabled')
            }
        }
        return config
    except Exception as e:
        atm_logger.log_system('admin', 'config_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao obter configurações")

@router.put("/config/{key}")
async def update_config(key: str, value: Any):
    """Endpoint para atualizar configurações"""
    try:
        atm_config.set(key, value)
        atm_logger.log_audit('admin', 'config_updated', 'system', {
            'key': key,
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })
        return {"message": "Configuração atualizada com sucesso"}
    except Exception as e:
        atm_logger.log_system('admin', 'config_update_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao atualizar configuração")

@router.get("/reports/daily")
async def get_daily_report():
    """Endpoint para relatório diário"""
    try:
        report = report_generator.generate_daily_report()
        return report
    except Exception as e:
        atm_logger.log_system('admin', 'daily_report_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao gerar relatório diário")

@router.get("/reports/weekly")
async def get_weekly_report():
    """Endpoint para relatório semanal"""
    try:
        report = report_generator.generate_weekly_report()
        return report
    except Exception as e:
        atm_logger.log_system('admin', 'weekly_report_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao gerar relatório semanal")

@router.get("/reports/monthly/{year}/{month}")
async def get_monthly_report(year: int, month: int):
    """Endpoint para relatório mensal"""
    try:
        report = report_generator.generate_monthly_report(year, month)
        return report
    except Exception as e:
        atm_logger.log_system('admin', 'monthly_report_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao gerar relatório mensal")

@router.get("/reports/performance")
async def get_performance_metrics():
    """Endpoint para métricas de performance"""
    try:
        metrics = report_generator.generate_performance_metrics()
        return metrics
    except Exception as e:
        atm_logger.log_system('admin', 'performance_metrics_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao obter métricas de performance")

@router.get("/reports/history")
async def get_transaction_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
):
    """Endpoint para histórico de transações"""
    try:
        history = report_generator.generate_transaction_history(start_date, end_date, limit)
        return history
    except Exception as e:
        atm_logger.log_system('admin', 'history_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao obter histórico")

@router.post("/notifications/test")
async def test_notifications():
    """Endpoint para testar notificações"""
    try:
        # Testar webhook
        webhook_success = notification_manager.send_webhook('test', {
            'message': 'Teste de notificação',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Testar email
        email_success = notification_manager.send_email(
            'admin@redatm.com',
            'Teste de Notificação',
            'Esta é uma notificação de teste do sistema RedATM.'
        )
        
        return {
            'webhook_success': webhook_success,
            'email_success': email_success,
            'message': 'Teste de notificações executado'
        }
    except Exception as e:
        atm_logger.log_system('admin', 'notification_test_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao testar notificações")

@router.get("/security/audit/{session_code}")
async def get_audit_trail(session_code: str):
    """Endpoint para trilha de auditoria"""
    try:
        audit_trail = security_manager.generate_audit_trail(session_code)
        return audit_trail
    except Exception as e:
        atm_logger.log_system('admin', 'audit_trail_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao gerar trilha de auditoria")

@router.get("/security/compliance/{amount}")
async def check_compliance(amount: float):
    """Endpoint para verificar compliance"""
    try:
        compliance = security_manager.check_compliance_requirements(amount)
        return compliance
    except Exception as e:
        atm_logger.log_system('admin', 'compliance_check_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao verificar compliance")

@router.get("/i18n/languages")
async def get_available_languages():
    """Endpoint para obter idiomas disponíveis"""
    try:
        return {
            'available': i18n_manager.get_available_languages(),
            'current': i18n_manager.current_language
        }
    except Exception as e:
        atm_logger.log_system('admin', 'languages_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao obter idiomas")

@router.get("/i18n/translations/{language}")
async def get_translations(language: str):
    """Endpoint para obter traduções"""
    try:
        translations = i18n_manager.get_all_texts(language)
        return translations
    except Exception as e:
        atm_logger.log_system('admin', 'translations_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao obter traduções")

@router.put("/i18n/language/{language}")
async def set_language(language: str):
    """Endpoint para definir idioma"""
    try:
        i18n_manager.set_language(language)
        atm_logger.log_audit('admin', 'language_changed', 'system', {
            'language': language,
            'timestamp': datetime.utcnow().isoformat()
        })
        return {"message": f"Idioma alterado para {language}"}
    except Exception as e:
        atm_logger.log_system('admin', 'language_change_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao alterar idioma")

@router.post("/maintenance/enable")
async def enable_maintenance_mode():
    """Endpoint para habilitar modo de manutenção"""
    try:
        atm_config.set('hardware.maintenance_mode', True)
        atm_logger.log_audit('admin', 'maintenance_enabled', 'system', {
            'timestamp': datetime.utcnow().isoformat()
        })
        notification_manager.notify_maintenance_required('system', 'Modo de manutenção habilitado')
        return {"message": "Modo de manutenção habilitado"}
    except Exception as e:
        atm_logger.log_system('admin', 'maintenance_enable_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao habilitar modo de manutenção")

@router.post("/maintenance/disable")
async def disable_maintenance_mode():
    """Endpoint para desabilitar modo de manutenção"""
    try:
        atm_config.set('hardware.maintenance_mode', False)
        atm_logger.log_audit('admin', 'maintenance_disabled', 'system', {
            'timestamp': datetime.utcnow().isoformat()
        })
        return {"message": "Modo de manutenção desabilitado"}
    except Exception as e:
        atm_logger.log_system('admin', 'maintenance_disable_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao desabilitar modo de manutenção")

@router.get("/logs/recent")
async def get_recent_logs(limit: int = 100):
    """Endpoint para obter logs recentes"""
    try:
        # Em um sistema real, isso leria os arquivos de log
        # Por enquanto, retornamos uma estrutura básica
        return {
            'message': 'Logs recentes',
            'limit': limit,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        atm_logger.log_system('admin', 'logs_error', {'error': str(e)})
        raise HTTPException(status_code=500, detail="Erro ao obter logs") 