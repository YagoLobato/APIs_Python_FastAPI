from core.config import settings
from core.database import engine
import models.all_models 

async def criar_tabelas():
    print("criando tabelas...")
    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBaseModel.metadata.drop_all)
        await conn.run_sync(settings.DBBaseModel.metadata.create_all)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(criar_tabelas())