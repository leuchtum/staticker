from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from . import core
from .collections import PlayerCollection, EventCollection

active_event = None
active_game = core.Game[1]

templates = Jinja2Templates(directory="staticker/templates")


async def not_found(_, exc):
    with open("staticker/templates/404.html") as f:
        content = f.read()
        return HTMLResponse(content, status_code=exc.status_code)
exceptions = {
    404: not_found
}

app = FastAPI(exception_handlers=exceptions)
app.mount("/static", StaticFiles(directory="staticker/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def app_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "active_event": active_event, "active_game": active_game})


@app.get("/about", response_class=HTMLResponse)
async def app_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/event/{event_id}", response_class=HTMLResponse)
async def app_event(request: Request, event_id: str):
    try:
        ev = core.get_event_by_id(event_id)
    except:
        raise HTTPException(status_code=404, detail="Event not found")
    return templates.TemplateResponse("event.html", {"request": request, "event": ev})


@app.get("/game/{game_id}", response_class=HTMLResponse)
async def app_game(request: Request, game_id: str):
    try:
        g = core.get_game_by_id(game_id)
    except:
        raise HTTPException(status_code=404, detail="Game not found")
    return templates.TemplateResponse("game.html", {"request": request, "game": g})


@app.get("/player/{player_id}", response_class=HTMLResponse)
async def app_player(request: Request, player_id: str, alert: bool = False):
    try:
        p = core.get_player_by_id(player_id)
    except:
        raise HTTPException(status_code=404, detail="Player not found")
    return templates.TemplateResponse("player.html", {"request": request, "player": p, "alert": alert})


@app.get("/events-overview", response_class=HTMLResponse)
async def app_events_overview(request: Request):
    ec = EventCollection()
    ec.load_all()
    events = ec.get_events()
    return templates.TemplateResponse("events-overview.html", {"request": request, "events": events})


@app.get("/player-overview", response_class=HTMLResponse)
async def app_player_overview(request: Request):
    pc = PlayerCollection()
    pc.load_all(sort_by="name")
    p = pc.get_player()
    return templates.TemplateResponse("player-overview.html", {"request": request, "players": p})


@app.get("/statistics-overview", response_class=HTMLResponse)
async def app_statistics_overview(request: Request):
    return templates.TemplateResponse("statistics.html", {"request": request})


@app.get("/new-player", response_class=HTMLResponse)
async def app_new_player(request: Request, alert: bool = False):
    return templates.TemplateResponse("new_player.html", {"request": request, "alert": alert})


@app.post("/new-player/submit")
async def app_new_player_submit(_: Request, name: str = Form(...)):
    p = core.Player(name=name)
    try:
        p.save()
    except:
        return RedirectResponse(url='/new-player?alert=1', status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url=f"/player/{p.id}?alert=1", status_code=status.HTTP_302_FOUND)
