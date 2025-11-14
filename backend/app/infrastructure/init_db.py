from app.models.dbModels.Entity import EntityDB
from app.infrastructure.db.session import async_engine
import app.models

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(EntityDB.metadata.create_all)

