import time
import threading
import logging
from sqlalchemy.orm import sessionmaker
from app.models import Session as SessionModel, InvoiceStatusEnum, SessionStatusEnum
from datetime import datetime

def mock_check_invoice_paid(invoice: str) -> bool:
    """Mock: Simula que invoices terminados em '7' são pagos após 1 minuto"""
    return invoice and invoice[-1] == '7'

def invoice_checker_loop(db_session_factory: sessionmaker, interval: int = 30):
    """Loop principal do verificador de invoices"""
    while True:
        try:
            db = db_session_factory()
            sessions = db.query(SessionModel).filter(
                SessionModel.invoice_status == InvoiceStatusEnum.aguardando,
                SessionModel.invoice.isnot(None)
            ).all()
            
            for session in sessions:
                # Verificar expiração automática
                if session.status == SessionStatusEnum.aguardando_pagamento and datetime.utcnow() > session.expires_at:
                    session.invoice_status = InvoiceStatusEnum.expirado
                    session.status = SessionStatusEnum.expirada
                    logging.info(f"[INVOICE CHECKER] Sessão {session.session_code} expirada automaticamente.")
                
                # Verificar pagamento (mock)
                elif mock_check_invoice_paid(session.invoice):
                    session.invoice_status = InvoiceStatusEnum.pago
                    session.status = SessionStatusEnum.concluida
                    logging.info(f"[INVOICE CHECKER] Invoice pago detectado para sessão {session.session_code}")
            
            db.commit()
            db.close()
            
        except Exception as e:
            logging.error(f"[INVOICE CHECKER] Erro no loop: {e}")
            if 'db' in locals():
                db.close()
        
        time.sleep(interval)

def start_invoice_checker(db_session_factory):
    """Inicia o verificador de invoices em background"""
    t = threading.Thread(target=invoice_checker_loop, args=(db_session_factory,), daemon=True)
    t.start()
    logging.info("[INVOICE CHECKER] Verificador de invoices iniciado") 