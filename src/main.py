#FastAPI handles web routing, incoming requests and builds the auto-documentation.
from fastapi import FastAPI , Depends, HTTPException, status
from src.database.connection import engine , Base , SessionLocal #engine is the bridge to postgres, Base is database blueprint metadata.
from src.database import models  #import  models file so SQLAlchemy is aware of users, transactions, budgets
from sqlalchemy.orm import Session
from src.security.encryption import hash_password , verify_password, create_access_token, SECRET_KEY, ALGORITHM
from src.schemas import UserCreate, UserResponse , UserLogin, TokenResponse, TransactionCreate, TransactionResponse
from src.database.models import User
from src.security.data_encryption import encrypt_data, decrypt_data
from typing import List
import json
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

@app.post("/auth/login", response_model=TokenResponse)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    # Look up the identity target record
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    # Defensive Mitigation: If user does not exist, through exception
    #Prevents user enumeration where attacker maps out registered emails.

    generic_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail = "Incorrect email or password.",
                                      headers={"WWW-Authenticate":"Bearer"},)
    if not user:
        raise generic_exception
    # Cryptographically verify the password string against database hash
    if not verify_password(user_data.password, user.hashed_password):
        raise generic_exception
    #Issue the secure authorisation token
    token_payload = {"sub": str(user.id), "email":user.email}
    jwt_access_token = create_access_token(data= token_payload)

    return {"access_token": jwt_access_token, "token_type": "bearer"}

# Configure FastAPI to recognise bearer authentication tokens in request headers
security_bearer = HTTPBearer()
def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)) -> int:
    """
    Security Dependency: Decodes JWT, validats authenticity and returns user identity.
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate session credentials.",
                                          headers={"WWW-Authenticate":"Bearer"},)
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Protected Transactions route
@app.post("/transactions",response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    # Isolate parameters and pack meta field into a JSON string block
    financial_meta = {
        "amount": transaction_data.amount,
        "category": transaction_data.category
    }
    meta_json_string = json.dumps(financial_meta)

    #Cryptographic Transformation Layer (AES-256 Encryption Application)

    cipher_title = encrypt_data(transaction_data.title)
    cipher_data = encrypt_data(meta_json_string)
    
    #Instantiate entity obkect matching schema
    new_transaction = models.Transaction(
        encrypted_title = cipher_title,
        data_string=cipher_data,
        user_id=current_user_id
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
# decrypt to return a clean response to the authentication client
    return TransactionResponse(
        id=new_transaction.id,
        title = decrypt_data(new_transaction.encrypted_title),
        amount=financial_meta["amount"],
        category=financial_meta["category"],
        user_id=new_transaction.user_id)
    
@app.get("/transactions",response_model= List[TransactionResponse])
def get_user_transactions( db: Session = Depends(get_db),current_user_id: int = Depends(get_current_user_id)):
    """
    Protected Query Route: Retrives, decrypts and reconstructs transaction history exclusively for the authenticated user session
    """
    # Query only transaction belonging to the token holder
    raw_transactions = db.query(models.Transaction).filter(models.Transaction.user_id == current_user_id).all()
    print(f"--- DEBUG: Found {len(raw_transactions)} raw rows in DB for user_id {current_user_id} ---")
    decrypted_history = []
    # Sequential Decryption loop
    for item in raw_transactions:
        try:
            #Decrypt title string
            plaintext_title = decrypt_data(item.encrypted_title)

            # Decrypt and unpack the metadata JSON strng back into a dictionary
            plaintext_meta_string = decrypt_data(item.data_string)
            financial_meta = json.loads(plaintext_meta_string)
            # Reconstructs the expetted response schema object
            decrypted_history.append(TransactionResponse(id=item.id, title = plaintext_title, amount = financial_meta["amount"],category=financial_meta["category"],user_id=item.user_id))
        except Exception:
            # Skip corrupted individual rows without crashing the whole feed
            continue

    return decrypted_history