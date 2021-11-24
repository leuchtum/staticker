from fastapi import Request, HTTPException, APIRouter
from fastapi.params import Form
from fastapi.responses import HTMLResponse, RedirectResponse
import starlette.status as status

from ..communication import arduino
from ..dependencies import manager, templates
from ..core import (
    Game,
    NotAllowedError,
    get_game_by_id,
    NotFoundError,
    get_player_by_name,
)


router = APIRouter(prefix="/game", tags=["game"])


@router.get("/id/{game_id}", response_class=HTMLResponse)
async def game(request: Request, game_id: str):
    try:
        g = get_game_by_id(game_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Game not found")
    dic = {"request": request, "game": g}
    return templates.TemplateResponse("game.html", dic)


@router.get("/active", response_class=HTMLResponse)
async def active_game():
    active_game = manager.get_active_game()
    if active_game:
        url = f"id/{active_game.id}"
        return RedirectResponse(url, status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(status_code=404, detail="No active game")


@router.post("/active/{action}")
async def active_game_action(action: str):
    try:
        allowed = ["gbd", "gbo", "gwd", "gwo", "obd", "obo", "owd", "owo"]
        allowed += [f"{i}_undo" for i in allowed]
        assert action in allowed
    except AssertionError:
        raise HTTPException(status_code=400, detail="Invalid command")

    active_game = manager.get_active_game()

    if active_game:
        if action == "undo":
            raise (NotImplementedError)
        else:
            active_game.goal_and_owner_by_key(action)
            # position = action[1:]
            # player_history = active_game.get_player_history(position)
            # await arduino.set_leds(position, player_history)
    else:
        raise HTTPException(status_code=404, detail="No active game")


@router.post("/new/submit")
async def new_game_submit(
    pwd: str = Form(...),
    pwo: str = Form(...),
    pbd: str = Form(...),
    pbo: str = Form(...),
    from_event: int = Form(...),
):
    try:
        pwd = get_player_by_name(pwd)
        pwo = get_player_by_name(pwo)
        pbd = get_player_by_name(pbd)
        pbo = get_player_by_name(pbo)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Player not found")

    ev = manager.get_active_event()
    active_game = manager.get_active_game()

    if active_game:
        raise HTTPException(status_code=403, detail="There is an active game")

    if not ev:
        raise HTTPException(status_code=404, detail="No active event")

    game = Game(event_id=from_event)

    try:
        pw = [pwd] if pwd == pwo else [pwd, pwo]
        pb = [pbd] if pbd == pbo else [pbd, pbo]
        game.add_player(pw, pb)
    except NotAllowedError:
        raise HTTPException(status_code=403, detail="Player only on one side allowed")

    ev.add_game(game)

    return RedirectResponse("/game/active", status_code=status.HTTP_302_FOUND)
