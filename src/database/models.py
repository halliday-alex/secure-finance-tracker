#core building blocks used to define database column data types
from sqlalchemy import Column, Integer, String, Float, ForeignKey
# Allows easily link to tables
from sqlalchemy.orm import relationship
# blueprint class created in connection.py
from src.database.connection import Base

class User(Base):
    """
    The Users Table: Stores account authentication records.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # Security: Never store plaintext passwords. Hold salted bycrypt hash string.
    hashed_password = Column(String,nullable=False)
    #Relationships. If user deleted, "cascade automaticaly wipes their data for privacy"
    transactions = relationship("Transaction",back_populates="owner", cascade="all,delete-orphan")
    budgets = relationship("Budget",back_populates="owner",cascade="all,delete-orphan")

class Transactions(Base):
    """
    The Transaction Table: Supports main dashboard list and expenses charts.
    """
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    #Security: To prevent exposing fina cial figures in database breach, string fields will hold encrypted AES-256 data payloads.
    encrypted_title = Column(String, nullable=False) #used for mapping frotend charts
    data_string = Column(String, nullable = False) # stores transaction data
    #cyber security : foreign key forces every single transaction to point explicitly to a valid User ID
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    owner = relationship("User",back_populates="transactions")

class Budget(Base):
    """
    The Budget Table: Supports the 'My Plan' progress trackers and saving goals.
    """
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    category_or_goal = Column(String,nullable=False) # "Holiday Fund" etc
    target_amount = Column(Float, nullable=False) #The total budget limt or savings target
    current_progress = Column(Float,default=0.0) #How much they have saved/spent

    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    owner = relationship("User",back_populates="budgets")
