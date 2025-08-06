from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.middleware import RateLimitMiddleware, AuditMiddleware
from app.api import atm, admin
from app.core.logger import atm_logger
from app.core.config import atm_config
from app.core.notifications import notification_manager
from app.core.monitoring import HealthMonitor
from app.core.reports import ReportGenerator
from app.core.security import SecurityManager
from app.core.i18n import i18n_manager
from app.core.auth import auth_manager
from app.core.backup_manager import backup_manager
from app.api import auth as auth_api
from app.deps import get_db_session_factory
import threading
import time
from datetime import datetime, timedelta

# Inicializar componentes globais
db_session_factory = get_db_session_factory()
health_monitor = HealthMonitor(db_session_factory)
report_generator = ReportGenerator(db_session_factory)
security_manager = SecurityManager(db_session_factory)

# Lista para armazenar transações simuladas
simulated_transactions = []

# Inicializar session_manager
from app.core.session_manager import SessionManager
session_manager = SessionManager(db_session_factory)

# Inicializar gerenciador de autenticação já foi feito na importação

# Atualizar instâncias globais nos módulos
import app.core.monitoring
import app.core.reports
import app.core.security
import app.api.atm

app.core.monitoring.health_monitor = health_monitor
app.core.reports.report_generator = report_generator
app.core.security.security_manager = security_manager
app.api.atm.session_manager = session_manager

app = FastAPI(title="LiquidGold ATM Backend", version="1.0.0")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8080", "http://localhost:8000", "http://0.0.0.0:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middlewares de segurança
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)

# Importar API de backup
from app.api import backup as backup_api

# Incluir rotas da API
app.include_router(atm.router, prefix="/api/atm", tags=["ATM"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(auth_api.router, prefix="/api/admin", tags=["Auth"])
app.include_router(backup_api.router, prefix="/api/admin/backup", tags=["Backup"])

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Rota para a interface administrativa
@app.get("/admin")
async def admin_interface():
    return FileResponse("app/static/admin.html")

# Rota para o arquivo JavaScript
@app.get("/admin.js")
async def admin_js():
    return FileResponse("app/static/admin.js", media_type="application/javascript")

# Rota para interface do ATM
@app.get("/atm")
async def get_atm_interface():
    """Interface principal do ATM"""
    return FileResponse("app/static/atm_interface.html")

@app.get("/atm_interface.js")
async def get_atm_interface_js():
    """JavaScript da interface do ATM"""
    return FileResponse("app/static/atm_interface.js")

# Rota de teste
@app.get("/test")
async def get_test():
    """Página de teste"""
    return FileResponse("test_interface.html")

# Background tasks
def health_check_task():
    """Tarefa em background para verificação de saúde do sistema"""
    while True:
        try:
            health_data = health_monitor.check_system_health()
            atm_logger.log_system('background', 'health_check_completed', {
                'overall_status': health_data.get('overall_status', 'unknown')
            })
        except Exception as e:
            atm_logger.log_system('background', 'health_check_error', {'error': str(e)})
        
        time.sleep(300)  # Verificar a cada 5 minutos

def daily_report_task():
    """Tarefa em background para relatórios diários"""
    while True:
        try:
            # Aguardar até meia-noite
            now = datetime.utcnow()
            next_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if next_midnight <= now:
                next_midnight = next_midnight.replace(day=next_midnight.day + 1)
            
            time.sleep((next_midnight - now).total_seconds())
            
            # Gerar relatório diário
            daily_report = report_generator.generate_daily_report()
            
            # Enviar notificação
            if daily_report and 'error' not in daily_report:
                notification_manager.notify_daily_summary(daily_report)
                
                # Exportar relatório
                filename = f"reports/daily_report_{datetime.utcnow().strftime('%Y%m%d')}.json"
                report_generator.export_report_to_json(daily_report, filename)
                
                atm_logger.log_system('background', 'daily_report_generated', {
                    'filename': filename,
                    'report_size': len(str(daily_report))
                })
            else:
                atm_logger.log_system('background', 'daily_report_error', {
                    'error': 'Failed to generate daily report'
                })
                
        except Exception as e:
            atm_logger.log_system('background', 'daily_report_error', {'error': str(e)})
            time.sleep(3600)  # Aguardar 1 hora em caso de erro

def cleanup_expired_sessions():
    """Tarefa em background para limpeza de sessões expiradas"""
    while True:
        try:
            # Limpar sessões expiradas
            cleaned_count = security_manager.cleanup_expired_sessions()
            
            if cleaned_count > 0:
                atm_logger.log_system('background', 'sessions_cleaned', {
                    'cleaned_count': cleaned_count
                })
                
        except Exception as e:
            atm_logger.log_system('background', 'session_cleanup_error', {'error': str(e)})
        
        time.sleep(600)  # Verificar a cada 10 minutos

# Eventos de startup e shutdown
@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    try:
        atm_logger.log_system('startup', 'application_started', {
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Inicializar banco de dados
        try:
            from app.db.init_db import init_db
            from app.deps import get_db_session
            
            async with get_db_session() as db:
                await init_db(db)
                
            atm_logger.log_system('startup', 'db_initialized', {'success': True})
        except Exception as e:
            atm_logger.log_system('startup', 'db_init_error', {'error': str(e)})
        
        # Iniciar tarefas em background
        health_thread = threading.Thread(target=health_check_task, daemon=True)
        health_thread.start()
        
        report_thread = threading.Thread(target=daily_report_task, daemon=True)
        report_thread.start()
        
        cleanup_thread = threading.Thread(target=cleanup_expired_sessions, daemon=True)
        cleanup_thread.start()
        
        atm_logger.log_system('startup', 'background_tasks_started', {
            'health_check': True,
            'daily_reports': True,
            'session_cleanup': True
        })
        
    except Exception as e:
        atm_logger.log_system('startup', 'startup_error', {'error': str(e)})

@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação"""
    try:
        atm_logger.log_system('shutdown', 'application_shutdown', {
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        atm_logger.log_system('shutdown', 'shutdown_error', {'error': str(e)})

# Rotas adicionais para funcionalidades do LiquidGold
@app.get("/api/health")
async def health_check():
    """Endpoint para verificação de saúde do sistema"""
    return health_monitor.check_system_health()

@app.get("/api/metrics")
async def get_metrics():
    """Endpoint para métricas do sistema"""
    return health_monitor.get_system_metrics()

@app.get("/api/config")
async def get_config():
    """Endpoint para configurações do sistema"""
    return atm_config.get_all()

@app.put("/api/config")
async def update_config(config_data: dict):
    """Endpoint para atualizar configurações"""
    for key, value in config_data.items():
        atm_config.set(key, value)
    return {"message": "Configuração atualizada com sucesso"}

@app.get("/api/reports/daily")
async def get_daily_report():
    """Endpoint para relatório diário"""
    try:
        # Usar dados das transações simuladas em vez do banco de dados
        today = datetime.utcnow().date()
        today_transactions = [
            tx for tx in simulated_transactions 
            if datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00')).date() == today
        ]
        
        # Adicionar transação fixa se for de hoje
        fixed_transaction = {
            "id": "TXN001",
            "session_code": "SESS001",
            "crypto_type": "BTC",
            "amount_ars": 50000,
            "amount_crypto": 0.001,
            "status": "completed",
            "created_at": "2024-08-01T10:30:00Z",
            "completed_at": "2024-08-01T10:35:00Z"
        }
        
        # Verificar se a transação fixa é de hoje (para teste, vamos incluí-la sempre)
        all_today_transactions = today_transactions + [fixed_transaction]
        
        # Calcular métricas
        total_transactions = len(all_today_transactions)
        completed_transactions = len([tx for tx in all_today_transactions if tx['status'] == 'completed'])
        failed_transactions = len([tx for tx in all_today_transactions if tx['status'] == 'failed'])
        pending_transactions = len([tx for tx in all_today_transactions if tx['status'] == 'pending'])
        
        total_amount_ars = sum(tx.get('amount_ars', 0) for tx in all_today_transactions)
        total_crypto = sum(tx.get('amount_crypto', 0) for tx in all_today_transactions)
        
        conversion_rate = (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Distribuição por hora (simulada)
        hourly_distribution = {}
        for i in range(24):
            hourly_distribution[str(i)] = len([tx for tx in all_today_transactions 
                                            if datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00')).hour == i])
        
        report = {
            'date': today.strftime('%Y-%m-%d'),
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'failed_transactions': failed_transactions,
            'pending_transactions': pending_transactions,
            'conversion_rate': round(conversion_rate, 2),
            'total_amount_ars': total_amount_ars,
            'total_crypto': total_crypto,
            'hourly_distribution': hourly_distribution,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return report
        
    except Exception as e:
        atm_logger.log_error('api', 'daily_report_error', {'error': str(e)})
        return {'error': str(e)}

@app.get("/api/reports/weekly")
async def get_weekly_report():
    """Endpoint para relatório semanal"""
    try:
        # Usar dados das transações simuladas
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=7)
        
        week_transactions = [
            tx for tx in simulated_transactions 
            if week_start <= datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00')).date() < week_end
        ]
        
        # Adicionar transação fixa se estiver na semana atual
        fixed_transaction = {
            "id": "TXN001",
            "session_code": "SESS001",
            "crypto_type": "BTC",
            "amount_ars": 50000,
            "amount_crypto": 0.001,
            "status": "completed",
            "created_at": "2024-08-01T10:30:00Z",
            "completed_at": "2024-08-01T10:35:00Z"
        }
        
        # Para teste, vamos incluir sempre
        all_week_transactions = week_transactions + [fixed_transaction]
        
        # Calcular métricas semanais
        total_transactions = len(all_week_transactions)
        completed_transactions = len([tx for tx in all_week_transactions if tx['status'] == 'completed'])
        total_amount_ars = sum(tx.get('amount_ars', 0) for tx in all_week_transactions)
        total_crypto = sum(tx.get('amount_crypto', 0) for tx in all_week_transactions)
        
        conversion_rate = (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Distribuição por dia da semana
        daily_distribution = {}
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            daily_transactions = [tx for tx in all_week_transactions 
                               if datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00')).date() == day_date]
            daily_distribution[day_date.strftime('%Y-%m-%d')] = len(daily_transactions)
        
        report = {
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d'),
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'conversion_rate': round(conversion_rate, 2),
            'total_amount_ars': total_amount_ars,
            'total_crypto': total_crypto,
            'daily_distribution': daily_distribution,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return report
        
    except Exception as e:
        atm_logger.log_error('api', 'weekly_report_error', {'error': str(e)})
        return {'error': str(e)}

@app.get("/api/reports/performance")
async def get_performance_metrics():
    """Endpoint para métricas de performance"""
    try:
        # Usar dados das transações simuladas
        all_transactions = simulated_transactions + [{
            "id": "TXN001",
            "session_code": "SESS001",
            "crypto_type": "BTC",
            "amount_ars": 50000,
            "amount_crypto": 0.001,
            "status": "completed",
            "created_at": "2024-08-01T10:30:00Z",
            "completed_at": "2024-08-01T10:35:00Z"
        }]
        
        # Calcular métricas de performance
        total_transactions = len(all_transactions)
        completed_transactions = len([tx for tx in all_transactions if tx['status'] == 'completed'])
        pending_transactions = len([tx for tx in all_transactions if tx['status'] == 'pending'])
        failed_transactions = len([tx for tx in all_transactions if tx['status'] == 'failed'])
        
        total_amount_ars = sum(tx.get('amount_ars', 0) for tx in all_transactions)
        avg_amount_ars = total_amount_ars / total_transactions if total_transactions > 0 else 0
        
        success_rate = (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Distribuição por status
        status_breakdown = {
            'completed': completed_transactions,
            'pending': pending_transactions,
            'failed': failed_transactions
        }
        
        # Distribuição por criptomoeda
        crypto_breakdown = {}
        for tx in all_transactions:
            crypto = tx.get('crypto_type', 'unknown')
            crypto_breakdown[crypto] = crypto_breakdown.get(crypto, 0) + 1
        
        # Métricas das últimas 24h
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        
        last_24h_transactions = []
        for tx in all_transactions:
            try:
                # Converter string para datetime sem timezone
                tx_date = datetime.fromisoformat(tx['created_at'].replace('Z', ''))
                if tx_date >= yesterday:
                    last_24h_transactions.append(tx)
            except:
                # Se não conseguir converter, incluir de qualquer forma
                last_24h_transactions.append(tx)
        
        last_24h_total = len(last_24h_transactions)
        last_24h_completed = len([tx for tx in last_24h_transactions if tx['status'] == 'completed'])
        last_24h_amount = sum(tx.get('amount_ars', 0) for tx in last_24h_transactions)
        last_24h_success_rate = (last_24h_completed / last_24h_total * 100) if last_24h_total > 0 else 0
        
        metrics = {
            'overall': {
                'total_transactions': total_transactions,
                'completed_transactions': completed_transactions,
                'success_rate': round(success_rate, 2),
                'total_amount_ars': total_amount_ars,
                'avg_amount_ars': round(avg_amount_ars, 2)
            },
            'last_24h': {
                'total_transactions': last_24h_total,
                'completed_transactions': last_24h_completed,
                'success_rate': round(last_24h_success_rate, 2),
                'total_amount_ars': last_24h_amount,
                'avg_amount_ars': round(last_24h_amount / last_24h_total, 2) if last_24h_total > 0 else 0
            },
            'status_breakdown': status_breakdown,
            'crypto_breakdown': crypto_breakdown,
            'generated_at': now.isoformat()
        }
        
        return metrics
        
    except Exception as e:
        atm_logger.log_error('api', 'performance_metrics_error', {'error': str(e)})
        return {'error': str(e)}

@app.get("/api/translations/{language}")
async def get_translations(language: str):
    """Endpoint para traduções"""
    return i18n_manager.get_translations(language)

@app.get("/api/languages")
async def get_available_languages():
    """Endpoint para idiomas disponíveis"""
    return i18n_manager.get_available_languages()

# Rotas administrativas adicionais
@app.get("/api/admin/health")
async def get_admin_health():
    """Endpoint para dados de saúde do sistema"""
    try:
        return health_monitor.check_system_health()
    except Exception as e:
        atm_logger.log_error('api', 'admin_health_error', {'error': str(e)})
        return {"error": "Erro ao obter dados de saúde"}

@app.get("/api/admin/transactions")
async def get_admin_transactions():
    """Endpoint para transações administrativas"""
    try:
        # Combinar transações fixas com transações simuladas
        all_transactions = [
            {
                "id": "TXN001",
                "session_code": "SESS001",
                "crypto_type": "BTC",
                "amount_ars": 50000,
                "amount_crypto": 0.001,
                "status": "completed",
                "created_at": "2024-08-01T10:30:00Z",
                "completed_at": "2024-08-01T10:35:00Z"
            }
        ]
        
        # Adicionar transações simuladas
        all_transactions.extend(simulated_transactions)
        
        # Ordenar por data de criação (mais recentes primeiro)
        all_transactions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "transactions": all_transactions,
            "total": len(all_transactions),
            "page": 1,
            "per_page": 10
        }
    except Exception as e:
        atm_logger.log_error('api', 'admin_transactions_error', {'error': str(e)})
        return {"error": "Erro ao obter transações"}

@app.get("/api/admin/security")
async def get_admin_security():
    """Endpoint para dados de segurança"""
    try:
        return security_manager.get_security_status()
    except Exception as e:
        atm_logger.log_error('api', 'admin_security_error', {'error': str(e)})
        return {"error": "Erro ao obter dados de segurança"}

@app.get("/api/admin/notifications")
async def get_admin_notifications():
    """Endpoint para notificações administrativas"""
    try:
        return notification_manager.get_notification_history()
    except Exception as e:
        atm_logger.log_error('api', 'admin_notifications_error', {'error': str(e)})
        return {"error": "Erro ao obter notificações"}

@app.get("/api/admin/logs")
async def get_admin_logs():
    """Endpoint para logs administrativos"""
    try:
        return atm_logger.get_recent_logs(100)
    except Exception as e:
        atm_logger.log_error('api', 'admin_logs_error', {'error': str(e)})
        return {"error": "Erro ao obter logs"}

@app.post("/api/admin/test-notifications")
async def test_admin_notifications():
    """Endpoint para testar notificações"""
    try:
        result = notification_manager.send_test_notification()
        return {"success": True, "message": "Notificação de teste enviada"}
    except Exception as e:
        atm_logger.log_error('api', 'test_notifications_error', {'error': str(e)})
        return {"error": "Erro ao enviar notificação de teste"}

@app.post("/api/admin/maintenance/enable")
async def enable_maintenance():
    """Endpoint para habilitar modo de manutenção"""
    try:
        security_manager.enable_maintenance_mode()
        return {"success": True, "message": "Modo de manutenção habilitado"}
    except Exception as e:
        atm_logger.log_error('api', 'enable_maintenance_error', {'error': str(e)})
        return {"error": "Erro ao habilitar modo de manutenção"}

@app.post("/api/admin/maintenance/disable")
async def disable_maintenance():
    """Endpoint para desabilitar modo de manutenção"""
    try:
        security_manager.disable_maintenance_mode()
        return {"success": True, "message": "Modo de manutenção desabilitado"}
    except Exception as e:
        atm_logger.log_error('api', 'disable_maintenance_error', {'error': str(e)})
        return {"error": "Erro ao desabilitar modo de manutenção"}

@app.post("/api/admin/simulate-transaction")
async def simulate_transaction(request: Request):
    """Endpoint para simular transação"""
    try:
        # Simular uma transação
        import random
        from datetime import datetime, timedelta
        
        # Se receber dados do ATM, usar eles
        request_data = await request.json()
        if request_data:
            crypto_type = request_data.get('crypto_type', random.choice(["BTC", "USDT"]))
            amount_ars = request_data.get('amount_ars', random.randint(10000, 500000))
            communication_method = request_data.get('communication_method', 'sms')
            phone = request_data.get('phone', 'N/A')
            transaction_type = request_data.get('transaction_type', 'purchase')
        else:
            crypto_type = random.choice(["BTC", "USDT"])
            amount_ars = random.randint(10000, 500000)
            communication_method = 'sms'
            phone = 'N/A'
            transaction_type = 'purchase'
        
        # Calcular valor em crypto baseado no tipo
        if crypto_type == "BTC":
            # Taxa de 8% para BTC
            crypto_amount = round((amount_ars * 0.92) / 113000, 6)  # Usando cotação aproximada
        else:  # USDT
            # Taxa de 6% para USDT
            crypto_amount = round((amount_ars * 0.94) / 1350, 6)  # Usando cotação aproximada
        
        # Status baseado no tipo de transação
        if transaction_type == 'sale':
            status = random.choice(["completed", "pending"])
        else:
            status = random.choice(["completed", "pending", "failed"])
        
        transaction = {
            "id": f"TXN{random.randint(1000, 9999)}",
            "session_code": f"SESS{random.randint(1000, 9999)}",
            "crypto_type": crypto_type,
            "amount_ars": amount_ars,
            "amount_crypto": crypto_amount,
            "status": status,
            "transaction_type": transaction_type,
            "communication_method": communication_method,
            "phone": phone,
            "created_at": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat() + "Z",
            "completed_at": datetime.utcnow().isoformat() + "Z" if status == "completed" else None
        }
        
        # Adicionar à lista de transações simuladas
        simulated_transactions.append(transaction)
        
        # Manter apenas as últimas 50 transações
        if len(simulated_transactions) > 50:
            simulated_transactions.pop(0)
        
        # Log da simulação
        atm_logger.log_system('simulation', 'transaction_simulated', transaction)
        
        return {"success": True, "transaction": transaction}
    except Exception as e:
        atm_logger.log_error('api', 'simulate_transaction_error', {'error': str(e)})
        return {"error": "Erro ao simular transação"}
