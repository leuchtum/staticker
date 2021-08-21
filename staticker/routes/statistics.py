@app.get("/statistics-overview", response_class=HTMLResponse)
async def app_statistics_overview(request: Request):
    dic = {"request": request}
    return templates.TemplateResponse("statistics.html", dic)