from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.core.session_manager import SessionManager

DATABASE_URL = "sqlite:///./liquidgold_atm.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

# Instância global do session manager
session_manager = SessionManager(SessionLocal)

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session_factory():
    """Retorna a factory de sessões do banco"""
    return SessionLocal 