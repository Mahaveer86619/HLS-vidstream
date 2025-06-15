from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.base import Base
from routes import auth
from db.db import engine
import logging

from routes import auth

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:7500",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

Base.metadata.create_all(engine)

logger.info("🚀 FastAPI application startup complete!")
