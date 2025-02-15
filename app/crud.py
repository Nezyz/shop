from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .database import get_db
from .redis import get_redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
redis_client = get_redis()

async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли токен в Redis
    cached_user = redis_client.get(f"token:{token}")
    if cached_user:
        return schemas.User.parse_raw(cached_user)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    # Кэшируем пользователя в Redis
    redis_client.set(f"token:{token}", user.json(), ex=30 * 60)  # 30 минут

    return user

async def get_user_info(db: AsyncSession, user: models.User):
    result = await db.execute(select(models.Inventory).filter(models.Inventory.owner_id == user.id))
    inventory = [{"item_name": item.item_name, "quantity": item.quantity} for item in result.scalars()]
    coin_history = {
        "received": [{"fromUser": t.from_user.username, "amount": t.amount} for t in user.received_transactions],
        "sent": [{"toUser": t.to_user.username, "amount": t.amount} for t in user.sent_transactions]
    }
    return schemas.InfoResponse(coins=user.coins, inventory=inventory, coinHistory=coin_history)

async def send_coin(db: AsyncSession, from_user: models.User, to_user: str, amount: int):
    if from_user.coins < amount:
        raise HTTPException(status_code=400, detail="Not enough coins")
    to_user_db = await get_user(db, to_user)
    if not to_user_db:
        raise HTTPException(status_code=404, detail="User not found")
    from_user.coins -= amount
    to_user_db.coins += amount
    transaction = models.Transaction(amount=amount, from_user_id=from_user.id, to_user_id=to_user_db.id)
    db.add(transaction)
    await db.commit()
    await db.refresh(from_user)
    await db.refresh(to_user_db)
    return {"message": "Coins sent successfully"}

async def buy_item(db: AsyncSession, user: models.User, item: str):
    item_prices = {
        "t-shirt": 80,
        "cup": 20,
        "book": 50,
        "pen": 10,
        "powerbank": 200,
        "hoody": 300,
        "umbrella": 200,
        "socks": 10,
        "wallet": 50,
        "pink-hoody": 500
    }
    if item not in item_prices:
        raise HTTPException(status_code=404, detail="Item not found")
    price = item_prices[item]
    if user.coins < price:
        raise HTTPException(status_code=400, detail="Not enough coins")
    user.coins -= price
    result = await db.execute(select(models.Inventory).filter(models.Inventory.owner_id == user.id, models.Inventory.item_name == item))
    inventory_item = result.scalars().first()
    if inventory_item:
        inventory_item.quantity += 1
    else:
        inventory_item = models.Inventory(item_name=item, owner_id=user.id)
        db.add(inventory_item)
    await db.commit()
    await db.refresh(user)
    return {"message": "Item bought successfully"}