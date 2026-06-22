import os
from cryptography.fernet import Fernet
# Fallback development key 
FIELD_ENCRYPTION_KEY = os.getenv("FIELD_ENCRYPTION_KEY", "7432O_D8NKZOLYvLRvKt51uJyOxb4vJPoOEBg3YUEpI=")

# Initialise the AES-256 cryptographic engine
cipher_suite = Fernet(FIELD_ENCRYPTION_KEY.encode())

def encrypt_data(plaintext: str) -> str:
    """
    Transforms raw senstitive data text into AES-256 encrypted ciphertext string.
    """
    if not plaintext:
        return plaintext
    # Convert string to bytes, encrypt and decode bytes back to storable string.
    return cipher_suite.encrypt(plaintext.encode()).decode()

def decrypt_data(ciphertext: str) -> str:
    """
    Decrypt AES-256 ciphertext back into human-readable plaintext string.
    """
    if not ciphertext:
        return ciphertext
    
    try:
        return cipher_suite.decrypt(ciphertext.encode()).decode()
    except Exception:
        # Cryptographic fail safe: Prevent unhandled server crashes if data is corrupted or tampered with.
        return "[DECRYPTION_ERROR: Integrity Verification Failed]"