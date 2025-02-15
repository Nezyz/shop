from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    coins: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Inventory(BaseModel):
    item_name: str
    quantity: int

    class Config:
        orm_mode = True

class Transaction(BaseModel):
    amount: int
    from_user: str
    to_user: str

    class Config:
        orm_mode = True

class InfoResponse(BaseModel):
    coins: int
    inventory: List[Inventory]
    coinHistory: dict

class SendCoinRequest(BaseModel):
    toUser: str
    amount: int