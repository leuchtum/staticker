from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from . import core
from .collections import PlayerCollection, EventCollection
from .manager import manager


##############################################################


active_event = None
active_game = None


##############################################################


async def not_found(_, exc):
    with open("staticker/templates/404.html") as f:
        content = f.read()
        return HTMLResponse(content, status_code=exc.status_code)
    
exceptions = {404: not_found}
app = FastAPI(exception_handlers=exceptions)
app.mount("/static", StaticFiles(directory="staticker/static"), name="static")
templates = Jinja2Templates(directory="staticker/templates")


##############################################################


@app.get("/", response_class=HTMLResponse)
async def app_root(request: Request):
    dic = {
        "request": request,
        "active_event": manager.get_active_event(),
        "active_game": manager.get_active_game()
    }
    return templates.TemplateResponse("home.html", dic)


@app.get("/about", response_class=HTMLResponse)
async def app_about(request: Request):
    dic = {"request": request}
    return templates.TemplateResponse("about.html", dic)


##############################################################


@app.get("/events-overview", response_class=HTMLResponse)
async def app_events_overview(request: Request):
    ec = EventCollection()
    ec.load_all()
    dic = {
        "request": request,
        "events": ec.get_events(),
        "active_event":manager.get_active_event()
    }
    return templates.TemplateResponse("events-overview.html", dic)


@app.get("/event/{event_id}", response_class=HTMLResponse)
async def app_event(request: Request, event_id: str):
    try:
        ev = core.get_event_by_id(event_id)
    except:
        raise HTTPException(status_code=404, detail="Event not found")
    dic = {"request": request, "event": ev}
    return templates.TemplateResponse("event.html", dic)


##############################################################


@app.get("/player-overview", response_class=HTMLResponse)
async def app_player_overview(request: Request):
    pc = PlayerCollection()
    pc.load_all(sort_by="name")
    p = pc.get_player()
    dic = {"request": request, "players": p}
    return templates.TemplateResponse("player-overview.html", dic)


@app.get("/player/{player_id}", response_class=HTMLResponse)
async def app_player(request: Request, player_id: str, alert: bool = False):
    try:
        p = core.get_player_by_id(player_id)
    except:
        raise HTTPException(status_code=404, detail="Player not found")
    dic = {"request": request, "player": p, "alert": alert}
    return templates.TemplateResponse("player.html", dic)


##############################################################


@app.get("/new-player", response_class=HTMLResponse)
async def app_new_player(request: Request, alert: bool = False):
    dic = {"request": request, "alert": alert}
    return templates.TemplateResponse("new_player.html", dic)


@app.post("/new-player/submit")
async def app_new_player_submit(_: Request, name: str = Form(...)):
    p = core.Player(name=name)
    code = status.HTTP_302_FOUND
    try:
        p.save()
    except:
        return RedirectResponse(url='/new-player?alert=1', status_code=code)
    return RedirectResponse(url=f"/player/{p.id}?alert=1", status_code=code)


##############################################################


@app.get("/statistics-overview", response_class=HTMLResponse)
async def app_statistics_overview(request: Request):
    dic = {"request": request}
    return templates.TemplateResponse("statistics.html", dic)


##############################################################


@app.get("/game/{game_id}", response_class=HTMLResponse)
async def app_game(request: Request, game_id: str):
    try:
        g = core.get_game_by_id(game_id)
    except:
        raise HTTPException(status_code=404, detail="Game not found")
    dic = {"request": request, "game": g}
    return templates.TemplateResponse("game.html", dic)
