from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas, crud
from .database import engine, get_db
from .redis import get_redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from . import models
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from . import models
import asyncio

# Создаем асинхронный движок
engine = create_async_engine("postgresql+asyncpg://user:password@db:5432/avito_shop", echo=True)

# Создаем асинхронную сессию
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    # Запускаем создание таблиц при старте приложения
    asyncio.create_task(create_tables())

app = FastAPI()

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(crud.get_current_user)):
    return current_user

@app.get("/api/info", response_model=schemas.InfoResponse)
async def get_info(current_user: models.User = Depends(crud.get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.get_user_info(db, current_user)

@app.post("/api/sendCoin")
async def send_coin(send_coin_request: schemas.SendCoinRequest, current_user: models.User = Depends(crud.get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.send_coin(db, current_user, send_coin_request.toUser, send_coin_request.amount)

@app.get("/api/buy/{item}")
async def buy_item(item: str, current_user: models.User = Depends(crud.get_current_user), db: AsyncSession = Depends(get_db)):
    return await crud.buy_item(db, current_user, item)