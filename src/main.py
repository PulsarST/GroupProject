from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.templating import _TemplateResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")


@app.get("/{name}")
async def index(request: Request, name: str) -> _TemplateResponse:
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Home", "name": name}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
