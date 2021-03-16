from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import starlette.status as status
from staticker.context import Context

templates = Jinja2Templates(directory="staticker/templates")
context = Context()

async def not_found(request, exc):
    with open("staticker/templates/404.html") as f:
        content = f.read()
        return HTMLResponse(content, status_code=exc.status_code)

exceptions = {
    404: not_found
}

app = FastAPI(exception_handlers=exceptions)
app.mount("/static", StaticFiles(directory="staticker/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "context": context})

@app.get("/about", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/session/{session_id}", response_class=HTMLResponse)
async def read_item(request: Request, session_id: str):
    return templates.TemplateResponse("session.html", {"request": request, "session_id": session_id})

@app.get("/game/{game_id}", response_class=HTMLResponse)
async def read_item(request: Request, game_id: str):
    game = Game()
    game.game_id = game_id
    return templates.TemplateResponse("game.html", {"request": request, "game": game})

@app.get("/player/{player_id}", response_class=HTMLResponse)
async def read_item(request: Request, player_id: str, alert: bool = False):
    p = context.get_player(player_id)
    if p:
        return templates.TemplateResponse("player.html", {"request": request, "player": p, "alert": alert})
    else:
        raise HTTPException(status_code=404, detail="Player not found")

@app.get("/sessions-overview", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("sessions-overview.html", {"request": request})

@app.get("/player-overview", response_class=HTMLResponse)
async def read_item(request: Request):
    ps = context.get_players(all=True)
    return templates.TemplateResponse("player-overview.html", {"request": request, "players": ps})

@app.get("/statistics-overview", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("statistics.html", {"request": request})

@app.get("/new-player", response_class=HTMLResponse)
async def read_item(request: Request, alert: bool = False):
    return templates.TemplateResponse("new_player.html", {"request": request, "alert": alert})

@app.post("/new-player/submit")
async def asdfasdf(request: Request, name: str = Form(...)):
    if context.name_exists(name):
        return RedirectResponse(url='/new-player?alert=1', status_code=status.HTTP_302_FOUND)
    p = context.new_player(name)
    return RedirectResponse(url='/player/'+p.id+"?alert=1", status_code=status.HTTP_302_FOUND)

#BUG rename functions