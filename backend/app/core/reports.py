import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from .config import atm_config
from .logger import atm_logger
from .notifications import notification_manager
from ..models import Session as SessionModel

class ReportGenerator:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.logger = atm_logger
        self.notifications = notification_manager
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Gera relatório diário de transações"""
        if date is None:
            date = datetime.utcnow()
        
        try:
            db = self.db_session_factory()
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # Estatísticas básicas
            total_transactions = db.query(SessionModel).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at < end_date
            ).count()
            
            completed_transactions = db.query(SessionModel).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at < end_date,
                SessionModel.status == 'pago'
            ).count()
            
            failed_transactions = db.query(SessionModel).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at < end_date,
                SessionModel.status == 'expirada'
            ).count()
            
            # Valores
            total_amount = db.query(func.sum(SessionModel.amount_ars)).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at < end_date,
                SessionModel.status == 'pago'
            ).scalar() or 0
            
            total_btc = db.query(func.sum(SessionModel.btc_expected)).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at < end_date,
                SessionModel.status == 'pago'
            ).scalar() or 0
            
            # Taxa de conversão
            conversion_rate = (completed_transactions / total_transactions * 100) if total_transactions > 0 else 0
            
            # Transações por hora
            hourly_transactions = db.query(
                func.extract('hour', SessionModel.created_at).label('hour'),
                func.count(SessionModel.id).label('count')
            ).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at < end_date
            ).group_by(
                func.extract('hour', SessionModel.created_at)
            ).all()
            
            hourly_data = {str(hour): count for hour, count in hourly_transactions}
            
            db.close()
            
            report = {
                'date': start_date.strftime('%Y-%m-%d'),
                'total_transactions': total_transactions,
                'completed_transactions': completed_transactions,
                'failed_transactions': failed_transactions,
                'conversion_rate': round(conversion_rate, 2),
                'total_amount_ars': total_amount,
                'total_btc': total_btc,
                'hourly_distribution': hourly_data,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Log do relatório
            self.logger.log_system('reports', 'daily_report_generated', {
                'date': start_date.strftime('%Y-%m-%d'),
                'total_transactions': total_transactions,
                'total_amount': total_amount
            })
            
            return report
            
        except Exception as e:
            self.logger.log_system('reports', 'daily_report_error', {'error': str(e)})
            return {'error': str(e)}
    
    def generate_weekly_report(self, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Gera relatório semanal de transações"""
        if end_date is None:
            end_date = datetime.utcnow()
        
        try:
            db = self.db_session_factory()
            start_date = end_date - timedelta(days=7)
            
            # Estatísticas por dia
            daily_stats = db.query(
                func.date(SessionModel.created_at).label('date'),
                func.count(SessionModel.id).label('transactions'),
                func.sum(SessionModel.amount_ars).label('amount'),
                func.sum(SessionModel.btc_expected).label('btc')
            ).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at <= end_date,
                SessionModel.status == 'pago'
            ).group_by(
                func.date(SessionModel.created_at)
            ).all()
            
            # Totais
            total_transactions = sum(day.transactions for day in daily_stats)
            total_amount = sum(day.amount for day in daily_stats if day.amount)
            total_btc = sum(day.btc for day in daily_stats if day.btc)
            
            # Média diária
            avg_daily_transactions = total_transactions / 7
            avg_daily_amount = total_amount / 7
            
            # Maior e menor dia
            if daily_stats:
                max_day = max(daily_stats, key=lambda x: x.transactions)
                min_day = min(daily_stats, key=lambda x: x.transactions)
            else:
                max_day = min_day = None
            
            db.close()
            
            report = {
                'period': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'total_transactions': total_transactions,
                'total_amount_ars': total_amount,
                'total_btc': total_btc,
                'avg_daily_transactions': round(avg_daily_transactions, 2),
                'avg_daily_amount': round(avg_daily_amount, 2),
                'daily_breakdown': [
                    {
                        'date': day.date.strftime('%Y-%m-%d'),
                        'transactions': day.transactions,
                        'amount': day.amount or 0,
                        'btc': day.btc or 0
                    }
                    for day in daily_stats
                ],
                'peak_day': {
                    'date': max_day.date.strftime('%Y-%m-%d'),
                    'transactions': max_day.transactions,
                    'amount': max_day.amount or 0
                } if max_day else None,
                'lowest_day': {
                    'date': min_day.date.strftime('%Y-%m-%d'),
                    'transactions': min_day.transactions,
                    'amount': min_day.amount or 0
                } if min_day else None,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.log_system('reports', 'weekly_report_error', {'error': str(e)})
            return {'error': str(e)}
    
    def generate_monthly_report(self, year: int, month: int) -> Dict[str, Any]:
        """Gera relatório mensal de transações"""
        try:
            db = self.db_session_factory()
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            # Estatísticas por semana
            weekly_stats = db.query(
                func.extract('week', SessionModel.created_at).label('week'),
                func.count(SessionModel.id).label('transactions'),
                func.sum(SessionModel.amount_ars).label('amount'),
                func.sum(SessionModel.btc_expected).label('btc')
            ).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at < end_date,
                SessionModel.status == 'pago'
            ).group_by(
                func.extract('week', SessionModel.created_at)
            ).all()
            
            # Totais
            total_transactions = sum(week.transactions for week in weekly_stats)
            total_amount = sum(week.amount for week in weekly_stats if week.amount)
            total_btc = sum(week.btc for week in weekly_stats if week.btc)
            
            # Média semanal
            avg_weekly_transactions = total_transactions / len(weekly_stats) if weekly_stats else 0
            avg_weekly_amount = total_amount / len(weekly_stats) if weekly_stats else 0
            
            db.close()
            
            report = {
                'period': {
                    'year': year,
                    'month': month,
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'total_transactions': total_transactions,
                'total_amount_ars': total_amount,
                'total_btc': total_btc,
                'avg_weekly_transactions': round(avg_weekly_transactions, 2),
                'avg_weekly_amount': round(avg_weekly_amount, 2),
                'weekly_breakdown': [
                    {
                        'week': int(week.week),
                        'transactions': week.transactions,
                        'amount': week.amount or 0,
                        'btc': week.btc or 0
                    }
                    for week in weekly_stats
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.log_system('reports', 'monthly_report_error', {'error': str(e)})
            return {'error': str(e)}
    
    def generate_transaction_history(self, 
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None,
                                   limit: int = 100) -> Dict[str, Any]:
        """Gera histórico de transações com filtros"""
        try:
            db = self.db_session_factory()
            
            query = db.query(SessionModel)
            
            if start_date:
                query = query.filter(SessionModel.created_at >= start_date)
            if end_date:
                query = query.filter(SessionModel.created_at <= end_date)
            
            transactions = query.order_by(desc(SessionModel.created_at)).limit(limit).all()
            
            history = []
            for tx in transactions:
                history.append({
                    'session_code': tx.session_code,
                    'created_at': tx.created_at.isoformat(),
                    'status': tx.status.value if tx.status else None,
                    'amount_ars': tx.amount_ars,
                    'btc_expected': tx.btc_expected,
                    'invoice': tx.invoice,
                    'invoice_status': tx.invoice_status.value if tx.invoice_status else None
                })
            
            db.close()
            
            return {
                'transactions': history,
                'total_count': len(history),
                'filters': {
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'limit': limit
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.log_system('reports', 'history_report_error', {'error': str(e)})
            return {'error': str(e)}
    
    def generate_performance_metrics(self) -> Dict[str, Any]:
        """Gera métricas de performance do ATM"""
        try:
            db = self.db_session_factory()
            
            # Últimas 24 horas
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            # Transações por status
            status_counts = db.query(
                SessionModel.status,
                func.count(SessionModel.id)
            ).filter(
                SessionModel.created_at >= yesterday
            ).group_by(SessionModel.status).all()
            
            # Tempo médio de transação (simulado)
            avg_transaction_time = 120  # segundos
            
            # Taxa de sucesso
            total_recent = sum(count for _, count in status_counts)
            successful = sum(count for status, count in status_counts if status.value == 'pago')
            success_rate = (successful / total_recent * 100) if total_recent > 0 else 0
            
            # Valor médio por transação
            avg_amount = db.query(func.avg(SessionModel.amount_ars)).filter(
                SessionModel.created_at >= yesterday,
                SessionModel.status == 'pago'
            ).scalar() or 0
            
            db.close()
            
            return {
                'last_24h': {
                    'total_transactions': total_recent,
                    'successful_transactions': successful,
                    'success_rate': round(success_rate, 2),
                    'avg_amount': round(avg_amount, 2),
                    'avg_transaction_time': avg_transaction_time
                },
                'status_breakdown': {
                    status.value: count for status, count in status_counts
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.log_system('reports', 'performance_metrics_error', {'error': str(e)})
            return {'error': str(e)}
    
    def export_report_to_json(self, report: Dict[str, Any], filename: str) -> bool:
        """Exporta relatório para arquivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.log_system('reports', 'report_exported', {
                'filename': filename,
                'report_type': report.get('type', 'unknown')
            })
            
            return True
            
        except Exception as e:
            self.logger.log_system('reports', 'export_error', {
                'filename': filename,
                'error': str(e)
            })
            return False

# Instância global do gerador de relatórios (será inicializada no main.py)
report_generator = None 