from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    coins = Column(Integer, default=1000)

    inventory = relationship("Inventory", back_populates="owner")
    sent_transactions = relationship("Transaction", foreign_keys="Transaction.from_user_id", back_populates="from_user")
    received_transactions = relationship("Transaction", foreign_keys="Transaction.to_user_id", back_populates="to_user")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    quantity = Column(Integer, default=1)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="inventory")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))

    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_transactions")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_transactions")