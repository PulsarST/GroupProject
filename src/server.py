from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from database.service import (
    get_db, get_zones, get_spots, create_session_db, close_session_db, create_payment_db, get_sessions, get_payments
)
from pydantic import BaseModel
from typing import Optional


class SessionCreate(BaseModel):
    zone_id: str
    spot_id: int
    plate: str
    tariff_id: Optional[int] = None


app = FastAPI(title="Умная парковка")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/zones")
async def api_get_zones(db=Depends(get_db)):
    return await get_zones(db)

@app.get("/spots")
async def api_get_spots(zone_id: str, db=Depends(get_db)):
    return await get_spots(db, zone_id)

@app.get("/sessions")
async def api_get_sessions(db=Depends(get_db)):
    return await get_sessions(db)

@app.post("/sessions")
async def api_create_session(session_data: SessionCreate, db=Depends(get_db)):
    return await create_session_db(db, **session_data.dict())

@app.put("/sessions/{session_id}/close")
async def api_close_session(session_id: int, db=Depends(get_db)):
    return await close_session_db(db, session_id)

@app.post("/sessions/{session_id}/pay")
async def api_create_payment(session_id: int, db=Depends(get_db)):
    return await create_payment_db(db, session_id)

@app.get("/payments")
async def api_get_payments(db=Depends(get_db)):
    return await get_payments(db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000)
