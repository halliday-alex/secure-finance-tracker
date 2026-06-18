# os allows Python to read environment variables directly from Mac's operating system memory
import os
from sqlalchemy import create_engine # handles database connection pools and abstrats raw SQL strings into Python code
from sqlalchemy.ext.declarative import declarative_base #blueprint builder, linking Python classes straight to database tables
from sqlalchemy.orm import sessionmaker #creates isolated database sessions, making sure data operations don't leak into each other

DB_USER = os.getenv("DB_USER","postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD","PASSWORD1432!")
DB_HOST = os.getenv("DB_HOST","localhost")
DB_PORT = os.getenv("DB_PORT","5432")
DB_NAME = os.getenv("DB_NAME","secure_finance_db")
#official PostgreSQL connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#creates database engine
engine = create_engine(DATABASE_URL)
#creates session factory. Everytime a user requests or saves data, this gives them an isolated session.
SessionLocal = sessionmaker(autocomit=False, autoflush=False, bind=engine)
#base class for future tables (Users, transactions) will inherit from
Base = declarative_base()
# A helper function safely opens database connections and guarentees closes when done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() #security steps: prevents ganding database connections draining server resources