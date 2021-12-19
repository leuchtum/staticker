from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .collections import PlayerCollection
from .communication import arduino
from .log import logger
from .dependencies import manager, templates

from .routes.event import router as event_router
from .routes.game import router as game_router, active_game_action
from .routes.player import router as player_router

from .core import get_game_by_id


app = FastAPI()
app.mount("/static", StaticFiles(directory="staticker/static"), name="static")
app.include_router(event_router)
app.include_router(game_router)
app.include_router(player_router)


@app.on_event("startup")
async def startup_event():
    arduino.set_button_callback(active_game_action)
    await arduino.startup()


@app.get("/debug")
async def debug():
    ev = manager.get_active_event()
    if ev:
        ev.deactivate()


@app.get("/", response_class=HTMLResponse)
async def app_root(request: Request):
    dic = {
        "request": request,
        "active_event": manager.get_active_event(),
        "active_game": manager.get_active_game(),
    }
    return templates.TemplateResponse("home.html", dic)


@app.get("/about", response_class=HTMLResponse)
async def app_about(request: Request):
    dic = {"request": request}
    return templates.TemplateResponse("about.html", dic)


##############################################################


@app.get("/data/{obj}")
async def app_data(
    request: Request, obj: str, load_all: str = False, game_id: int = None
):
    if obj == "player":
        if load_all:
            pc = PlayerCollection()
            pc.load_all(sort_by="name")
            return pc.get_names_with_ids()
        else:
            raise (NotImplementedError)
    elif obj == "active_game_exists":
        active_game = manager.get_active_game()
        if active_game:
            return active_game.id
        else:
            return False
    elif obj == "game_score":
        game = get_game_by_id(game_id)
        if game.id == game_id:
            return game.get_score()
        else:
            return False
    else:
        raise (NotImplementedError)
