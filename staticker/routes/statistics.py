from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse

from ..dependencies import templates

from ..statistics import GlobalStatistics, EventStatistics
from ..collections import PlayerCollection, EventCollection
from ..core import get_player_by_id, get_event_by_id

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/", response_class=HTMLResponse)
async def stats_overview(request: Request):
    dic = {"request": request}
    return templates.TemplateResponse("stats-overview.html", dic)


@router.get("/global", response_class=HTMLResponse)
async def stats_global(request: Request):
    gs = GlobalStatistics()

    dic = {"request": request, "stats": gs.get_formatted_stats()}
    return templates.TemplateResponse("stats-global.html", dic)


@router.get("/player", response_class=HTMLResponse)
async def stats_player_overview(request: Request):
    pc = PlayerCollection()
    pc.load_all()
    dic = {"request": request, "players": pc.player}
    return templates.TemplateResponse("stats-player-overview.html", dic)


@router.get("/player/{player_id}", response_class=HTMLResponse)
async def stats_player(request: Request, player_id: int):
    player = get_player_by_id(player_id)
    dic = {"request": request, "player": player}
    return templates.TemplateResponse("stats-player.html", dic)


@router.get("/event", response_class=HTMLResponse)
async def stats_event_overview(request: Request):
    ec = EventCollection()
    ec.load_all()
    dic = {"request": request, "events": ec.get_events()}
    return templates.TemplateResponse("stats-event-overview.html", dic)


@router.get("/event/{event_id}", response_class=HTMLResponse)
async def stats_event(request: Request, event_id: int):
    ev = get_event_by_id(event_id)
    ev_stat = EventStatistics(ev)
    dic = {"request": request, "stats": ev_stat.get_formatted_stats(), "event": ev}
    return templates.TemplateResponse("stats-event.html", dic)
