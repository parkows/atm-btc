from app.models import Base
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./atm_btc.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas/atualizadas com sucesso.") 