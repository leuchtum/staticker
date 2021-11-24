from fastapi import Request, HTTPException, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
import starlette.status as status
import peewee

from ..collections import PlayerCollection
from ..dependencies import templates, manager
from ..core import NotFoundError, get_player_by_id, Player


router = APIRouter(prefix="/player", tags=["player"])


@router.get("/", response_class=HTMLResponse)
async def player_overview(request: Request):
    pc = PlayerCollection()
    pc.load_all(sort_by="name")
    p = pc.get_player()
    dic = {"request": request, "players": p}
    return templates.TemplateResponse("player-overview.html", dic)


@router.get("/id/{player_id}", response_class=HTMLResponse)
async def player(request: Request, player_id: str, created: bool = False):
    try:
        p = get_player_by_id(player_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Player not found")
    dic = {"request": request, "player": p, "created": created}
    return templates.TemplateResponse("player.html", dic)


@router.get("/new", response_class=HTMLResponse)
async def new_player(request: Request, exists: bool = False, errchars: bool = False):
    dic = {"request": request, "exists": exists, "errchars": errchars}
    return templates.TemplateResponse("new_player.html", dic)


@router.post("/new/submit")
async def new_player_submit(_: Request, name: str = Form(...)):
    allowed_chars = set(
        "0123456789abcdefghijklmnopqrstuvwxyzäöüABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ_-"
    )
    code = status.HTTP_302_FOUND
    if set(name).issubset(allowed_chars):
        p = Player(name=name)
    else:
        return RedirectResponse(url="/player/new?errchars=1", status_code=code)
    try:
        p.save()
    except peewee.IntegrityError:
        return RedirectResponse(url="/player/new?exists=1", status_code=code)
    return RedirectResponse(url=f"/player/id/{p.id}?created=1", status_code=code)
