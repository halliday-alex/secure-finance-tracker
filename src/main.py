#FastAPI handles web routing, incoming requests and builds the auto-documentation.
from fastapi import FastAPI

app = FastAPI(title="Secure Finance Tracker API",description="A Cyber-secure backend framework for managing finance.",
              version="1.0.0")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "message": "Welcome to the Secure Finance Tracker API!"
    }