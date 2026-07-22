import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Attendance System")
    ENV: str = os.getenv("ENV", "development")

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://localhost:9000")

    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    # -------------------------
    # VALIDATION
    # -------------------------
    def validate(self):
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set")

        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET is not set")

        if len(self.JWT_SECRET) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")

        if self.ENV not in ["development", "production"]:
            raise ValueError("ENV must be either 'development' or 'production'")


settings = Settings()
settings.validate()