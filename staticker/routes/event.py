from fastapi import Request, HTTPException, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
import starlette.status as status
import json


from ..statistics import EventStatistics
from ..collections import EventCollection
from ..dependencies import manager, templates
from ..core import get_event_by_id, Event, NotAllowedError, get_player_by_name


router = APIRouter(
    prefix="/event",
    tags=["event"]
)


@router.get("/", response_class=HTMLResponse)
async def event_overview(request: Request):
    ec = EventCollection()
    ec.load_all()
    dic = {
        "request": request,
        "events": ec.get_events(),
        "active_event": manager.get_active_event()
    }
    return templates.TemplateResponse("events-overview.html", dic)


@router.get("/id/{event_id}", response_class=HTMLResponse)
async def event(request: Request, event_id: str, created: bool = False):
    try:
        ev = get_event_by_id(event_id)
    except:
        raise HTTPException(status_code=404, detail="Event not found")
    
    ev_stat = EventStatistics(ev)
    main_ranking = ev_stat.get_main_ranking()
    
    dic = {
        "request": request,
        "event": ev,
        "created": created,
        "main_ranking": main_ranking
    }
    return templates.TemplateResponse("event.html", dic)


@router.post("/id/{event_id}/deactivate")
async def deactivate(request: Request, event_id: str):
    try:
        ev = get_event_by_id(event_id)
        ev.deactivate()
    except:
        raise HTTPException(status_code=404, detail="Event not found")

    return RedirectResponse(f"/event/id/{event_id}", status_code=status.HTTP_302_FOUND)


@router.get("/active", response_class=HTMLResponse)
async def active_event():
    active_event = manager.get_active_event()
    if active_event:
        url = f"id/{active_event.id}"
        return RedirectResponse(url, status_code=status.HTTP_302_FOUND)
    else:
        raise HTTPException(status_code=404, detail="No active event")


@router.get("/new", response_class=HTMLResponse)
async def new_event(request: Request, min_player_violation: bool = False, err: bool = False):
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

@router.post("/new/submit")
async def new_event_submit(selected_players: str = Form(...)):
    selected_players = json.loads(selected_players)

    if len(selected_players) < 2:
        url = '/event/new?min_player_violation=true'
    else:
        ev = Event(mode="TEST")
        try:
            ev.activate()
            player = [get_player_by_name(name)
                      for name in selected_players]
            ev.add_player(player)
            ev.save()
        except NotAllowedError:
            url = '/event/new?err=true'
        else:
            url = f"/event/id/{ev.id}?created=1"

    return RedirectResponse(url, status_code=status.HTTP_302_FOUND)