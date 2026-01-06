# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# CHANGE THIS to your actual Postgres password
# Format: postgresql://username:password@localhost/databasename
# Format: postgresql://user:password@localhost:PORT/dbname
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:8008@localhost:5434/speakflow"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to give access to the database in every API call
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# .\venv\Scripts\activate  
#pip install fastapi uvicorn sqlalchemy psycopg2-binary passlib[argon2] python-dotenv groq python-multipart pydantic[email]
#uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload