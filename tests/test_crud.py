import pytest
from app import crud, schemas
from app.database import AsyncSessionLocal, Base, engine
from sqlalchemy.ext.asyncio import AsyncSession

# Фикстура для создания базы данных и таблиц
@pytest.fixture(scope="module")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        yield session  # Возвращаем сессию
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Тест для создания пользователя
@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    user = schemas.UserCreate(username="testuser", password="testpass")
    db_user = await crud.create_user(db, user)
    assert db_user.username == "testuser"
    assert db_user.coins == 1000

# Тест для получения пользователя
@pytest.mark.asyncio
async def test_get_user(db: AsyncSession):
    user = schemas.UserCreate(username="testuser", password="testpass")
    await crud.create_user(db, user)
    db_user = await crud.get_user(db, username="testuser")
    assert db_user is not None
    assert db_user.username == "testuser"

# Тест для аутентификации пользователя
@pytest.mark.asyncio
async def test_authenticate_user(db: AsyncSession):
    user = schemas.UserCreate(username="testuser", password="testpass")
    await crud.create_user(db, user)
    authenticated_user = await crud.authenticate_user(db, username="testuser", password="testpass")
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"

# Тест для передачи монет
@pytest.mark.asyncio
async def test_send_coin(db: AsyncSession):
    user1 = schemas.UserCreate(username="user1", password="pass1")
    user2 = schemas.UserCreate(username="user2", password="pass2")
    await crud.create_user(db, user1)
    await crud.create_user(db, user2)
    result = await crud.send_coin(db, from_user=await crud.get_user(db, username="user1"), to_user="user2", amount=100)
    assert result == {"message": "Coins sent successfully"}

# Тест для покупки товара
@pytest.mark.asyncio
async def test_buy_item(db: AsyncSession):
    user = schemas.UserCreate(username="testuser", password="testpass")
    await crud.create_user(db, user)
    result = await crud.buy_item(db, user=await crud.get_user(db, username="testuser"), item="t-shirt")
    assert result == {"message": "Item bought successfully"}