import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "DGtech")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "24832612umaprogressaoultimoxpenultimo>>proximo")

settings = Settings()