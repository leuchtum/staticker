from fastapi import Request, HTTPException, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
import starlette.status as status

from ..communication import arduino
from ..dependencies import manager, templates
from ..core import get_game_by_id, NotFoundError


router = APIRouter(
    prefix="/game",
    tags=["game"]
)


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
        allowed = ["gbd", "gbo", "gwd", "gwo",
                   "obd", "obo", "owd", "owo", "undo"]
        assert action in allowed
    except AssertionError:
        raise HTTPException(status_code=400, detail="Invalid command")

    active_game = manager.get_active_game()
    
    if active_game:
        if action == "undo":
            raise(NotImplementedError)
        else:
            active_game.goal_and_owner_by_key(action)
            position = action[1:]
            player_history = manager.active_game.get_player_history(position)
            await arduino.set_leds(position, player_history)
    else:
        raise HTTPException(status_code=404, detail="No active game ")