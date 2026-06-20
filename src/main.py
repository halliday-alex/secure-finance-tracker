#FastAPI handles web routing, incoming requests and builds the auto-documentation.
from fastapi import FastAPI , Depends, HTTPException, status
from src.database.connection import engine , Base , SessionLocal #engine is the bridge to postgres, Base is database blueprint metadata.
from src.database import models  #import  models file so SQLAlchemy is aware of users, transactions, budgets
from sqlalchemy.orm import Session
from src.security.encryption import hash_password
from src.schemas import UserCreate, UserResponse
from src.database.models import User
# Initialise database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Finance Tracker API",description="A Cyber-secure backend framework for managing finance.",
              version="1.0.0")

@app.get("/")
def read_root():
    return {
        "stat   us": "healthy",
        "message": "Welcome to the Secure Finance Tracker API!"
    }

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register",response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session=Depends(get_db)):
    # Defensive Check: Ensure the user does not already exist
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Email is already registered."
        )
    # Apply hash to plaintext password
    secure_hashed_password = hash_password(user_data.password)
    # Create new user
    # create a fallback username from the email taking the information before the @
    fallback_username = user_data.email.split("@")[0]

    new_user = models.User(username = fallback_username,email = user_data.email, hashed_password = secure_hashed_password)
    # commit and save to PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user