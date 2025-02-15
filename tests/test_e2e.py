# tests/test_e2e.py
import pytest
import httpx
from app import schemas

# Базовый URL API
BASE_URL = "http://localhost:8000"

# Тест для регистрации и авторизации
@pytest.mark.asyncio
async def test_register_and_login():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Регистрация
        response = await client.post("/register", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

        # Авторизация
        response = await client.post("/token", data={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        assert "access_token" in response.json()

# Тест для передачи монет
@pytest.mark.asyncio
async def test_send_coin():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Регистрация пользователя 1
        response = await client.post("/register", json={"username": "user1", "password": "pass1"})
        assert response.status_code == 200

        # Регистрация пользователя 2
        response = await client.post("/register", json={"username": "user2", "password": "pass2"})
        assert response.status_code == 200

        # Авторизация пользователя 1
        response = await client.post("/token", data={"username": "user1", "password": "pass1"})
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Передача монет от user1 к user2
        response = await client.post(
            "/api/sendCoin",
            json={"toUser": "user2", "amount": 100},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Coins sent successfully"}

# Тест для покупки товара
@pytest.mark.asyncio
async def test_buy_item():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Регистрация
        response = await client.post("/register", json={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200

        # Авторизация
        response = await client.post("/token", data={"username": "testuser", "password": "testpass"})
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Покупка товара
        response = await client.get(
            "/api/buy/t-shirt",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Item bought successfully"}