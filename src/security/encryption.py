import os
from datetime import datetime, timedelta, timezone 
import jwt
from passlib.context import CryptContext
# Tell passlib to explicitly use bcrypt and automatically handle salting
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
#In production, always load this via os.getenv("SECRET_KEY") from environment.
SECRET_KEY = os.getenv("SECRET_KEY","SUPER_SECRET_DEVELOPMENT_KEY_DO_NOT_USE_IN_PRODUCTION_1432!")
ALGORITHM = "HS256" # HS256 very secure
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password:str) -> str:
    """
    Takes a plaintext password, generates secure random salt, mixes with password and runs through bcrypt
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Extracts salt from stored hash, hashes  incoming plain password with the salt and checks if they match in constant time to prevent timimg side channel attacks.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Generates a short lives, signed JSON Web Token (JWT) for authentication state.
    """
    to_encode = data.copy()
    # Calculate token expiration window
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt