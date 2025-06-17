from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class SecretKeys(BaseSettings):
    REGION_NAME: str = os.getenv("REGION_NAME", "ap-south-1")
    SQS_QUEUE_URL: str = os.getenv("SQS_QUEUE_URL", "")