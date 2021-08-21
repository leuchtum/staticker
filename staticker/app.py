from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
import json

from . import core
from .collections import PlayerCollection, EventCollection
from .communication import arduino
from .log import logger
from .manager import manager


async def not_found(_, exc):
    with open("staticker/templates/404.html") as f:
        content = f.read()
        return HTMLResponse(content, status_code=exc.status_code)

exceptions = {404: not_found}
app = FastAPI(exception_handlers=exceptions)
app.mount("/static", StaticFiles(directory="staticker/static"), name="static")
templates = Jinja2Templates(directory="staticker/templates")


@app.on_event("startup")
async def startup_event():
    arduino.set_button_callback(app_active_game_action)
    await arduino.startup()


@app.get("/debug")
async def debug():
    ev = manager.get_active_event()
    if ev:
        ev.deactivate()


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


@app.get("/event", response_class=HTMLResponse)
async def app_events_overview(request: Request):
    ec = EventCollection()
    ec.load_all()
    dic = {
        "request": request,
        "events": ec.get_events(),
        "active_event": manager.get_active_event()
    }
    return templates.TemplateResponse("events-overview.html", dic)


@app.get("/event/{event_id}", response_class=HTMLResponse)
async def app_event(request: Request, event_id: str, created: bool = False):
    try:
        ev = core.get_event_by_id(event_id)
    except:
        raise HTTPException(status_code=404, detail="Event not found")
    dic = {
        "request": request,
        "event": ev,
        "created": created
    }
    return templates.TemplateResponse("event.html", dic)


@app.get("/new-event", response_class=HTMLResponse)
async def app_new_event(request: Request, min_player_violation: bool = False, err: bool = False):
    # Check if an event is active
    active_event = manager.get_active_event()
    active_event_id = active_event.id if active_event else None

    # Render HTMLResponse
    dic = {
        "request": request,
        "active_event_id": active_event_id,
        "min_player_violation": min_player_violation,
        "err": err
    }
    return templates.TemplateResponse("new_event.html", dic)


@app.post("/new-event/submit")
async def app_new_event_submit(selected_players: str = Form(...)):
    selected_players = json.loads(selected_players)

    if len(selected_players) < 2:
        url = '/new-event?min_player_violation=true'
    else:
        ev = core.Event(mode="TEST")
        try:
            ev.activate()
            player = [core.get_player_by_name(name)
                      for name in selected_players]
            ev.add_player(player)
            ev.save()
        except core.NotAllowedError:
            url = '/new-event?err=true'
        else:
            url = f"/event/{ev.id}?created=1"

    return RedirectResponse(url, status_code=status.HTTP_302_FOUND)


##############################################################


@app.get("/player", response_class=HTMLResponse)
async def app_player_overview(request: Request):
    pc = PlayerCollection()
    pc.load_all(sort_by="name")
    p = pc.get_player()
    dic = {"request": request, "players": p}
    return templates.TemplateResponse("player-overview.html", dic)


@app.get("/player/{player_id}", response_class=HTMLResponse)
async def app_player(request: Request, player_id: str, created: bool = False):
    try:
        p = core.get_player_by_id(player_id)
    except:
        raise HTTPException(status_code=404, detail="Player not found")
    dic = {"request": request,
           "player": p,
           "created": created}
    return templates.TemplateResponse("player.html", dic)


@app.get("/new-player", response_class=HTMLResponse)
async def app_new_player(request: Request, exists: bool = False):
    dic = {"request": request, "exists": exists}
    return templates.TemplateResponse("new_player.html", dic)


@app.post("/new-player/submit")
async def app_new_player_submit(_: Request, name: str = Form(...)):
    p = core.Player(name=name)
    code = status.HTTP_302_FOUND
    try:
        p.save()
    except:
        return RedirectResponse(url='/new-player?exists=1', status_code=code)
    return RedirectResponse(url=f"/player/{p.id}?created=1", status_code=code)


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


@app.get("/active-game", response_class=HTMLResponse)
async def app_active_game(request: Request):
    dic = {"request": request}
    return templates.TemplateResponse("about.html", dic)


@app.post("/active-game/{action}")
async def app_active_game_action(action: str):
    try:
        allowed = ["gbd", "gbo", "gwd", "gwo",
                   "obd", "obo", "owd", "owo", "undo"]
        assert action in allowed
    except AssertionError:
        raise HTTPException(status_code=400, detail="Invalid command")

    if manager.active_game:
        if action == "undo":
            pass
        else:
            manager.active_game.goal_and_owner_by_key(action)
            position = action[1:]
            player_history = manager.active_game.get_player_history(position)
            await arduino.set_leds(position, player_history)


##############################################################


@app.get("/data/{obj}")
async def app_data(request: Request, obj: str, load_all: str = False):
    if obj == "player":
        if load_all:
            pc = PlayerCollection()
            pc.load_all(sort_by="name")
            return pc.get_names_with_ids()
        else:
            raise(NotImplementedError)
    else:
        raise(NotImplementedError)
