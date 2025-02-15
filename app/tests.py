from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import pytest
import dependencies

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[dependencies.get_db] = override_get_db
    yield TestClient(app)

def test_send_coins(client, db):
    # Создайте тестовых пользователей и токен
    response = client.post(
        "/api/sendCoin",
        json={"toUser": "testuser", "amount": 100},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "success"}