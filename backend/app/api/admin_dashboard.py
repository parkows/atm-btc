#!/usr/bin/env python3
"""
APIs do Dashboard Administrativo - LiquidGold ATM
Dashboard avançado com métricas, monitoramento e controle
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func, desc

from app.schemas import StandardResponse
from app.deps import SessionLocal
from app.core.monitoring_advanced import advanced_monitoring
from app.core.webhook_manager import webhook_manager, WebhookEventType
from app.models import Session as SessionModel
from app.core.crypto_manager import crypto_manager

router = APIRouter(prefix="/admin", tags=["admin"])

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

@router.get("/dashboard/overview", response_model=Dict[str, Any])
def get_dashboard_overview():
    """Obtém visão geral do dashboard"""
    try:
        # Métricas atuais
        current_metrics = advanced_monitoring.get_current_metrics()
        
        # Estatísticas de sessões
        db = SessionLocal()
        total_sessions = db.query(SessionModel).count()
        btc_sessions = db.query(SessionModel).filter(SessionModel.crypto_type == 'BTC').count()
        usdt_sessions = db.query(SessionModel).filter(SessionModel.crypto_type == 'USDT').count()
        
        # Sessões hoje
        today = datetime.now().date()
        sessions_today = db.query(SessionModel).filter(
            func.date(SessionModel.created_at) == today
        ).count()
        
        # Volume hoje
        volume_today = db.query(func.sum(SessionModel.amount_ars)).filter(
            func.date(SessionModel.created_at) == today
        ).scalar() or 0.0
        
        # Sessões ativas (últimas 5 horas)
        active_sessions = db.query(SessionModel).filter(
            SessionModel.created_at >= datetime.now() - timedelta(hours=5)
        ).count()
        
        db.close()
        
        # Status dos webhooks
        webhook_status = webhook_manager.get_webhook_status()
        
        return {
            "system_metrics": current_metrics.get('system', {}),
            "business_metrics": current_metrics.get('business', {}),
            "session_stats": {
                "total_sessions": total_sessions,
                "btc_sessions": btc_sessions,
                "usdt_sessions": usdt_sessions,
                "sessions_today": sessions_today,
                "active_sessions": active_sessions
            },
            "volume_stats": {
                "volume_today_ars": volume_today,
                "volume_today_usd": volume_today / 1000  # Aproximação
            },
            "webhook_status": webhook_status,
            "alerts": current_metrics.get('alerts', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dashboard: {str(e)}")

@router.get("/dashboard/metrics", response_model=Dict[str, Any])
def get_dashboard_metrics(hours: int = Query(24, description="Horas de histórico")):
    """Obtém métricas detalhadas do dashboard"""
    try:
        # Histórico de métricas
        metrics_history = advanced_monitoring.get_metrics_history(hours)
        
        # Estatísticas de sessões por período
        db = SessionLocal()
        
        # Sessões por hora (últimas 24h)
        hourly_stats = []
        for i in range(24):
            hour_start = datetime.now() - timedelta(hours=i+1)
            hour_end = datetime.now() - timedelta(hours=i)
            
            count = db.query(SessionModel).filter(
                SessionModel.created_at >= hour_start,
                SessionModel.created_at < hour_end
            ).count()
            
            hourly_stats.append({
                "hour": hour_start.hour,
                "count": count
            })
        
        # Volume por criptomoeda
        volume_by_crypto = db.query(
            SessionModel.crypto_type,
            func.sum(SessionModel.amount_ars).label('total_volume'),
            func.count(SessionModel.id).label('session_count')
        ).group_by(SessionModel.crypto_type).all()
        
        # Taxa de sucesso por período
        success_rate_data = []
        for i in range(6):  # Últimas 6 horas
            period_start = datetime.now() - timedelta(hours=i+1)
            period_end = datetime.now() - timedelta(hours=i)
            
            total = db.query(SessionModel).filter(
                SessionModel.created_at >= period_start,
                SessionModel.created_at < period_end
            ).count()
            
            # Simulação de taxa de sucesso (em produção seria baseado em status real)
            success_rate = 95.0 + (i * 0.5)  # Simulação
            success_rate_data.append({
                "period": period_start.hour,
                "success_rate": success_rate,
                "total_sessions": total
            })
        
        db.close()
        
        return {
            "metrics_history": metrics_history,
            "hourly_stats": hourly_stats,
            "volume_by_crypto": [
                {
                    "crypto_type": row.crypto_type,
                    "total_volume": float(row.total_volume),
                    "session_count": row.session_count
                }
                for row in volume_by_crypto
            ],
            "success_rate_data": success_rate_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")

# ============================================================================
# MONITORAMENTO AVANÇADO
# ============================================================================

@router.get("/monitoring/status", response_model=Dict[str, Any])
def get_monitoring_status():
    """Obtém status do sistema de monitoramento"""
    try:
        return {
            "monitoring_active": advanced_monitoring.is_monitoring,
            "current_metrics": advanced_monitoring.get_current_metrics(),
            "alert_thresholds": advanced_monitoring.alert_thresholds,
            "webhook_status": webhook_manager.get_webhook_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@router.post("/monitoring/start", response_model=StandardResponse)
def start_monitoring():
    """Inicia sistema de monitoramento"""
    try:
        advanced_monitoring.start_monitoring()
        webhook_manager.start_processing()
        
        return StandardResponse(
            success=True,
            message="Sistema de monitoramento iniciado com sucesso"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar monitoramento: {str(e)}")

@router.post("/monitoring/stop", response_model=StandardResponse)
def stop_monitoring():
    """Para sistema de monitoramento"""
    try:
        advanced_monitoring.stop_monitoring()
        webhook_manager.stop_processing()
        
        return StandardResponse(
            success=True,
            message="Sistema de monitoramento parado com sucesso"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar monitoramento: {str(e)}")

@router.get("/monitoring/alerts", response_model=List[Dict[str, Any]])
def get_monitoring_alerts(limit: int = Query(50, description="Limite de alertas")):
    """Obtém alertas do sistema"""
    try:
        alerts = advanced_monitoring.alerts[-limit:] if advanced_monitoring.alerts else []
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter alertas: {str(e)}")

# ============================================================================
# WEBHOOKS
# ============================================================================

@router.get("/webhooks/status", response_model=Dict[str, Any])
def get_webhooks_status():
    """Obtém status dos webhooks"""
    try:
        return webhook_manager.get_webhook_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter status dos webhooks: {str(e)}")

@router.get("/webhooks/registered", response_model=Dict[str, List[str]])
def get_registered_webhooks():
    """Obtém webhooks registrados"""
    try:
        return webhook_manager.get_registered_webhooks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter webhooks: {str(e)}")

@router.post("/webhooks/register", response_model=StandardResponse)
def register_webhook(event_type: str, url: str):
    """Registra novo webhook"""
    try:
        # Validar tipo de evento
        try:
            event_enum = WebhookEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Tipo de evento inválido: {event_type}")
        
        webhook_manager.register_webhook(event_enum, url)
        
        return StandardResponse(
            success=True,
            message=f"Webhook registrado com sucesso para {event_type}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar webhook: {str(e)}")

@router.delete("/webhooks/unregister", response_model=StandardResponse)
def unregister_webhook(event_type: str, url: str):
    """Remove webhook"""
    try:
        # Validar tipo de evento
        try:
            event_enum = WebhookEventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Tipo de evento inválido: {event_type}")
        
        webhook_manager.unregister_webhook(event_enum, url)
        
        return StandardResponse(
            success=True,
            message=f"Webhook removido com sucesso"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover webhook: {str(e)}")

@router.post("/webhooks/clear", response_model=StandardResponse)
def clear_webhooks(event_type: Optional[str] = None):
    """Limpa webhooks"""
    try:
        if event_type:
            try:
                event_enum = WebhookEventType(event_type)
                webhook_manager.clear_webhooks(event_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Tipo de evento inválido: {event_type}")
        else:
            webhook_manager.clear_webhooks()
        
        return StandardResponse(
            success=True,
            message="Webhooks limpos com sucesso"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar webhooks: {str(e)}")

# ============================================================================
# RELATÓRIOS
# ============================================================================

@router.get("/reports/sessions", response_model=Dict[str, Any])
def get_sessions_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    crypto_type: Optional[str] = None
):
    """Gera relatório de sessões"""
    try:
        db = SessionLocal()
        query = db.query(SessionModel)
        
        # Filtros
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(SessionModel.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(SessionModel.created_at <= end_dt)
        
        if crypto_type:
            query = query.filter(SessionModel.crypto_type == crypto_type)
        
        sessions = query.all()
        
        # Estatísticas
        total_sessions = len(sessions)
        total_volume = sum(s.amount_ars for s in sessions)
        
        # Por criptomoeda
        btc_sessions = [s for s in sessions if s.crypto_type == 'BTC']
        usdt_sessions = [s for s in sessions if s.crypto_type == 'USDT']
        
        btc_volume = sum(s.amount_ars for s in btc_sessions)
        usdt_volume = sum(s.amount_ars for s in usdt_sessions)
        
        # Por período
        sessions_by_date = {}
        for session in sessions:
            date_key = session.created_at.date().isoformat()
            if date_key not in sessions_by_date:
                sessions_by_date[date_key] = {
                    'count': 0,
                    'volume': 0.0,
                    'btc_count': 0,
                    'usdt_count': 0
                }
            
            sessions_by_date[date_key]['count'] += 1
            sessions_by_date[date_key]['volume'] += session.amount_ars
            
            if session.crypto_type == 'BTC':
                sessions_by_date[date_key]['btc_count'] += 1
            else:
                sessions_by_date[date_key]['usdt_count'] += 1
        
        db.close()
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_sessions": total_sessions,
                "total_volume_ars": total_volume,
                "btc_sessions": len(btc_sessions),
                "btc_volume_ars": btc_volume,
                "usdt_sessions": len(usdt_sessions),
                "usdt_volume_ars": usdt_volume
            },
            "daily_breakdown": sessions_by_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get("/reports/performance", response_model=Dict[str, Any])
def get_performance_report():
    """Gera relatório de performance"""
    try:
        # Métricas de performance
        metrics_history = advanced_monitoring.get_metrics_history(24)
        
        # Calcular médias
        if metrics_history.get('system_metrics'):
            system_metrics = metrics_history['system_metrics']
            
            avg_cpu = sum(m['cpu_percent'] for m in system_metrics) / len(system_metrics)
            avg_memory = sum(m['memory_percent'] for m in system_metrics) / len(system_metrics)
            avg_response_time = sum(m['response_time_avg'] for m in system_metrics) / len(system_metrics)
            avg_requests_per_second = sum(m['requests_per_second'] for m in system_metrics) / len(system_metrics)
        else:
            avg_cpu = avg_memory = avg_response_time = avg_requests_per_second = 0.0
        
        # Estatísticas de sessões
        db = SessionLocal()
        
        # Sessões por hora
        hourly_sessions = []
        for i in range(24):
            hour_start = datetime.now() - timedelta(hours=i+1)
            hour_end = datetime.now() - timedelta(hours=i)
            
            count = db.query(SessionModel).filter(
                SessionModel.created_at >= hour_start,
                SessionModel.created_at < hour_end
            ).count()
            
            hourly_sessions.append({
                "hour": hour_start.hour,
                "sessions": count
            })
        
        # Taxa de sucesso (simulação)
        success_rate = 98.5  # Simulação
        
        db.close()
        
        return {
            "performance_metrics": {
                "avg_cpu_percent": round(avg_cpu, 2),
                "avg_memory_percent": round(avg_memory, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "avg_requests_per_second": round(avg_requests_per_second, 2),
                "success_rate_percent": success_rate
            },
            "hourly_sessions": hourly_sessions,
            "alerts_count": len(advanced_monitoring.alerts),
            "webhook_events_sent": webhook_manager.stats['events_sent'],
            "webhook_events_failed": webhook_manager.stats['events_failed']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório de performance: {str(e)}")

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

@router.get("/config/alert-thresholds", response_model=Dict[str, float])
def get_alert_thresholds():
    """Obtém thresholds de alerta"""
    try:
        return advanced_monitoring.alert_thresholds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter thresholds: {str(e)}")

@router.put("/config/alert-thresholds", response_model=StandardResponse)
def update_alert_thresholds(thresholds: Dict[str, float]):
    """Atualiza thresholds de alerta"""
    try:
        for key, value in thresholds.items():
            if key in advanced_monitoring.alert_thresholds:
                advanced_monitoring.alert_thresholds[key] = value
        
        return StandardResponse(
            success=True,
            message="Thresholds atualizados com sucesso"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar thresholds: {str(e)}")

@router.get("/config/crypto-limits", response_model=Dict[str, Any])
def get_crypto_limits():
    """Obtém limites das criptomoedas"""
    try:
        return crypto_manager.get_supported_cryptos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter limites: {str(e)}") 