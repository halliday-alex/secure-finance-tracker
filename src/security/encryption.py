from passlib.context import CryptContext
#Tell passlib to explicitly use bcrypt and automatically handle salting
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

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