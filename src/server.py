import asyncio
from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.service import create_tables

app = FastAPI(title="Умная парковка")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

asyncio.run(create_tables())

@app.get("/spots")
def get_spots():
    pass

    
@app.get("/")
def root() -> Dict[str, int]:
    return {"status": 200}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app)
