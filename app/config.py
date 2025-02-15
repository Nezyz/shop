import os

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/avito_shop")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()