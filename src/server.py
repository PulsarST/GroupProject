from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import transforms
from dataclasses import asdict
from typing import Dict, Tuple

app = FastAPI(title="Умная парковка")

# Allow requests from Flet frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

state: Dict[str, Tuple] = {}


@app.post("/load_seed")
async def load_seed():
    zones, spots, tariffs, vehicles, events, rules, sessions, payments, violations = (
        transforms.load_seed("./src/data/seed.json")
    )

    state["zones"] = zones
    state["spots"] = spots
    state["tariffs"] = tariffs
    state["vehicles"] = vehicles
    state["events"] = events
    state["rules"] = rules
    state["sessions"] = sessions
    state["payments"] = payments
    state["violations"] = violations

    # Return counts for frontend
    return {
        "status": "ok",
        "zones": len(zones),
        "spots": len(spots),
        "tariffs": len(tariffs),
        "vehicles": len(vehicles),
    }


@app.get("/data")
async def get_data():
    """Return serialized state for frontend"""

    def serialize_tuple(t):
        return [asdict(x) for x in t]

    return {
        "zones": serialize_tuple(state["zones"]),
        "spots": serialize_tuple(state["spots"]),
        "tariffs": serialize_tuple(state["tariffs"]),
        "vehicles": serialize_tuple(state["vehicles"]),
        "events": serialize_tuple(state["events"]),
        "rules": serialize_tuple(state["rules"]),
        "sessions": serialize_tuple(state["sessions"]),
        "payments": serialize_tuple(state["payments"]),
        "violations": serialize_tuple(state["violations"]),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app)
