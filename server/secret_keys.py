from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache
import os

load_dotenv()


class SecretKeys(BaseSettings):
    COGNITO_CLIENT_ID: str = os.getenv("COGNITO_CLIENT_ID", "")
    COGNITO_CLIENT_SECRET: str = os.getenv("COGNITO_CLIENT_SECRET", "")
    REGION_NAME: str = os.getenv("REGION_NAME", "ap-south-1")
    POSTGRES_DB_URL: str = os.getenv("POSTGRES_DB_URL", "")
    AWS_RAW_VIDEOS_BUCKET: str = os.getenv("AWS_RAW_VIDEOS_BUCKET", "")
    AWS_VIDEO_THUMBNAIL_BUCKET: str = os.getenv("AWS_VIDEO_THUMBNAIL_BUCKET", "")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields


@lru_cache()
def get_secret_keys() -> SecretKeys:
    return SecretKeys()


# Create a singleton instance
secret_keys = get_secret_keys()
