from database.service import *
from sqlalchemy import Sequence

import asyncio
import pytest

pytest_plugins = ('pytest_asyncio',)

current_dir = os.path.dirname(os.path.abspath(__file__))
db_relative_path = os.path.join(current_dir, "test_database.db")
db_absolute_path = os.path.abspath(db_relative_path)

TEST_DB_PATH = f"sqlite+aiosqlite:///{db_absolute_path}"

engine = create_async_engine(TEST_DB_PATH, echo=True)
SessionTestDB = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionTestDB() as session:
        yield session

def compare_sequence(a: Sequence, 
            b: dict[str, list]) -> bool:
    
    result = True
    for key, item in b.items():
        for i in range(len(a)):
            result = result and eval("a[i]."+key) == item[i]

    return result

def compare(a, b: dict) -> bool:
    
    result = True
    for key, item in b.items():
        result = result and eval("a."+key) == item
    
    return result