from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import dashboard, ranking, watchlist, alerts
from app.tasks.scheduler import build_scheduler

app = FastAPI(title='TW Stock Insight Bot', version='0.2.0')
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

app.include_router(dashboard.router)
app.include_router(ranking.router)
app.include_router(watchlist.router)
app.include_router(alerts.router)

scheduler = build_scheduler()

@app.on_event('startup')
def startup_event() -> None:
    if scheduler and not scheduler.running:
        scheduler.start()

@app.on_event('shutdown')
def shutdown_event() -> None:
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
