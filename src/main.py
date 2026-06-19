#FastAPI handles web routing, incoming requests and builds the auto-documentation.
from fastapi import FastAPI
from src.database.connection import engine,Base #engine is the bridge to postgres, Base is database blueprint metadata.
from src.database import models #import  models file so SQLAlchemy is aware of users, transactions, budgets

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Finance Tracker API",description="A Cyber-secure backend framework for managing finance.",
              version="1.0.0")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "message": "Welcome to the Secure Finance Tracker API!"
    }