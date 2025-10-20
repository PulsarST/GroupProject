import asyncio
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, except_
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import (
        create_async_engine,
        AsyncSession,
        async_sessionmaker)

from database.database import Base

app = FastAPI(title="Умная парковка")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_async_engine("sqlite:///.../data/database.db")
SessionDB = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Tables are created all")


async def get_db():
    async with SessionDB() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

asyncio.run(create_tables())
    
@app.get("/")
def root() -> Dict[str, int]:
    return {"status": 200}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app)
