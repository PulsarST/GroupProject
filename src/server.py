from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from database.service import (
    get_active_sessions,
    get_db,
    get_zones,
    get_spots,
    create_session_db,
    close_session_db,
    create_payment_db,
    get_sessions,
    get_payments,
    get_endtime_sessions,
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


@app.get("/test_endtimes")
async def api_get_endtime_sessions(db=Depends(get_db)):
    return await get_endtime_sessions(db)


@app.get("/active-session")
async def api_get_active_sessions(db=Depends(get_db)):
    return await get_active_sessions(db)



# Схемы для API
class SessionOut(BaseModel):
    id: str
    spot_id: str
    status: str
    start: str
    end: str | None = None

class PaymentOut(BaseModel):
    id: str
    session_id: str
    amount: int
    ts: str

@app.get("/admin_sessions")
async def admin_get_sessions(offset: int = 0, limit: int = 10, db=Depends(get_db)):
    sessions = await get_sessions(db)
    result = []

    for s in sessions[offset:offset+limit]:
        start_ts = getattr(s, "start", None)
        end_ts = getattr(s, "end", None)

        result.append({
            "id": s.id,
            "spot_id": getattr(s, "spot_id", None),
            "status": getattr(s, "status", None),
            "start": start_ts.isoformat() if start_ts else "-",
            "end": end_ts.isoformat() if end_ts else "-",
        })

    return result


@app.get("/admin_payments")
async def admin_get_payments(offset: int = 0, limit: int = 10, db=Depends(get_db)):
    payments = await get_payments(db)
    result = []

    for p in payments[offset:offset+limit]:
        result.append({
            "id": p.id,
            "session_id": getattr(p, "session_id", None),
            "amount": getattr(p, "amount", None),
            "ts": getattr(p, "ts", None).isoformat() if getattr(p, "ts", None) else None,
        })

    return result

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000)
