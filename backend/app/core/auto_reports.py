#!/usr/bin/env python3
"""
Sistema de Relatórios Automáticos - LiquidGold ATM
Geração automática de relatórios por email e webhooks
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
import os

from .config import atm_config
from .logger import atm_logger
from .monitoring_advanced import advanced_monitoring
from .webhook_manager import webhook_manager
from app.deps import SessionLocal
from app.models import Session as SessionModel
from sqlalchemy import func

class AutoReportGenerator:
    """Gerador de relatórios automáticos"""
    
    def __init__(self):
        self.config = atm_config
        self.logger = atm_logger
        
        # Configurações de email
        self.email_config = {
            'enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': '',
            'password': '',
            'from_email': '',
            'to_emails': []
        }
        
        # Configurações de relatórios
        self.report_config = {
            'daily_enabled': True,
            'weekly_enabled': True,
            'monthly_enabled': True,
            'auto_save': True,
            'save_path': 'reports/'
        }
        
        # Thread de geração
        self.report_thread = None
        self.is_generating = False
        
        # Criar diretório de relatórios
        os.makedirs(self.report_config['save_path'], exist_ok=True)
    
    def start_auto_reports(self):
        """Inicia geração automática de relatórios"""
        if self.is_generating:
            return
        
        self.is_generating = True
        self.report_thread = threading.Thread(target=self._report_generation_loop, daemon=True)
        self.report_thread.start()
        
        self.logger.log_system('auto_reports', 'auto_reports_started', {
            'timestamp': datetime.now().isoformat()
        })
    
    def stop_auto_reports(self):
        """Para geração automática de relatórios"""
        self.is_generating = False
        if self.report_thread:
            self.report_thread.join()
        
        self.logger.log_system('auto_reports', 'auto_reports_stopped', {
            'timestamp': datetime.now().isoformat()
        })
    
    def _report_generation_loop(self):
        """Loop principal de geração de relatórios"""
        while self.is_generating:
            try:
                now = datetime.now()
                
                # Relatório diário (00:00)
                if now.hour == 0 and now.minute < 5:
                    self._generate_daily_report()
                
                # Relatório semanal (domingo 00:00)
                if now.weekday() == 6 and now.hour == 0 and now.minute < 5:
                    self._generate_weekly_report()
                
                # Relatório mensal (primeiro dia do mês 00:00)
                if now.day == 1 and now.hour == 0 and now.minute < 5:
                    self._generate_monthly_report()
                
                # Aguardar próximo ciclo (verificar a cada hora)
                time.sleep(3600)  # 1 hora
                
            except Exception as e:
                self.logger.log_system('auto_reports', 'report_generation_error', {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                time.sleep(3600)  # Aguardar 1 hora antes de tentar novamente
    
    def _generate_daily_report(self):
        """Gera relatório diário"""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            report_data = self._collect_report_data(start_date, end_date)
            report_data['report_type'] = 'daily'
            report_data['period'] = {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
            
            # Salvar relatório
            filename = f"daily_report_{yesterday.strftime('%Y%m%d')}.json"
            self._save_report(filename, report_data)
            
            # Enviar por email
            if self.email_config['enabled']:
                self._send_report_email('Relatório Diário - LiquidGold ATM', report_data, filename)
            
            # Enviar webhook
            webhook_manager.send_business_metrics(report_data)
            
            self.logger.log_system('auto_reports', 'daily_report_generated', {
                'date': yesterday.isoformat(),
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.log_system('auto_reports', 'daily_report_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def _generate_weekly_report(self):
        """Gera relatório semanal"""
        try:
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=6)
            
            report_data = self._collect_report_data(start_date, end_date)
            report_data['report_type'] = 'weekly'
            report_data['period'] = {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
            
            # Salvar relatório
            filename = f"weekly_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
            self._save_report(filename, report_data)
            
            # Enviar por email
            if self.email_config['enabled']:
                self._send_report_email('Relatório Semanal - LiquidGold ATM', report_data, filename)
            
            # Enviar webhook
            webhook_manager.send_business_metrics(report_data)
            
            self.logger.log_system('auto_reports', 'weekly_report_generated', {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.log_system('auto_reports', 'weekly_report_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def _generate_monthly_report(self):
        """Gera relatório mensal"""
        try:
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date.replace(day=1)
            
            report_data = self._collect_report_data(start_date, end_date)
            report_data['report_type'] = 'monthly'
            report_data['period'] = {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
            
            # Salvar relatório
            filename = f"monthly_report_{start_date.strftime('%Y%m')}.json"
            self._save_report(filename, report_data)
            
            # Enviar por email
            if self.email_config['enabled']:
                self._send_report_email('Relatório Mensal - LiquidGold ATM', report_data, filename)
            
            # Enviar webhook
            webhook_manager.send_business_metrics(report_data)
            
            self.logger.log_system('auto_reports', 'monthly_report_generated', {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.log_system('auto_reports', 'monthly_report_error', {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def _collect_report_data(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Coleta dados para relatório"""
        db = SessionLocal()
        
        try:
            # Sessões no período
            sessions = db.query(SessionModel).filter(
                SessionModel.created_at >= start_date,
                SessionModel.created_at <= end_date
            ).all()
            
            # Estatísticas gerais
            total_sessions = len(sessions)
            total_volume = sum(s.amount_ars for s in sessions)
            
            # Por criptomoeda
            btc_sessions = [s for s in sessions if s.crypto_type == 'BTC']
            usdt_sessions = [s for s in sessions if s.crypto_type == 'USDT']
            
            btc_volume = sum(s.amount_ars for s in btc_sessions)
            usdt_volume = sum(s.amount_ars for s in usdt_sessions)
            
            # Por dia
            daily_stats = {}
            current_date = start_date.date()
            end_date_obj = end_date.date()
            
            while current_date <= end_date_obj:
                day_sessions = [s for s in sessions if s.created_at.date() == current_date]
                daily_stats[current_date.isoformat()] = {
                    'sessions': len(day_sessions),
                    'volume': sum(s.amount_ars for s in day_sessions),
                    'btc_sessions': len([s for s in day_sessions if s.crypto_type == 'BTC']),
                    'usdt_sessions': len([s for s in day_sessions if s.crypto_type == 'USDT'])
                }
                current_date += timedelta(days=1)
            
            # Métricas de performance
            metrics_history = advanced_monitoring.get_metrics_history(
                int((end_date - start_date).total_seconds() / 3600)
            )
            
            # Top sessões por valor
            top_sessions = sorted(sessions, key=lambda x: x.amount_ars, reverse=True)[:10]
            top_sessions_data = [
                {
                    'session_code': s.session_code,
                    'crypto_type': s.crypto_type,
                    'amount_ars': s.amount_ars,
                    'created_at': s.created_at.isoformat()
                }
                for s in top_sessions
            ]
            
            return {
                'summary': {
                    'total_sessions': total_sessions,
                    'total_volume_ars': total_volume,
                    'btc_sessions': len(btc_sessions),
                    'btc_volume_ars': btc_volume,
                    'usdt_sessions': len(usdt_sessions),
                    'usdt_volume_ars': usdt_volume,
                    'avg_session_value': total_volume / total_sessions if total_sessions > 0 else 0
                },
                'daily_breakdown': daily_stats,
                'performance_metrics': metrics_history.get('system_metrics', []),
                'top_sessions': top_sessions_data,
                'webhook_stats': webhook_manager.stats,
                'alerts_count': len(advanced_monitoring.alerts)
            }
            
        finally:
            db.close()
    
    def _save_report(self, filename: str, data: Dict[str, Any]):
        """Salva relatório em arquivo"""
        if not self.report_config['auto_save']:
            return
        
        filepath = os.path.join(self.report_config['save_path'], filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def _send_report_email(self, subject: str, report_data: Dict[str, Any], filename: str):
        """Envia relatório por email"""
        if not self.email_config['enabled'] or not self.email_config['to_emails']:
            return
        
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = subject
            
            # Corpo do email
            body = self._generate_email_body(report_data)
            msg.attach(MIMEText(body, 'html'))
            
            # Anexar arquivo JSON
            filepath = os.path.join(self.report_config['save_path'], filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.log_system('auto_reports', 'report_email_sent', {
                'subject': subject,
                'recipients': self.email_config['to_emails'],
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.log_system('auto_reports', 'report_email_error', {
                'error': str(e),
                'subject': subject,
                'timestamp': datetime.now().isoformat()
            })
    
    def _generate_email_body(self, report_data: Dict[str, Any]) -> str:
        """Gera corpo do email em HTML"""
        summary = report_data['summary']
        period = report_data.get('period', {})
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f7931a; color: white; padding: 20px; text-align: center; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: white; border-radius: 5px; }}
                .metric h3 {{ margin: 0; color: #f7931a; }}
                .metric p {{ margin: 5px 0; font-size: 24px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f7931a; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 LiquidGold ATM - Relatório Automático</h1>
                <p>Período: {period.get('start', 'N/A')} a {period.get('end', 'N/A')}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Resumo Executivo</h2>
                <div class="metric">
                    <h3>Total de Sessões</h3>
                    <p>{summary['total_sessions']:,}</p>
                </div>
                <div class="metric">
                    <h3>Volume Total (ARS)</h3>
                    <p>${summary['total_volume_ars']:,.2f}</p>
                </div>
                <div class="metric">
                    <h3>Sessões BTC</h3>
                    <p>{summary['btc_sessions']:,}</p>
                </div>
                <div class="metric">
                    <h3>Sessões USDT</h3>
                    <p>{summary['usdt_sessions']:,}</p>
                </div>
                <div class="metric">
                    <h3>Volume BTC (ARS)</h3>
                    <p>${summary['btc_volume_ars']:,.2f}</p>
                </div>
                <div class="metric">
                    <h3>Volume USDT (ARS)</h3>
                    <p>${summary['usdt_volume_ars']:,.2f}</p>
                </div>
            </div>
            
            <h2>📈 Top 10 Sessões por Valor</h2>
            <table>
                <tr>
                    <th>Código da Sessão</th>
                    <th>Criptomoeda</th>
                    <th>Valor (ARS)</th>
                    <th>Data</th>
                </tr>
        """
        
        for session in report_data.get('top_sessions', [])[:10]:
            html += f"""
                <tr>
                    <td>{session['session_code']}</td>
                    <td>{session['crypto_type']}</td>
                    <td>${session['amount_ars']:,.2f}</td>
                    <td>{session['created_at'][:10]}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <p><em>Relatório gerado automaticamente pelo sistema LiquidGold ATM</em></p>
        </body>
        </html>
        """
        
        return html
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, 
                       password: str, from_email: str, to_emails: List[str]):
        """Configura email para relatórios"""
        self.email_config.update({
            'enabled': True,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'from_email': from_email,
            'to_emails': to_emails
        })
        
        self.logger.log_system('auto_reports', 'email_configured', {
            'smtp_server': smtp_server,
            'from_email': from_email,
            'to_emails_count': len(to_emails),
            'timestamp': datetime.now().isoformat()
        })
    
    def generate_custom_report(self, start_date: datetime, end_date: datetime, 
                              report_type: str = 'custom') -> Dict[str, Any]:
        """Gera relatório customizado"""
        try:
            report_data = self._collect_report_data(start_date, end_date)
            report_data['report_type'] = report_type
            report_data['period'] = {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
            
            # Salvar relatório
            filename = f"{report_type}_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.json"
            self._save_report(filename, report_data)
            
            return report_data
            
        except Exception as e:
            self.logger.log_system('auto_reports', 'custom_report_error', {
                'error': str(e),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'timestamp': datetime.now().isoformat()
            })
            raise
    
    def get_report_status(self) -> Dict[str, Any]:
        """Retorna status dos relatórios automáticos"""
        return {
            'auto_reports_active': self.is_generating,
            'email_enabled': self.email_config['enabled'],
            'auto_save_enabled': self.report_config['auto_save'],
            'save_path': self.report_config['save_path'],
            'daily_enabled': self.report_config['daily_enabled'],
            'weekly_enabled': self.report_config['weekly_enabled'],
            'monthly_enabled': self.report_config['monthly_enabled']
        }

# Instância global do gerador de relatórios
auto_report_generator = AutoReportGenerator() 