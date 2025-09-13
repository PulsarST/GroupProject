from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core import transforms

app = FastAPI(title="Умная парковка")


templates = Jinja2Templates(directory="templates")


state = {}


MENU = [
    "Overview",
    "Data",
    "Functional Core",
    "Pipelines",
    "Async/FRP",
    "Reports",
    "Tests",
    "About",
]


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "menu": MENU, "choice": "Overview", "state": state},
    )


@app.get("/{page}", response_class=HTMLResponse)
async def page(request: Request, page: str):
    choice = page if page in MENU else "Overview"
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "menu": MENU, "choice": choice, "state": state},
    )


@app.post("/load-seed")
async def load_seed():
    zones, spots, tariffs, vehicles, events, rules, sessions, payments, violations = (
        transforms.load_seed("./src/data/seed.json")
    )
    state.update(
        {
            "zones": zones,
            "spots": spots,
            "tariffs": tariffs,
            "vehicles": vehicles,
            "events": events,
            "rules": rules,
            "sessions": sessions,
            "payments": payments,
            "violations": violations,
        }
    )
    return {"status": "ok", "zones": len(zones), "spots": len(spots)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
