from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class SecretKeys(BaseSettings):
    REGION_NAME: str = os.getenv("REGION_NAME", "ap-south-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    S3_BUCKET: str = ""
    S3_KEY: str = ""
    S3_PROCESSED_VIDEOS_BUCKET: str = os.getenv("S3_PROCESSED_VIDEOS_BUCKET", "")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "")