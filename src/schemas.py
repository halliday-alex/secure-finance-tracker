from pydantic import BaseModel, EmailStr, Field

# Format of user registration body looks like.
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(...,min_length=8,max_length=72)


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

# Format login body expects and what token response payload looks like.
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(...,min_length=8,max_length=72)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    title: str = Field(...,max_length=100) #Plaintext incoming
    amount: float = Field(...,gt=0)
    category: str = Field(...,max_length=50) # Plaintext incoming

class TransactionResponse(BaseModel):
    id: int
    title: str # Decrypted seamlessly for the authorised user
    amount: float # Reconstructed seamlessly
    category: str # Decrypted seamlessly
    user_id: int

    class Config:
        from_attributes = True