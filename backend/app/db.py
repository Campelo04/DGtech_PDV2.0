from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def init_db() -> None:
    global _client, _db
    _client = AsyncIOMotorClient(settings.MONGO_URI)
    _db = _client[settings.DB_NAME]
    # índices mínimos p/ usuários
    await _db.Users.create_index("username", unique=True)

def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("DB não inicializado. Chame init_db() no startup.")
    return _db