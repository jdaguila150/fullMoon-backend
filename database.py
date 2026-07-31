# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker

# DATABASE_URL = "sqlite:///./fullmoon.db"

# # check_same_thread: False es necesario para SQLite en FastAPI
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# # Dependencia para inyectar la sesión en las rutas
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()




import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Cargamos las variables del .env
load_dotenv()

# Obtenemos la URL. Si no existe, usamos SQLite local por defecto.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Corrección vital para URLs de Render/Supabase/Neon
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requiere un argumento especial para hilos, Postgres no.
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()